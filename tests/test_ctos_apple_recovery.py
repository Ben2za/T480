from __future__ import annotations

import argparse
import contextlib
import errno
import hashlib
import importlib.machinery
import importlib.util
import io
import json
import os
import stat
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts/ctos-apple-recovery"
LOADER = importlib.machinery.SourceFileLoader("ctos_apple_recovery", str(SCRIPT_PATH))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
assert SPEC is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[LOADER.name] = MODULE
LOADER.exec_module(MODULE)


class XmlProfileTests(unittest.TestCase):
    def profile(self, name: str) -> ET.Element:
        return ET.fromstring(MODULE.PROFILE_PATHS[name].read_text(encoding="utf-8"))

    def test_both_profiles_match_declared_invariants(self) -> None:
        for profile, path in MODULE.PROFILE_PATHS.items():
            with self.subTest(profile=profile):
                signature = MODULE.xml_signature(self.profile(profile))
                expected = MODULE.expected_signature(profile)
                for key, value in expected.items():
                    self.assertEqual(signature[key], value, f"{path}: {key}")

    def test_operational_xml_mutations_are_not_signature_equivalent(self) -> None:
        root = self.profile("install")
        root.find("./devices/disk/driver").set("cache", "unsafe")
        interface = root.find("./devices/interface")
        ET.SubElement(interface, "link", {"state": "down"})
        root.find("./devices/graphics").set("passwd", "known-secret")
        ET.SubElement(root.find("./cpu"), "feature", {"policy": "disable", "name": "aes"})
        signature = MODULE.xml_signature(root)
        errors = MODULE.signature_errors(
            signature,
            MODULE.expected_signature("install"),
        )
        self.assertTrue(any("disk_entries" in error for error in errors), errors)
        self.assertTrue(any("interfaces" in error for error in errors), errors)
        self.assertTrue(any("graphics_unexpected_attributes" in error for error in errors), errors)
        self.assertTrue(any("cpu_child_tags" in error for error in errors), errors)

    def test_fixed_machine_uuid_and_resources(self) -> None:
        for profile in MODULE.PROFILE_PATHS:
            root = self.profile(profile)
            self.assertEqual(root.findtext("uuid"), "fae71b6a-3d2e-498f-b1b6-a0f7a5672721")
            self.assertEqual(root.find("./os/type").attrib["machine"], "pc-q35-11.0")
            self.assertEqual(root.findtext("memory"), "8192")
            self.assertEqual(root.find("memory").attrib["unit"], "MiB")
            self.assertEqual(root.findtext("vcpu"), "4")

    def test_secure_boot_nvram_and_private_tpm_are_explicit(self) -> None:
        for profile in MODULE.PROFILE_PATHS:
            root = self.profile(profile)
            loader = root.find("./os/loader")
            self.assertIsNotNone(loader)
            self.assertEqual(loader.attrib["secure"], "yes")
            self.assertEqual(loader.attrib["readonly"], "yes")
            self.assertEqual(loader.attrib["type"], "pflash")
            self.assertEqual(loader.text.strip(), str(MODULE.OVMF_CODE_PATH))
            self.assertEqual(root.findtext("./os/nvram").strip(), str(MODULE.NVRAM_PATH))
            self.assertEqual(root.find("./features/smm").attrib["state"], "on")
            backend = root.find("./devices/tpm/backend")
            source = root.find("./devices/tpm/backend/source")
            self.assertEqual(root.find("./devices/tpm").attrib["model"], "tpm-crb")
            self.assertEqual(backend.attrib["type"], "emulator")
            self.assertEqual(backend.attrib["version"], "2.0")
            self.assertEqual(backend.attrib["persistent_state"], "yes")
            self.assertEqual(source.attrib, {"type": "dir", "path": str(MODULE.TPM_STATE_PATH)})

    def test_only_windows_inbox_storage_and_network_devices(self) -> None:
        for profile in MODULE.PROFILE_PATHS:
            root = self.profile(profile)
            target = root.find("./devices/disk[@device='disk']/target")
            self.assertEqual(target.attrib, {"dev": "sda", "bus": "sata"})
            self.assertEqual(root.find("./devices/interface/model").attrib["type"], "e1000e")
            self.assertEqual(root.find("./devices/memballoon").attrib["model"], "none")
            serialized = ET.tostring(root, encoding="unicode").lower()
            self.assertNotIn("virtio", serialized)
            self.assertEqual(root.findall("./devices/channel"), [])

    def test_install_media_and_reboot_policy(self) -> None:
        install = self.profile("install")
        maintenance = self.profile("maintenance")
        install_cdroms = install.findall("./devices/disk[@device='cdrom']")
        self.assertEqual(len(install_cdroms), 1)
        self.assertEqual(
            install_cdroms[0].find("source").attrib["file"],
            "/var/lib/libvirt/ctos/iso/Win11_25H2_English_x64_v2.iso",
        )
        self.assertEqual(install.findtext("on_reboot"), "restart")
        self.assertEqual(maintenance.findall("./devices/disk[@device='cdrom']"), [])

    def test_local_spice_has_no_data_exchange_or_usb_redirection(self) -> None:
        forbidden = ("hostdev", "redirdev", "filesystem", "sound", "audio", "smartcard")
        for profile in MODULE.PROFILE_PATHS:
            root = self.profile(profile)
            graphics = root.find("./devices/graphics")
            self.assertEqual(graphics.attrib["type"], "spice")
            self.assertEqual(graphics.find("listen").attrib["type"], "none")
            self.assertEqual(graphics.find("clipboard").attrib["copypaste"], "no")
            self.assertEqual(graphics.find("filetransfer").attrib["enable"], "no")
            for tag in forbidden:
                self.assertEqual(root.findall(f"./devices/{tag}"), [], f"{profile}: {tag}")

    def test_exact_device_allowlist_rejects_security_relevant_drift(self) -> None:
        def emulator_drift(root: ET.Element) -> None:
            root.find("./devices/emulator").text = "/tmp/untrusted-qemu"

        def serial_drift(root: ET.Element) -> None:
            root.find("./devices/serial").attrib["type"] = "file"

        def console_drift(root: ET.Element) -> None:
            root.find("./devices/console/target").attrib["port"] = "1"

        def video_drift(root: ET.Element) -> None:
            root.find("./devices/video/model").attrib["type"] = "qxl"

        def pcr_drift(root: ET.Element) -> None:
            root.find("./devices/tpm/backend/active_pcr_banks/sha256").tag = "sha1"

        def graphics_drift(root: ET.Element) -> None:
            root.find("./devices/graphics/image").attrib["compression"] = "auto_glz"

        def serial_log_injection(root: ET.Element) -> None:
            ET.SubElement(
                root.find("./devices/serial"),
                "log",
                {"file": "/tmp/guest-serial.log", "append": "on"},
            )

        def graphics_gl_injection(root: ET.Element) -> None:
            ET.SubElement(
                root.find("./devices/graphics"),
                "gl",
                {"enable": "yes", "rendernode": "/dev/dri/renderD128"},
            )

        def interface_rom_injection(root: ET.Element) -> None:
            ET.SubElement(
                root.find("./devices/interface"),
                "rom",
                {"file": "/tmp/untrusted.rom"},
            )

        def video_acceleration_injection(root: ET.Element) -> None:
            ET.SubElement(
                root.find("./devices/video/model"),
                "acceleration",
                {"accel3d": "yes"},
            )

        def tpm_encryption_injection(root: ET.Element) -> None:
            ET.SubElement(
                root.find("./devices/tpm/backend"),
                "encryption",
                {"secret": "00000000-0000-0000-0000-000000000000"},
            )

        mutations = {
            "emulator": emulator_drift,
            "serial": serial_drift,
            "console": console_drift,
            "video": video_drift,
            "PCR bank": pcr_drift,
            "graphics image": graphics_drift,
            "serial host log": serial_log_injection,
            "graphics rendernode": graphics_gl_injection,
            "interface ROM": interface_rom_injection,
            "video nested acceleration": video_acceleration_injection,
            "TPM nested encryption": tpm_encryption_injection,
        }
        expected = MODULE.expected_signature("maintenance")
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                root = self.profile("maintenance")
                mutate(root)
                errors = MODULE.signature_errors(MODULE.xml_signature(root), expected)
                self.assertTrue(errors, f"{label} drift was not detected")

    @unittest.skipUnless(MODULE.shutil.which("virt-xml-validate"), "virt-xml-validate unavailable")
    def test_libvirt_schema_validation(self) -> None:
        state = MODULE.repo_validation_state()
        self.assertTrue(state["ok"], state)


class HelperUnitTests(unittest.TestCase):
    def media_identities(self) -> dict[str, object]:
        return {
            "ok": True,
            "root_uid": os.getuid(),
            "qemu_uid": os.getuid(),
            "libvirt_gid": os.getgid(),
            "errors": [],
        }

    def test_publish_json_no_replace_creates_complete_single_link(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "state.json"
            payload = {"schema": "test.v1", "value": 7}
            MODULE.publish_json_no_replace(
                target,
                payload,
                uid=os.getuid(),
                gid=os.getgid(),
                mode=0o640,
            )
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), payload)
            metadata = target.lstat()
            self.assertTrue(stat.S_ISREG(metadata.st_mode))
            self.assertEqual(metadata.st_nlink, 1)
            self.assertEqual(stat.S_IMODE(metadata.st_mode), 0o640)
            self.assertEqual([entry.name for entry in target.parent.iterdir()], ["state.json"])

    def test_publish_json_no_replace_never_overwrites_existing_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "state.json"
            target.write_bytes(b"original\n")
            before = target.lstat()
            with self.assertRaises(FileExistsError):
                MODULE.publish_json_no_replace(
                    target,
                    {"replacement": True},
                    uid=os.getuid(),
                    gid=os.getgid(),
                    mode=0o640,
                )
            after = target.lstat()
            self.assertEqual(target.read_bytes(), b"original\n")
            self.assertEqual((after.st_dev, after.st_ino), (before.st_dev, before.st_ino))
            self.assertEqual([entry.name for entry in target.parent.iterdir()], ["state.json"])

    def test_publish_failure_before_link_leaves_no_named_staging(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "state.json"
            with mock.patch.object(
                MODULE,
                "_link_tmpfile_no_replace",
                side_effect=OSError(errno.EIO, "injected pre-link fault"),
            ):
                with self.assertRaises(OSError):
                    MODULE.publish_json_no_replace(
                        target,
                        {"value": 1},
                        uid=os.getuid(),
                        gid=os.getgid(),
                        mode=0o640,
                    )
            self.assertFalse(target.exists())
            self.assertEqual(list(target.parent.iterdir()), [])

    def test_directory_fsync_failure_leaves_recoverable_complete_target(self) -> None:
        real_fsync = os.fsync

        def fail_directory_sync(descriptor: int) -> None:
            if stat.S_ISDIR(os.fstat(descriptor).st_mode):
                raise OSError(errno.EIO, "injected directory fsync fault")
            real_fsync(descriptor)

        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "state.json"
            payload = {"value": 1}
            with mock.patch.object(MODULE.os, "fsync", side_effect=fail_directory_sync):
                with self.assertRaises(OSError):
                    MODULE.publish_json_no_replace(
                        target,
                        payload,
                        uid=os.getuid(),
                        gid=os.getgid(),
                        mode=0o640,
                    )
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), payload)
            self.assertEqual(target.lstat().st_nlink, 1)
            with self.assertRaises(FileExistsError):
                MODULE.publish_json_no_replace(
                    target,
                    payload,
                    uid=os.getuid(),
                    gid=os.getgid(),
                    mode=0o640,
                )

    def test_volume_creation_xml_declares_exact_private_permissions(self) -> None:
        identities = self.media_identities()
        captured: dict[str, object] = {}

        def fake_virsh(arguments, readonly=False, timeout=20.0):
            del readonly, timeout
            self.assertEqual(arguments[0:2], ["vol-create", MODULE.VOLUME_POOL])
            self.assertEqual(arguments[-1], "--validate")
            root = ET.fromstring(Path(arguments[2]).read_text(encoding="utf-8"))
            captured["capacity"] = root.findtext("capacity")
            captured["owner"] = root.findtext("./target/permissions/owner")
            captured["group"] = root.findtext("./target/permissions/group")
            captured["mode"] = root.findtext("./target/permissions/mode")
            return MODULE.CommandResult(0, "created", "")

        with mock.patch.object(MODULE, "virsh", side_effect=fake_virsh):
            result = MODULE.create_managed_windows_volume(identities)
        self.assertEqual(result.rc, 0)
        self.assertEqual(captured["capacity"], str(MODULE.VOLUME_SIZE_BYTES))
        self.assertEqual(captured["owner"], str(os.getuid()))
        self.assertEqual(captured["group"], str(os.getgid()))
        self.assertEqual(captured["mode"], "0640")

    def test_blank_preinstall_disk_rejects_any_mapped_guest_data(self) -> None:
        info = json.dumps(
            [
                {
                    "format": "qcow2",
                    "virtual-size": MODULE.VOLUME_SIZE_BYTES,
                    "dirty-flag": False,
                    "format-specific": {"data": {"corrupt": False}},
                }
            ]
        )
        check = json.dumps({"check-errors": 0, "corruptions": 0, "leaks": 0})
        mapping = json.dumps(
            [
                {
                    "start": 0,
                    "length": MODULE.VOLUME_SIZE_BYTES,
                    "data": True,
                    "zero": False,
                }
            ]
        )
        with tempfile.TemporaryDirectory() as directory:
            disk = Path(directory) / "disk.qcow2"
            disk.write_bytes(b"qcow2")
            os.chmod(disk, MODULE.DISK_MODE)
            with mock.patch.object(MODULE, "DISK_PATH", disk), mock.patch.object(
                MODULE, "volume_state", return_value={"compatible": True}
            ), mock.patch.object(
                MODULE.shutil, "which", return_value="/usr/bin/qemu-img"
            ), mock.patch.object(
                MODULE,
                "run",
                side_effect=[
                    MODULE.CommandResult(0, info, ""),
                    MODULE.CommandResult(0, check, ""),
                    MODULE.CommandResult(0, mapping, ""),
                ],
            ):
                state = MODULE.blank_preinstall_disk_state()
        self.assertFalse(state["ok"], state)
        self.assertTrue(any("unallocated zero" in error for error in state["errors"]), state)

    def write_media_attestation(self, path: Path, target: Path, size: int, digest: str) -> None:
        path.write_text(
            json.dumps(
                {
                    "schema": MODULE.MEDIA_ATTESTATION_SCHEMA,
                    "pool": MODULE.ISO_POOL,
                    "filename": MODULE.WINDOWS_ISO_NAME,
                    "managed_path": str(target),
                    "release": MODULE.WINDOWS_RELEASE,
                    "language": MODULE.WINDOWS_LANGUAGE,
                    "size": size,
                    "sha256": digest,
                    "hash_source": MODULE.WINDOWS_HASH_SOURCE,
                    "entitlement_status": MODULE.ELIGIBLE_DURABLE_ENTITLEMENT,
                    "imported_utc": "2026-07-17T12:00:00+00:00",
                }
            ),
            encoding="utf-8",
        )
        os.chmod(path, MODULE.MEDIA_ATTESTATION_MODE)

    def run_payload(self) -> dict[str, object]:
        return {
            "schema": MODULE.RUN_ATTESTATION_SCHEMA,
            "run_id": "11111111-1111-4111-8111-111111111111",
            "domain": MODULE.DOMAIN,
            "domain_uuid": MODULE.DOMAIN_UUID,
            "profile": "install",
            "prepared_utc": "2026-07-17T11:00:00+00:00",
            "challenge": "a" * 64,
            "host_boot_id": "22222222-2222-4222-8222-222222222222",
            "workflow_sha256": "b" * 64,
            "hardware_sha256": MODULE.canonical_json_sha256(MODULE.expected_signature("install")),
            "entitlement_status": MODULE.ELIGIBLE_DURABLE_ENTITLEMENT,
            "media_sha256": MODULE.WINDOWS_SHA256,
            "windows_release": MODULE.WINDOWS_RELEASE,
            "preinstall_attestation_sha256": "c" * 64,
            "preinstall_disk_attestation_sha256": "6" * 64,
        }

    def guest_evidence_payload(self, phase: str = "windows-installed") -> dict[str, object]:
        run = self.run_payload()
        if phase == "windows-installed":
            apple = {
                "installed": False,
                "product_id": "",
                "package_family": "",
                "publisher": "",
                "status": "",
                "opened_without_phone": False,
            }
        else:
            apple = {
                "installed": True,
                "product_id": "9NP83LWLPZ9K",
                "package_family": "AppleInc.AppleDevices_nzyj5cx40ttqa",
                "publisher": "Apple Inc.",
                "status": "OK",
                "opened_without_phone": True,
            }
        return {
            "schema": MODULE.GUEST_EVIDENCE_SCHEMA,
            "evidence_id": "33333333-3333-4333-8333-333333333333",
            "run_id": run["run_id"],
            "challenge": run["challenge"],
            "host_boot_id": run["host_boot_id"],
            "workflow_sha256": run["workflow_sha256"],
            "phase": phase,
            "captured_utc": "2026-07-17T12:00:00+00:00",
            "collection": "operator-reviewed-console",
            "system": {"installation_complete": True, "clock_synchronized": True},
            "network": {"ctos_nat_egress": True},
            "windows": {
                "product_name": "Windows 11 Pro",
                "display_version": MODULE.WINDOWS_RELEASE,
                "build": "26200",
                "activation": "Licensed",
                "evaluation": False,
                "pending_reboot": False,
                "pending_updates": False,
            },
            "security": {
                "secure_boot": True,
                "tpm_present": True,
                "tpm_ready": True,
                "tpm_spec": "2.0",
                "defender_enabled": True,
                "real_time_protection": True,
                "firewall_profiles_enabled": ["Domain", "Private", "Public"],
            },
            "storage": {"bitlocker_encrypted": False, "bitlocker_protection": False},
            "power": {"hibernate_enabled": False, "ac_sleep_timeout_minutes": 0},
            "devices": {"problem_count": 0},
            "privacy": {
                "personal_microsoft_account": False,
                "apple_account": False,
                "phone_ever_attached": False,
            },
            "apple_devices": apple,
        }

    def maintenance_payload(self) -> dict[str, object]:
        return {
            "schema": MODULE.MAINTENANCE_STATE_SCHEMA,
            "generation": "44444444-4444-4444-8444-444444444444",
            "phase": "windows-installed",
            "created_utc": "2025-01-01T12:00:00+00:00",
            "domain": {
                "name": MODULE.DOMAIN,
                "uuid": MODULE.DOMAIN_UUID,
                "profile": "maintenance",
                "hardware_sha256": MODULE.canonical_json_sha256(
                    MODULE.expected_signature("maintenance")
                ),
            },
            "run": {
                "id": self.run_payload()["run_id"],
                "attestation_sha256": "d" * 64,
            },
            "disk": {
                "path": str(MODULE.DISK_PATH),
                "format": "qcow2",
                "virtual_size": MODULE.VOLUME_SIZE_BYTES,
                "sha256": "e" * 64,
                "qemu_check": "clean",
            },
            "nvram": {
                "path": str(MODULE.NVRAM_PATH.relative_to(MODULE.STATE_ROOT)),
                "sha256": "f" * 64,
                "secure_boot": True,
            },
            "tpm": {
                "path": str(MODULE.TPM_STATE_PATH.relative_to(MODULE.STATE_ROOT)),
                "tree_sha256": "1" * 64,
                "file_count": 1,
            },
            "evidence": {
                "id": self.guest_evidence_payload()["evidence_id"],
                "sha256": "2" * 64,
            },
            "shutdown": {
                "mode": "acpi-observed",
                "receipt_sha256": "3" * 64,
                "artifact_stat_sha256": "4" * 64,
            },
            "provenance": {
                "preinstall_sha256": "5" * 64,
                "entitlement_status": MODULE.ELIGIBLE_DURABLE_ENTITLEMENT,
                "workflow_sha256": self.run_payload()["workflow_sha256"],
            },
        }

    def test_parser_exposes_required_commands_and_post_command_json(self) -> None:
        parser = MODULE.build_parser()
        expected = {
            "status",
            "plan",
            "apply-infra",
            "prepare-secure-state",
            "verify-media",
            "import-media",
            "ingest-evidence",
            "transition-maintenance",
            "define",
            "start-maintenance",
            "seal-baseline",
            "start-session",
            "usb-preflight",
            "open-console",
            "shutdown",
            "close-session",
        }
        choices = next(action for action in parser._actions if action.dest == "command").choices
        self.assertEqual(set(choices), expected)
        self.assertTrue(parser.parse_args(["status", "--json"]).json)
        self.assertTrue(parser.parse_args(["--json", "status"]).json)

    def test_verify_media_accepts_only_fixed_managed_path_and_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "Win11_25H2_English_x64_v2.iso"
            attestation = root / "media.json"
            payload = b"test Microsoft media payload"
            path.write_bytes(payload)
            os.chmod(path, MODULE.MEDIA_MODE)
            digest = hashlib.sha256(payload).hexdigest()
            self.write_media_attestation(attestation, path, len(payload), digest)
            with mock.patch.object(MODULE, "WINDOWS_ISO_PATH", path), mock.patch.object(
                MODULE, "WINDOWS_SHA256", digest
            ), mock.patch.object(
                MODULE, "MEDIA_ATTESTATION_PATH", attestation
            ), mock.patch.object(
                MODULE, "media_identities", return_value=self.media_identities()
            ):
                state = MODULE.media_state(verify_hash=True)
            self.assertTrue(state["ok"], state)
            self.assertTrue(state["verified"])
            self.assertEqual(state["actual_sha256"], digest)

    def test_verify_media_rejects_hash_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "Win11_25H2_English_x64_v2.iso"
            attestation = root / "media.json"
            path.write_bytes(b"wrong")
            os.chmod(path, MODULE.MEDIA_MODE)
            self.write_media_attestation(attestation, path, 5, "0" * 64)
            with mock.patch.object(MODULE, "WINDOWS_ISO_PATH", path), mock.patch.object(
                MODULE, "WINDOWS_SHA256", "0" * 64
            ), mock.patch.object(
                MODULE, "MEDIA_ATTESTATION_PATH", attestation
            ), mock.patch.object(
                MODULE, "media_identities", return_value=self.media_identities()
            ):
                state = MODULE.media_state(verify_hash=True)
            self.assertFalse(state["ok"])
            self.assertTrue(any("mismatch" in error for error in state["errors"]), state)

    def test_import_media_requires_root_before_preflight_or_source_access(self) -> None:
        args = argparse.Namespace(json=True, source="/does/not/exist")
        with mock.patch.object(MODULE.os, "geteuid", return_value=1000), mock.patch.object(
            MODULE, "mutation_preflight"
        ) as preflight:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                rc = MODULE.command_import_media(args)
        self.assertEqual(rc, 1)
        self.assertFalse(json.loads(output.getvalue())["ok"])
        preflight.assert_not_called()

    def test_import_media_entitlement_gate_precedes_source_access(self) -> None:
        args = argparse.Namespace(json=True, source="/does/not/exist")
        preflight_state = {
            "ok": False,
            "errors": ["durable Windows VM entitlement is not recorded"],
        }
        with mock.patch.object(MODULE.os, "geteuid", return_value=0), mock.patch.object(
            MODULE, "mutation_preflight", return_value=preflight_state
        ), mock.patch.object(MODULE, "media_identities") as identities:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                rc = MODULE.command_import_media(args)
        self.assertEqual(rc, 1)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["error"], "media import blocked before source access")
        identities.assert_not_called()

    def test_import_media_is_atomic_attested_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            downloads = root / "downloads"
            iso_dir = root / "iso"
            snapshots = root / "snapshots"
            downloads.mkdir()
            iso_dir.mkdir()
            snapshots.mkdir()
            source = downloads / MODULE.WINDOWS_ISO_NAME
            target = iso_dir / MODULE.WINDOWS_ISO_NAME
            attestation = snapshots / "media.json"
            content = b"authenticated Microsoft ISO test fixture"
            digest = hashlib.sha256(content).hexdigest()
            source.write_bytes(content)
            os.chmod(source, 0o600)
            identities = self.media_identities()

            def fake_virsh(arguments, readonly=False, timeout=20.0):
                del timeout
                if arguments == ["pool-refresh", MODULE.ISO_POOL] and not readonly:
                    return MODULE.CommandResult(0, "refreshed", "")
                if arguments == [
                    "vol-path",
                    "--pool",
                    MODULE.ISO_POOL,
                    MODULE.WINDOWS_ISO_NAME,
                ] and readonly:
                    return MODULE.CommandResult(0, str(target), "")
                raise AssertionError((arguments, readonly))

            patches = (
                mock.patch.object(MODULE, "WINDOWS_ISO_PATH", target),
                mock.patch.object(MODULE, "MEDIA_ATTESTATION_PATH", attestation),
                mock.patch.object(MODULE, "WINDOWS_SHA256", digest),
            )
            args = argparse.Namespace(json=True, source=str(source))
            with patches[0], patches[1], patches[2], mock.patch.object(
                MODULE.os, "geteuid", return_value=0
            ), mock.patch.object(
                MODULE, "mutation_preflight", return_value={"ok": True, "errors": []}
            ), mock.patch.object(
                MODULE, "media_identities", return_value=identities
            ), mock.patch.object(
                MODULE, "virsh", side_effect=fake_virsh
            ):
                first_output = io.StringIO()
                with contextlib.redirect_stdout(first_output):
                    first_rc = MODULE.command_import_media(args)
                source.unlink()
                second_output = io.StringIO()
                with contextlib.redirect_stdout(second_output):
                    second_rc = MODULE.command_import_media(args)

            first = json.loads(first_output.getvalue())
            second = json.loads(second_output.getvalue())
            self.assertEqual(first_rc, 0, first)
            self.assertTrue(first["changed"])
            self.assertEqual(second_rc, 0, second)
            self.assertFalse(second["changed"])
            self.assertEqual(target.read_bytes(), content)
            self.assertEqual(stat.S_IMODE(target.stat().st_mode), MODULE.MEDIA_MODE)
            self.assertEqual(target.stat().st_nlink, 1)
            self.assertEqual(attestation.stat().st_nlink, 1)
            self.assertEqual(json.loads(attestation.read_text())["sha256"], digest)

    def test_import_media_never_overwrites_conflicting_managed_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            iso_dir = root / "iso"
            snapshots = root / "snapshots"
            iso_dir.mkdir()
            snapshots.mkdir()
            target = iso_dir / MODULE.WINDOWS_ISO_NAME
            target.write_bytes(b"conflict")
            os.chmod(target, MODULE.MEDIA_MODE)
            attestation = snapshots / "media.json"
            args = argparse.Namespace(json=True, source="/source/must/not/be/read")
            with mock.patch.object(MODULE, "WINDOWS_ISO_PATH", target), mock.patch.object(
                MODULE, "MEDIA_ATTESTATION_PATH", attestation
            ), mock.patch.object(
                MODULE, "WINDOWS_SHA256", "0" * 64
            ), mock.patch.object(
                MODULE.os, "geteuid", return_value=0
            ), mock.patch.object(
                MODULE, "mutation_preflight", return_value={"ok": True, "errors": []}
            ), mock.patch.object(
                MODULE, "media_identities", return_value=self.media_identities()
            ), mock.patch.object(MODULE, "virsh") as virsh_mock:
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    rc = MODULE.command_import_media(args)
            self.assertEqual(rc, 1)
            self.assertEqual(target.read_bytes(), b"conflict")
            self.assertFalse(attestation.exists())
            virsh_mock.assert_not_called()

    def test_guest_evidence_schema_is_strict_run_bound_and_type_safe(self) -> None:
        run = self.run_payload()
        evidence = self.guest_evidence_payload()
        now = MODULE.dt.datetime.fromisoformat("2026-07-17T13:00:00+00:00")

        errors = MODULE.validate_guest_evidence(
            evidence,
            expected_phase="windows-installed",
            expected_run_id=str(run["run_id"]),
            expected_challenge=str(run["challenge"]),
            expected_host_boot_id=str(run["host_boot_id"]),
            expected_workflow_sha256=str(run["workflow_sha256"]),
            run_prepared_utc=str(run["prepared_utc"]),
            now=now,
        )
        self.assertEqual(errors, [])

        evidence["challenge"] = "d" * 64
        errors = MODULE.validate_guest_evidence(
            evidence,
            expected_phase="windows-installed",
            expected_run_id=str(run["run_id"]),
            expected_challenge=str(run["challenge"]),
            expected_host_boot_id=str(run["host_boot_id"]),
            expected_workflow_sha256=str(run["workflow_sha256"]),
            run_prepared_utc=str(run["prepared_utc"]),
            now=now,
        )
        self.assertTrue(any("challenge" in error for error in errors), errors)

        evidence = self.guest_evidence_payload()
        evidence["windows"]["product_name"] = ["Windows 11 Pro"]
        errors = MODULE.validate_guest_evidence(
            evidence,
            expected_phase="windows-installed",
            expected_run_id=str(run["run_id"]),
            expected_challenge=str(run["challenge"]),
            expected_host_boot_id=str(run["host_boot_id"]),
            expected_workflow_sha256=str(run["workflow_sha256"]),
            run_prepared_utc=str(run["prepared_utc"]),
            now=now,
        )
        self.assertTrue(any("product_name" in error for error in errors), errors)

    def test_guest_evidence_rejects_unknown_keys_and_predating_run(self) -> None:
        run = self.run_payload()
        now = MODULE.dt.datetime.fromisoformat("2026-07-17T13:00:00+00:00")
        evidence = self.guest_evidence_payload()
        evidence["unexpected"] = True
        errors = MODULE.validate_guest_evidence(
            evidence,
            expected_phase="windows-installed",
            expected_run_id=str(run["run_id"]),
            expected_challenge=str(run["challenge"]),
            expected_host_boot_id=str(run["host_boot_id"]),
            expected_workflow_sha256=str(run["workflow_sha256"]),
            run_prepared_utc=str(run["prepared_utc"]),
            now=now,
        )
        self.assertTrue(any("unexpected" in error for error in errors), errors)

        evidence = self.guest_evidence_payload()
        evidence["captured_utc"] = "2026-07-17T10:00:00+00:00"
        errors = MODULE.validate_guest_evidence(
            evidence,
            expected_phase="windows-installed",
            expected_run_id=str(run["run_id"]),
            expected_challenge=str(run["challenge"]),
            expected_host_boot_id=str(run["host_boot_id"]),
            expected_workflow_sha256=str(run["workflow_sha256"]),
            run_prepared_utc=str(run["prepared_utc"]),
            now=now,
        )
        self.assertTrue(any("predates" in error for error in errors), errors)

    def test_operator_json_reader_rejects_duplicate_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.json"
            path.write_text('{"schema":"one","schema":"two"}', encoding="utf-8")
            os.chmod(path, 0o600)
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                MODULE.read_operator_json_source(path)

    def test_install_run_is_published_before_vm_start(self) -> None:
        args = argparse.Namespace(
            profile="install",
            json=True,
            open_console=False,
            resume=False,
        )
        run_payload = self.run_payload()
        missing_run = {"ok": False, "run_id": "", "payload": {}, "errors": ["missing"]}
        valid_run = {
            "ok": True,
            "run_id": run_payload["run_id"],
            "payload": run_payload,
            "errors": [],
        }
        domain = {
            "compatible": True,
            "profile": "install",
            "info": {"state": "shut off", "managed_save": "no"},
        }
        events: list[str] = []

        def publish(*args, **kwargs):
            del args, kwargs
            events.append("publish")

        def fake_virsh(arguments, readonly=False, timeout=20.0):
            del readonly, timeout
            self.assertEqual(arguments, ["start", MODULE.DOMAIN])
            events.append("start")
            return MODULE.CommandResult(0, "started", "")

        with tempfile.TemporaryDirectory() as directory, mock.patch.object(
            MODULE, "RUN_ATTESTATION_PATH", Path(directory) / "run.json"
        ), mock.patch.object(
            MODULE.os, "geteuid", return_value=0
        ), mock.patch.object(
            MODULE, "mutation_preflight", return_value={"ok": True, "errors": []}
        ), mock.patch.object(
            MODULE, "own_domain_state", return_value=domain
        ), mock.patch.object(
            MODULE, "volume_state", return_value={"compatible": True}
        ), mock.patch.object(
            MODULE, "preinstall_disk_state", return_value={"ok": True, "errors": []}
        ), mock.patch.object(
            MODULE, "run_attestation_state", side_effect=[missing_run, valid_run]
        ), mock.patch.object(
            MODULE, "install_run_payload", return_value=run_payload
        ), mock.patch.object(
            MODULE, "media_identities", return_value=self.media_identities()
        ), mock.patch.object(
            MODULE, "publish_json_no_replace", side_effect=publish
        ), mock.patch.object(
            MODULE, "virsh", side_effect=fake_virsh
        ):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                rc = MODULE.command_start_maintenance(args)
        self.assertEqual(rc, 0, output.getvalue())
        self.assertEqual(events, ["publish", "start"])

    def test_running_install_without_prestart_run_is_refused(self) -> None:
        args = argparse.Namespace(
            profile="install",
            json=True,
            open_console=False,
            resume=False,
        )
        domain = {
            "compatible": True,
            "profile": "install",
            "info": {"state": "running", "managed_save": "no"},
        }
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(
            MODULE, "RUN_ATTESTATION_PATH", Path(directory) / "run.json"
        ), mock.patch.object(
            MODULE.os, "geteuid", return_value=0
        ), mock.patch.object(
            MODULE, "mutation_preflight", return_value={"ok": True, "errors": []}
        ), mock.patch.object(
            MODULE, "own_domain_state", return_value=domain
        ), mock.patch.object(
            MODULE, "volume_state", return_value={"compatible": True}
        ), mock.patch.object(
            MODULE,
            "run_attestation_state",
            return_value={"ok": False, "run_id": "", "payload": {}, "errors": ["missing"]},
        ), mock.patch.object(MODULE, "publish_json_no_replace") as publish, mock.patch.object(
            MODULE, "virsh"
        ) as virsh_mock:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                rc = MODULE.command_start_maintenance(args)
        self.assertEqual(rc, 1)
        publish.assert_not_called()
        virsh_mock.assert_not_called()

    def test_qemu_disk_check_rejects_reported_leaks_even_with_zero_exit(self) -> None:
        info = json.dumps(
            [
                {
                    "format": "qcow2",
                    "virtual-size": MODULE.VOLUME_SIZE_BYTES,
                    "dirty-flag": False,
                    "format-specific": {"data": {"corrupt": False}},
                }
            ]
        )
        check = json.dumps({"check-errors": 0, "corruptions": 0, "leaks": 1})
        with tempfile.TemporaryDirectory() as directory:
            disk = Path(directory) / "disk.qcow2"
            disk.write_bytes(b"qcow2")
            os.chmod(disk, MODULE.DISK_MODE)
            with mock.patch.object(MODULE, "DISK_PATH", disk), mock.patch.object(
                MODULE.shutil, "which", return_value="/usr/bin/qemu-img"
            ), mock.patch.object(
                MODULE, "volume_state", return_value={"compatible": True}
            ), mock.patch.object(
                MODULE, "preinstall_disk_state", return_value={"ok": True, "errors": []}
            ), mock.patch.object(
                MODULE, "media_identities", return_value=self.media_identities()
            ), mock.patch.object(
                MODULE,
                "run",
                side_effect=[
                    MODULE.CommandResult(0, info, ""),
                    MODULE.CommandResult(0, check, ""),
                ],
            ):
                state = MODULE.disk_postinstall_state(hash_disk=True)
        self.assertFalse(state["ok"], state)
        self.assertTrue(any("leaks" in error for error in state["errors"]), state)

    def test_tpm_tree_rejects_symlink_and_accepts_only_nonempty_regular_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "tpm"
            root.mkdir()
            state_file = root / "tpm2-00.permall"
            state_file.write_bytes(b"state")
            os.chmod(root, MODULE.TPM_STATE_MODE)
            os.chmod(state_file, 0o600)
            identities = {
                "ok": True,
                "root_uid": os.getuid(),
                "qemu_uid": os.getuid(),
                "swtpm_uid": os.getuid(),
                "swtpm_gid": os.getgid(),
                "libvirt_gid": os.getgid(),
                "errors": [],
            }
            with mock.patch.object(MODULE, "TPM_STATE_PATH", root), mock.patch.object(
                MODULE, "secure_state_identities", return_value=identities
            ):
                state = MODULE.tpm_tree_state(require_nonempty=True)
            self.assertTrue(state["ok"], state)

            (root / "escape").symlink_to(state_file)
            with mock.patch.object(MODULE, "TPM_STATE_PATH", root), mock.patch.object(
                MODULE, "secure_state_identities", return_value=identities
            ):
                state = MODULE.tpm_tree_state(require_nonempty=True)
            self.assertFalse(state["ok"], state)
            self.assertTrue(any("symlink" in error for error in state["errors"]), state)

    def test_full_state_maintenance_requires_artifacts_intent_and_completion(self) -> None:
        valid_component = {"ok": True, "payload": {}, "errors": []}

        def evaluate(
            *,
            artifacts_ok: bool = True,
            intent_ok: bool = True,
            complete_ok: bool = True,
            incomplete: bool = False,
        ) -> tuple[dict[str, object], mock.Mock]:
            maintenance = {
                "ok": artifacts_ok,
                "payload": {},
                "errors": [] if artifacts_ok else ["artifact mismatch"],
            }
            with mock.patch.object(
                MODULE, "repo_validation_state", return_value={"ok": True}
            ), mock.patch.object(
                MODULE, "host_checks", return_value=[MODULE.Check("host", True, "ok")]
            ), mock.patch.object(
                MODULE, "infra_state", return_value={"ok": True}
            ), mock.patch.object(
                MODULE, "entitlement_state", return_value={"ok": True}
            ), mock.patch.object(
                MODULE, "media_state", return_value={"verified": True}
            ), mock.patch.object(
                MODULE, "volume_state", return_value={"compatible": True}
            ), mock.patch.object(
                MODULE, "preinstall_disk_state", return_value={"ok": True, "errors": []}
            ), mock.patch.object(
                MODULE,
                "own_domain_state",
                return_value={"compatible": True, "profile": "maintenance"},
            ), mock.patch.object(
                MODULE, "maintenance_state", return_value=maintenance
            ) as maintenance_mock, mock.patch.object(
                MODULE, "run_attestation_state", return_value=valid_component
            ), mock.patch.object(
                MODULE,
                "transition_intent_state",
                return_value={**valid_component, "ok": intent_ok},
            ), mock.patch.object(
                MODULE,
                "transition_complete_state",
                return_value={**valid_component, "ok": complete_ok},
            ), mock.patch.object(
                MODULE, "incomplete_transition_exists", return_value=incomplete
            ):
                return MODULE.full_state(), maintenance_mock

        ready, maintenance_mock = evaluate()
        self.assertTrue(ready["ok"], ready)
        maintenance_mock.assert_called_once_with(verify_artifacts=True)

        for label, overrides in (
            ("artifacts", {"artifacts_ok": False}),
            ("intent", {"intent_ok": False}),
            ("completion", {"complete_ok": False}),
            ("incomplete", {"incomplete": True}),
        ):
            with self.subTest(boundary=label):
                state, maintenance_mock = evaluate(**overrides)
                self.assertFalse(state["ok"], state)
                maintenance_mock.assert_called_once_with(verify_artifacts=True)

    def test_new_transition_refuses_maintenance_before_consistency_or_mutation(self) -> None:
        args = argparse.Namespace(
            json=True,
            evidence_id="33333333-3333-4333-8333-333333333333",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with mock.patch.object(
                MODULE, "TRANSITION_INTENT_PATH", root / "intent.json"
            ), mock.patch.object(
                MODULE, "TRANSITION_COMPLETE_PATH", root / "complete.json"
            ), mock.patch.object(
                MODULE.os, "geteuid", return_value=0
            ), mock.patch.object(
                MODULE, "mutation_preflight", return_value={"ok": True, "errors": []}
            ), mock.patch.object(
                MODULE,
                "own_domain_state",
                return_value={"compatible": True, "profile": "maintenance"},
            ), mock.patch.object(
                MODULE, "postinstall_consistency_state"
            ) as consistency, mock.patch.object(
                MODULE, "publish_json_no_replace"
            ) as publish, mock.patch.object(MODULE, "virsh") as virsh_mock:
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    rc = MODULE.command_transition_maintenance(args)

        self.assertEqual(rc, 1)
        self.assertIn("only be created from the exact install profile", output.getvalue())
        consistency.assert_not_called()
        publish.assert_not_called()
        virsh_mock.assert_not_called()

    def test_postinstall_consistency_uses_historical_run_and_evidence(self) -> None:
        evidence_id = "33333333-3333-4333-8333-333333333333"
        run_payload = self.run_payload()
        run_state = {
            "ok": True,
            "run_id": run_payload["run_id"],
            "payload": run_payload,
            "errors": [],
        }
        fingerprint = "4" * 64
        receipt = {
            "ok": True,
            "evidence_id": evidence_id,
            "payload": {"artifact_stat_sha256": fingerprint},
            "errors": [],
        }
        domain = {"compatible": True, "profile": "install", "errors": []}
        valid_component = {"ok": True, "errors": []}
        with mock.patch.object(
            MODULE, "run_attestation_state", return_value=run_state
        ) as run_mock, mock.patch.object(
            MODULE,
            "guest_evidence_state",
            return_value={"ok": True, "errors": []},
        ) as evidence_mock, mock.patch.object(
            MODULE, "shutdown_receipt_state", return_value=receipt
        ), mock.patch.object(
            MODULE, "preinstall_provenance_state", return_value=valid_component
        ), mock.patch.object(
            MODULE, "own_domain_state", return_value=domain
        ), mock.patch.object(
            MODULE, "offline_domain_guards", return_value=valid_component
        ), mock.patch.object(
            MODULE,
            "domain_numeric_state",
            return_value={"ok": True, "state": 5, "reason": 1, "errors": []},
        ), mock.patch.object(
            MODULE, "disk_postinstall_state", return_value=valid_component
        ), mock.patch.object(
            MODULE, "postinstall_nvram_state", return_value=valid_component
        ), mock.patch.object(
            MODULE, "tpm_tree_state", return_value=valid_component
        ), mock.patch.object(
            MODULE,
            "offline_state_fingerprint",
            return_value={"sha256": fingerprint, "payload": {}},
        ):
            state = MODULE.postinstall_consistency_state(evidence_id)

        self.assertTrue(state["ok"], state)
        run_mock.assert_called_once_with(require_current_environment=False)
        evidence_mock.assert_called_once_with(
            evidence_id,
            "windows-installed",
            run_payload,
            enforce_freshness=False,
        )

    def test_maintenance_state_accepts_old_evidence_without_rolling_freshness(self) -> None:
        payload = self.maintenance_payload()
        run_payload = self.run_payload()
        run_state = {
            "ok": True,
            "run_id": run_payload["run_id"],
            "payload": run_payload,
            "errors": [],
        }
        old_evidence = self.guest_evidence_payload()
        old_evidence["captured_utc"] = "2025-01-01T11:00:00+00:00"

        def stable_hash(path, label):
            del label
            if path == MODULE.RUN_ATTESTATION_PATH:
                return payload["run"]["attestation_sha256"], mock.Mock()
            if path == MODULE.SHUTDOWN_RECEIPT_PATH:
                return payload["shutdown"]["receipt_sha256"], mock.Mock()
            raise AssertionError(path)

        with mock.patch.object(
            MODULE, "managed_json_object", return_value=(payload, [])
        ), mock.patch.object(
            MODULE, "run_attestation_state", return_value=run_state
        ) as run_mock, mock.patch.object(
            MODULE,
            "guest_evidence_state",
            return_value={
                "ok": True,
                "sha256": payload["evidence"]["sha256"],
                "payload": old_evidence,
                "errors": [],
            },
        ) as evidence_mock, mock.patch.object(
            MODULE, "stable_regular_file_hash", side_effect=stable_hash
        ), mock.patch.object(
            MODULE,
            "shutdown_receipt_state",
            return_value={
                "ok": True,
                "payload": {
                    "artifact_stat_sha256": payload["shutdown"]["artifact_stat_sha256"]
                },
                "errors": [],
            },
        ), mock.patch.object(
            MODULE,
            "preinstall_provenance_state",
            return_value={
                "ok": True,
                "sha256": payload["provenance"]["preinstall_sha256"],
                "errors": [],
            },
        ), mock.patch.object(
            MODULE,
            "disk_postinstall_state",
            return_value={"ok": True, "sha256": payload["disk"]["sha256"], "errors": []},
        ), mock.patch.object(
            MODULE,
            "postinstall_nvram_state",
            return_value={"ok": True, "sha256": payload["nvram"]["sha256"], "errors": []},
        ), mock.patch.object(
            MODULE,
            "tpm_tree_state",
            return_value={
                "ok": True,
                "tree_sha256": payload["tpm"]["tree_sha256"],
                "file_count": payload["tpm"]["file_count"],
                "errors": [],
            },
        ), mock.patch.object(
            MODULE,
            "own_domain_state",
            return_value={"compatible": True, "profile": "maintenance", "info": {"state": "shut off"}},
        ), mock.patch.object(
            MODULE, "offline_domain_guards", return_value={"ok": True, "errors": []}
        ), mock.patch.object(
            MODULE,
            "domain_numeric_state",
            return_value={"ok": True, "state": 5, "reason": 0, "errors": []},
        ), mock.patch.object(
            MODULE,
            "offline_state_fingerprint",
            return_value={
                "sha256": payload["shutdown"]["artifact_stat_sha256"],
                "payload": {},
            },
        ):
            state = MODULE.maintenance_state(verify_artifacts=True)

        self.assertTrue(state["ok"], state)
        run_mock.assert_called_once_with(require_current_environment=False)
        evidence_mock.assert_called_once_with(
            payload["evidence"]["id"],
            "windows-installed",
            run_payload,
            enforce_freshness=False,
        )

    def test_transition_never_redefines_before_consistency_passes(self) -> None:
        args = argparse.Namespace(
            json=True,
            evidence_id="33333333-3333-4333-8333-333333333333",
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            patches = (
                mock.patch.object(MODULE, "TRANSITION_INTENT_PATH", root / "intent.json"),
                mock.patch.object(MODULE, "TRANSITION_COMPLETE_PATH", root / "complete.json"),
            )
            with patches[0], patches[1], mock.patch.object(
                MODULE.os, "geteuid", return_value=0
            ), mock.patch.object(
                MODULE, "mutation_preflight", return_value={"ok": True, "errors": []}
            ), mock.patch.object(
                MODULE,
                "own_domain_state",
                return_value={"compatible": True, "profile": "install"},
            ), mock.patch.object(
                MODULE,
                "postinstall_consistency_state",
                return_value={"ok": False, "errors": ["disk failed"]},
            ), mock.patch.object(MODULE, "virsh") as virsh_mock, mock.patch.object(
                MODULE, "publish_json_no_replace"
            ) as publish:
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    rc = MODULE.command_transition_maintenance(args)
        self.assertEqual(rc, 1)
        virsh_mock.assert_not_called()
        publish.assert_not_called()

    def test_transition_publishes_intent_before_define_and_completion_last(self) -> None:
        args = argparse.Namespace(
            json=True,
            evidence_id="33333333-3333-4333-8333-333333333333",
        )
        run_id = "11111111-1111-4111-8111-111111111111"
        maintenance = {
            "schema": MODULE.MAINTENANCE_STATE_SCHEMA,
            "generation": "44444444-4444-4444-8444-444444444444",
            "phase": "windows-installed",
            "created_utc": "2026-07-17T13:00:00+00:00",
            "domain": {},
            "run": {"id": run_id},
            "disk": {},
            "nvram": {},
            "tpm": {},
            "evidence": {},
            "shutdown": {"artifact_stat_sha256": "f" * 64},
            "provenance": {},
        }
        consistency = {
            "ok": True,
            "run": {"run_id": run_id},
            "domain": {"profile": "install"},
            "errors": [],
        }
        stored: dict[Path, dict[str, object]] = {}
        events: list[str] = []

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            intent_path = root / "intent.json"
            maintenance_path = root / "maintenance.json"
            complete_path = root / "complete.json"

            def publish(path, payload, **kwargs):
                del kwargs
                stored[path] = payload
                if path == intent_path:
                    events.append("intent")
                elif path == maintenance_path:
                    events.append("maintenance")
                elif path == complete_path:
                    events.append("complete")

            def intent_state():
                payload = stored.get(intent_path, {})
                return {"ok": bool(payload), "payload": payload, "errors": []}

            def complete_state():
                payload = stored.get(complete_path, {})
                return {"ok": bool(payload), "payload": payload, "errors": []}

            def fake_virsh(arguments, readonly=False, timeout=20.0):
                del readonly, timeout
                if arguments[0] == "define":
                    events.append("define")
                elif arguments[0] == "autostart":
                    events.append("autostart")
                else:
                    raise AssertionError(arguments)
                return MODULE.CommandResult(0, "ok", "")

            patches = (
                mock.patch.object(MODULE, "TRANSITION_INTENT_PATH", intent_path),
                mock.patch.object(MODULE, "MAINTENANCE_ATTESTATION_PATH", maintenance_path),
                mock.patch.object(MODULE, "TRANSITION_COMPLETE_PATH", complete_path),
            )
            with patches[0], patches[1], patches[2], mock.patch.object(
                MODULE.os, "geteuid", return_value=0
            ), mock.patch.object(
                MODULE, "mutation_preflight", return_value={"ok": True, "errors": []}
            ), mock.patch.object(
                MODULE, "postinstall_consistency_state", return_value=consistency
            ), mock.patch.object(
                MODULE, "media_identities", return_value=self.media_identities()
            ), mock.patch.object(
                MODULE, "build_maintenance_payload", return_value=maintenance
            ), mock.patch.object(
                MODULE, "transition_intent_state", side_effect=intent_state
            ), mock.patch.object(
                MODULE, "consistency_matches_maintenance", return_value=[]
            ), mock.patch.object(
                MODULE, "virsh", side_effect=fake_virsh
            ), mock.patch.object(
                MODULE,
                "own_domain_state",
                side_effect=[
                    {"compatible": True, "profile": "install"},
                    {"compatible": True, "profile": "maintenance"},
                ],
            ), mock.patch.object(
                MODULE,
                "offline_state_fingerprint",
                return_value={"sha256": "f" * 64, "payload": {}},
            ), mock.patch.object(
                MODULE,
                "maintenance_state",
                return_value={"ok": True, "payload": maintenance, "errors": []},
            ), mock.patch.object(
                MODULE, "transition_complete_state", side_effect=complete_state
            ), mock.patch.object(
                MODULE,
                "maintenance_commit_boundary",
                return_value={"ok": True, "errors": []},
            ), mock.patch.object(
                MODULE, "publish_json_no_replace", side_effect=publish
            ), mock.patch.object(
                MODULE, "sha256_file", return_value="d" * 64
            ):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    rc = MODULE.command_transition_maintenance(args)

        self.assertEqual(rc, 0, output.getvalue())
        self.assertEqual(
            events,
            ["intent", "define", "autostart", "autostart", "maintenance", "complete"],
        )

    def test_mutation_lock_refuses_a_second_concurrent_holder(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            lock = Path(directory) / "apple.lock"
            identities = self.media_identities()
            with mock.patch.object(MODULE, "MUTATION_LOCK_PATH", lock), mock.patch.object(
                MODULE, "media_identities", return_value=identities
            ), mock.patch.object(MODULE.os, "geteuid", return_value=0):
                with MODULE.mutation_lock():
                    with self.assertRaisesRegex(RuntimeError, "already active"):
                        with MODULE.mutation_lock():
                            self.fail("second lock unexpectedly acquired")

    def test_apple_usb_gate_detects_vendor_without_reading_identifiers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            device = root / "1-1"
            device.mkdir()
            (device / "idVendor").write_text("05ac\n", encoding="utf-8")
            (device / "serial").write_text("sensitive-value\n", encoding="utf-8")
            with mock.patch.object(MODULE, "USB_DEVICES_ROOT", root):
                check = MODULE.apple_usb_check()
            self.assertFalse(check.ok)
            self.assertNotIn("sensitive-value", check.detail)
            self.assertIn("disconnect", check.detail)

    def test_apple_usb_gate_fails_closed_on_unreadable_vendor(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            device = root / "1-1"
            device.mkdir()
            vendor = device / "idVendor"
            vendor.write_text("05ac\n", encoding="utf-8")

            def unreadable(path: Path) -> str:
                if path == vendor:
                    raise PermissionError("denied")
                return path.read_text(encoding="utf-8").strip()

            with mock.patch.object(MODULE, "USB_DEVICES_ROOT", root), mock.patch.object(
                MODULE, "read_text", side_effect=unreadable
            ):
                check = MODULE.apple_usb_check()
            self.assertFalse(check.ok)
            self.assertIn("incomplete", check.detail)
            self.assertNotIn("denied", check.detail)

    def test_apple_usb_gate_fails_closed_on_malformed_vendor(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            device = root / "1-1"
            device.mkdir()
            (device / "idVendor").write_text("\n", encoding="utf-8")
            with mock.patch.object(MODULE, "USB_DEVICES_ROOT", root):
                check = MODULE.apple_usb_check()
            self.assertFalse(check.ok)
            self.assertIn("malformed", check.detail)

    def test_ac_gate_requires_online_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            adapter = root / "AC"
            adapter.mkdir()
            (adapter / "type").write_text("Mains\n", encoding="utf-8")
            (adapter / "online").write_text("1\n", encoding="utf-8")
            with mock.patch.object(MODULE, "POWER_SUPPLY_ROOT", root):
                self.assertTrue(MODULE.ac_power_check().ok)
            (adapter / "online").write_text("0\n", encoding="utf-8")
            with mock.patch.object(MODULE, "POWER_SUPPLY_ROOT", root):
                self.assertFalse(MODULE.ac_power_check().ok)

    def test_typec_gate_rejects_non_enumerated_source_host_partner(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            port = root / "port1"
            partner = root / "port1-partner"
            port.mkdir()
            partner.mkdir()
            (port / "power_role").write_text("sink [source]\n", encoding="utf-8")
            (port / "data_role").write_text("device [host]\n", encoding="utf-8")
            with mock.patch.object(MODULE, "TYPEC_ROOT", root):
                check = MODULE.typec_partner_check()
            self.assertFalse(check.ok)
            self.assertIn("port1", check.detail)

    def test_typec_gate_allows_charger_sink_device_partner(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            port = root / "port0"
            partner = root / "port0-partner"
            port.mkdir()
            partner.mkdir()
            (port / "power_role").write_text("[sink] source\n", encoding="utf-8")
            (port / "data_role").write_text("[device] host\n", encoding="utf-8")
            with mock.patch.object(MODULE, "TYPEC_ROOT", root):
                check = MODULE.typec_partner_check()
            self.assertTrue(check.ok, check)

    def test_entitlement_gate_blocks_current_unlicensed_profile(self) -> None:
        state = MODULE.entitlement_state()
        self.assertFalse(state["ok"], state)
        self.assertEqual(state["status"], "blocked-no-eligible-vm-entitlement")

    def test_entitlement_gate_accepts_only_exact_audited_status(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            profile = Path(directory) / "ctos-vms.json"
            profile.write_text(
                json.dumps(
                    {
                        "domains": [
                            {
                                "name": MODULE.DOMAIN,
                                "windows_vm_entitlement_status": MODULE.ELIGIBLE_DURABLE_ENTITLEMENT,
                                "enterprise_evaluation_status": "not-authorized-disposable-only",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            with mock.patch.object(MODULE, "FLEET_PROFILE_PATH", profile):
                state = MODULE.entitlement_state()
            self.assertTrue(state["ok"], state)

    def test_prepare_secure_state_requires_visible_root_invocation(self) -> None:
        args = argparse.Namespace(json=True)
        with mock.patch.object(MODULE.os, "geteuid", return_value=1000), mock.patch.object(
            MODULE, "mutation_preflight"
        ) as preflight:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                rc = MODULE.command_prepare_secure_state(args)
        self.assertEqual(rc, 1)
        self.assertFalse(json.loads(output.getvalue())["ok"])
        preflight.assert_not_called()

    def test_prepare_secure_state_builds_atomic_verified_layout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            parent = root / "snapshots"
            parent.mkdir()
            state_root = parent / "ctos-apple-recovery"
            nvram = state_root / "maintenance_VARS.fd"
            tpm = state_root / "maintenance-tpm"
            attestation = state_root / "maintenance-state.json"
            template = root / "OVMF_VARS.4m.fd"
            code = root / "OVMF_CODE.secboot.4m.fd"
            template.write_bytes(b"template")
            code.write_bytes(b"code")

            def fake_run(arguments, timeout=20.0):
                del timeout
                Path(arguments[-1]).write_bytes(b"generated secure vars")
                return MODULE.CommandResult(0, "generated", "")

            inspection = {"ok": True, "tool": "virt-fw-vars", "markers": {}, "errors": []}
            prepare_identities = {
                "ok": True,
                "root_uid": 31001,
                "qemu_uid": 31002,
                "swtpm_uid": 31003,
                "libvirt_gid": 31004,
                "errors": [],
            }
            test_identities = {
                "ok": True,
                "root_uid": os.getuid(),
                "qemu_uid": os.getuid(),
                "swtpm_uid": os.getuid(),
                "libvirt_gid": os.getgid(),
                "errors": [],
            }
            patches = (
                mock.patch.object(MODULE, "STATE_ROOT", state_root),
                mock.patch.object(MODULE, "NVRAM_PATH", nvram),
                mock.patch.object(MODULE, "TPM_STATE_PATH", tpm),
                mock.patch.object(MODULE, "STATE_ATTESTATION_PATH", attestation),
                mock.patch.object(MODULE, "OVMF_VARS_TEMPLATE_PATH", template),
                mock.patch.object(MODULE, "OVMF_CODE_PATH", code),
            )
            args = argparse.Namespace(json=True)
            with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], mock.patch.object(
                MODULE.os, "geteuid", return_value=0
            ), mock.patch.object(
                MODULE, "mutation_preflight", return_value={"ok": True, "errors": []}
            ), mock.patch.object(
                MODULE, "own_domain_state", return_value={"ok": True, "exists": False}
            ), mock.patch.object(
                MODULE.shutil, "which", return_value="/usr/bin/virt-fw-vars"
            ), mock.patch.object(
                MODULE, "run", side_effect=fake_run
            ), mock.patch.object(
                MODULE, "inspect_secure_boot_varstore", return_value=inspection
            ), mock.patch.object(
                MODULE,
                "secure_state_identities",
                side_effect=[prepare_identities, test_identities],
            ), mock.patch.object(
                MODULE.os, "chown"
            ) as chown_mock:
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    rc = MODULE.command_prepare_secure_state(args)
            self.assertEqual(rc, 0, output.getvalue())
            self.assertTrue(json.loads(output.getvalue())["ok"])
            self.assertTrue(nvram.is_file())
            self.assertTrue(tpm.is_dir())
            self.assertEqual(len(chown_mock.call_args_list), 4)
            chown_targets = [Path(call.args[0]) for call in chown_mock.call_args_list]
            self.assertEqual(chown_targets[0].parent, state_root.parent)
            self.assertTrue(chown_targets[0].name.startswith(".ctos-apple-recovery."))
            self.assertEqual(
                chown_targets[1:],
                [
                    chown_targets[0] / nvram.name,
                    chown_targets[0] / tpm.name,
                    chown_targets[0] / attestation.name,
                ],
            )
            self.assertEqual(
                [call.args[1:] for call in chown_mock.call_args_list],
                [
                    (prepare_identities["root_uid"], prepare_identities["libvirt_gid"]),
                    (prepare_identities["qemu_uid"], prepare_identities["libvirt_gid"]),
                    (prepare_identities["swtpm_uid"], prepare_identities["libvirt_gid"]),
                    (prepare_identities["root_uid"], prepare_identities["libvirt_gid"]),
                ],
            )
            self.assertEqual(state_root.stat().st_mode & 0o777, MODULE.STATE_ROOT_MODE)
            self.assertEqual(nvram.stat().st_mode & 0o777, MODULE.NVRAM_MODE)
            self.assertEqual(tpm.stat().st_mode & 0o777, MODULE.TPM_STATE_MODE)
            self.assertEqual(attestation.stat().st_mode & 0o777, MODULE.STATE_ATTESTATION_MODE)
            attestation_data = json.loads(attestation.read_text())
            self.assertEqual(attestation_data["phase"], "pre-install")
            self.assertEqual(
                attestation_data["state_permissions"]["nvram"],
                "libvirt-qemu:libvirt 0640",
            )

    def test_secure_state_requires_matching_nvram_hash_and_transition_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            code = root / "OVMF_CODE.fd"
            nvram = root / "maintenance_VARS.fd"
            tpm = root / "maintenance-tpm"
            evidence = root / "maintenance-state.json"
            code.write_bytes(b"code")
            nvram.write_bytes(b"prepared vars")
            tpm.mkdir()
            attestation = {
                "schema": MODULE.SECURE_STATE_SCHEMA,
                "domain": MODULE.DOMAIN,
                "phase": "pre-install",
                "nvram_path": str(nvram),
                "tpm_path": str(tpm),
                "secure_boot": True,
                "microsoft_db_2011": True,
                "microsoft_db_2023": True,
                "microsoft_kek_2011": True,
                "microsoft_kek_2023": True,
                "inspection": "virt-fw-vars --print",
                "nvram_sha256": hashlib.sha256(b"prepared vars").hexdigest(),
            }
            evidence.write_text(json.dumps(attestation), encoding="utf-8")
            os.chmod(root, MODULE.STATE_ROOT_MODE)
            os.chmod(nvram, MODULE.NVRAM_MODE)
            os.chmod(tpm, MODULE.TPM_STATE_MODE)
            os.chmod(evidence, MODULE.STATE_ATTESTATION_MODE)
            attestation["state_permissions"] = {
                "root": "root:libvirt 0751",
                "nvram": "libvirt-qemu:libvirt 0640",
                "tpm": "tss:libvirt 0750",
                "attestation": "root:libvirt 0640",
            }
            evidence.write_text(json.dumps(attestation), encoding="utf-8")
            os.chmod(evidence, MODULE.STATE_ATTESTATION_MODE)
            test_identities = {
                "ok": True,
                "root_uid": os.getuid(),
                "qemu_uid": os.getuid(),
                "swtpm_uid": os.getuid(),
                "libvirt_gid": os.getgid(),
                "errors": [],
            }
            patches = (
                mock.patch.object(MODULE, "STATE_ROOT", root),
                mock.patch.object(MODULE, "OVMF_CODE_PATH", code),
                mock.patch.object(MODULE, "NVRAM_PATH", nvram),
                mock.patch.object(MODULE, "TPM_STATE_PATH", tpm),
                mock.patch.object(MODULE, "STATE_ATTESTATION_PATH", evidence),
            )
            inspection = {"ok": True, "tool": "virt-fw-vars", "markers": {}, "errors": []}
            with patches[0], patches[1], patches[2], patches[3], patches[4], mock.patch.object(
                MODULE, "inspect_secure_boot_varstore", return_value=inspection
            ), mock.patch.object(
                MODULE, "secure_state_identities", return_value=test_identities
            ):
                state = MODULE.secure_state()
            self.assertTrue(state["ok"], state)

            os.chmod(root, 0o771)
            with patches[0], patches[1], patches[2], patches[3], patches[4], mock.patch.object(
                MODULE, "inspect_secure_boot_varstore"
            ) as inspect_mock, mock.patch.object(
                MODULE, "secure_state_identities", return_value=test_identities
            ):
                state = MODULE.secure_state()
            self.assertFalse(state["ok"], state)
            self.assertTrue(any("root mode" in error for error in state["errors"]))
            inspect_mock.assert_not_called()
            os.chmod(root, MODULE.STATE_ROOT_MODE)

            os.chmod(nvram, 0o660)
            with patches[0], patches[1], patches[2], patches[3], patches[4], mock.patch.object(
                MODULE, "inspect_secure_boot_varstore", return_value=inspection
            ), mock.patch.object(
                MODULE, "secure_state_identities", return_value=test_identities
            ):
                state = MODULE.secure_state()
            self.assertFalse(state["ok"], state)
            self.assertTrue(any("mode" in error for error in state["errors"]))
            os.chmod(nvram, MODULE.NVRAM_MODE)

            (tpm / "created-by-swtpm").write_bytes(b"state")
            with patches[0], patches[1], patches[2], patches[3], patches[4], mock.patch.object(
                MODULE, "inspect_secure_boot_varstore", return_value=inspection
            ), mock.patch.object(
                MODULE, "secure_state_identities", return_value=test_identities
            ):
                state = MODULE.secure_state()
            self.assertFalse(state["ok"], state)
            self.assertTrue(any("strictly empty" in error for error in state["errors"]))

    def test_secure_state_rejects_symlinked_managed_root_without_inspecting_children(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            real_root = base / "real-state"
            real_root.mkdir()
            linked_root = base / "managed-state"
            linked_root.symlink_to(real_root, target_is_directory=True)
            code = base / "OVMF_CODE.fd"
            code.write_bytes(b"code")
            test_identities = {
                "ok": True,
                "root_uid": os.getuid(),
                "qemu_uid": os.getuid(),
                "swtpm_uid": os.getuid(),
                "libvirt_gid": os.getgid(),
                "errors": [],
            }
            with mock.patch.object(MODULE, "STATE_ROOT", linked_root), mock.patch.object(
                MODULE, "NVRAM_PATH", linked_root / "maintenance_VARS.fd"
            ), mock.patch.object(
                MODULE, "TPM_STATE_PATH", linked_root / "maintenance-tpm"
            ), mock.patch.object(
                MODULE, "STATE_ATTESTATION_PATH", linked_root / "maintenance-state.json"
            ), mock.patch.object(
                MODULE, "OVMF_CODE_PATH", code
            ), mock.patch.object(
                MODULE, "secure_state_identities", return_value=test_identities
            ), mock.patch.object(
                MODULE, "inspect_secure_boot_varstore"
            ) as inspect_mock:
                state = MODULE.secure_state()
            self.assertFalse(state["ok"], state)
            self.assertTrue(any("root" in error and "symlink" in error for error in state["errors"]))
            inspect_mock.assert_not_called()

    def test_varstore_inspection_rejects_missing_transition_keys(self) -> None:
        with mock.patch.object(MODULE.shutil, "which", return_value="/usr/bin/virt-fw-vars"), mock.patch.object(
            MODULE,
            "run",
            return_value=MODULE.CommandResult(0, "name=SecureBootEnable\n  bool: ON", ""),
        ):
            state = MODULE.inspect_secure_boot_varstore(Path("/tmp/test-vars.fd"))
        self.assertFalse(state["ok"])
        self.assertTrue(any("missing" in error for error in state["errors"]))

    def test_usb_preflight_needs_isolated_group_and_explicit_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cmdline = root / "cmdline"
            cmdline.write_text("quiet intel_iommu=on\n", encoding="utf-8")
            iommu_root = root / "iommu_groups"
            group = iommu_root / "17"
            devices = group / "devices"
            devices.mkdir(parents=True)
            pci_root = root / "pci"
            controller = pci_root / MODULE.USB_CONTROLLER
            controller.mkdir(parents=True)
            (controller / "vendor").write_text("0x8086\n", encoding="utf-8")
            (controller / "device").write_text("0x15c1\n", encoding="utf-8")
            (controller / "class").write_text("0x0c0330\n", encoding="utf-8")
            (controller / "iommu_group").symlink_to(group, target_is_directory=True)
            (devices / MODULE.USB_CONTROLLER).symlink_to(controller, target_is_directory=True)
            driver_dir = root / "drivers" / "xhci_hcd"
            driver_dir.mkdir(parents=True)
            (controller / "driver").symlink_to(driver_dir, target_is_directory=True)

            power = root / "power"
            ac = power / "AC"
            ac.mkdir(parents=True)
            (ac / "type").write_text("Mains\n", encoding="utf-8")
            (ac / "online").write_text("1\n", encoding="utf-8")
            usb = root / "usb"
            usb.mkdir()
            typec = root / "typec"
            typec.mkdir()
            evidence = root / "usb.json"
            evidence.write_text(
                json.dumps(
                    {
                        "schema": MODULE.USB_QUALIFICATION_SCHEMA,
                        "controller": MODULE.USB_CONTROLLER,
                        "group_isolated": True,
                        "physical_port_mapped": True,
                        "non_sensitive_reenumeration_passed": True,
                        "managed_detach_reattach_passed": True,
                        "ac_charging_survived": True,
                    }
                ),
                encoding="utf-8",
            )
            with mock.patch.object(MODULE, "PROC_CMDLINE_PATH", cmdline), mock.patch.object(
                MODULE, "IOMMU_GROUPS_ROOT", iommu_root
            ), mock.patch.object(MODULE, "PCI_DEVICES_ROOT", pci_root), mock.patch.object(
                MODULE, "POWER_SUPPLY_ROOT", power
            ), mock.patch.object(MODULE, "USB_DEVICES_ROOT", usb), mock.patch.object(
                MODULE, "USB_QUALIFICATION_PATH", evidence
            ), mock.patch.object(
                MODULE, "TYPEC_ROOT", typec
            ), mock.patch.object(
                MODULE, "USB_QUALIFICATION_IMPLEMENTED", True
            ):
                state = MODULE.usb_qualification_state()
            self.assertTrue(state["ok"], state)
            self.assertEqual(state["group_members"], [MODULE.USB_CONTROLLER])

    def test_usb_evidence_cannot_enable_unimplemented_session_workflow(self) -> None:
        self.assertFalse(MODULE.USB_QUALIFICATION_IMPLEMENTED)

    def test_shutdown_uses_acpi_and_has_no_force_or_agent_fallback(self) -> None:
        args = argparse.Namespace(json=False, wait=0)
        with mock.patch.object(
            MODULE,
            "own_domain_state",
            return_value={"exists": True, "info": {"state": "running"}},
        ), mock.patch.object(
            MODULE,
            "virsh",
            return_value=MODULE.CommandResult(0, "shutdown requested", ""),
        ) as virsh_mock:
            with contextlib.redirect_stdout(io.StringIO()):
                rc = MODULE.command_shutdown(args)
        self.assertEqual(rc, 0)
        virsh_mock.assert_called_once_with(["shutdown", MODULE.DOMAIN, "--mode", "acpi"])

    def test_running_domain_requires_live_xml_allowlist(self) -> None:
        inactive = MODULE.MAINTENANCE_XML_PATH.read_text(encoding="utf-8")
        live_root = ET.fromstring(inactive)
        devices = live_root.find("./devices")
        extra = ET.SubElement(devices, "interface", {"type": "bridge"})
        ET.SubElement(extra, "source", {"bridge": "br0"})
        ET.SubElement(extra, "model", {"type": "e1000e"})
        live = ET.tostring(live_root, encoding="unicode")

        def fake_virsh(arguments, readonly=False, timeout=20.0):
            del readonly, timeout
            if arguments == ["dominfo", MODULE.DOMAIN]:
                return MODULE.CommandResult(
                    0,
                    "Name: ctos-apple-recovery\nState: running\nAutostart: disable\n"
                    "Autostart Once: disable\nManaged save: no",
                    "",
                )
            if arguments == ["dumpxml", "--inactive", MODULE.DOMAIN]:
                return MODULE.CommandResult(0, inactive, "")
            if arguments == ["dumpxml", MODULE.DOMAIN]:
                return MODULE.CommandResult(0, live, "")
            raise AssertionError(arguments)

        with mock.patch.object(MODULE, "virsh", side_effect=fake_virsh):
            state = MODULE.own_domain_state()
        self.assertFalse(state["compatible"], state)
        self.assertTrue(any("live XML" in error for error in state["errors"]))

    def test_maintenance_profile_start_fails_closed_without_libvirt_calls(self) -> None:
        args = argparse.Namespace(profile="maintenance", json=True, open_console=False)
        with mock.patch.object(MODULE, "virsh") as virsh_mock, mock.patch.object(
            MODULE, "mutation_preflight"
        ) as preflight_mock:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                rc = MODULE.command_start_maintenance(args)
        self.assertEqual(rc, 1)
        self.assertFalse(json.loads(output.getvalue())["ok"])
        virsh_mock.assert_not_called()
        preflight_mock.assert_not_called()

    def test_unavailable_session_phases_fail_closed_without_libvirt_calls(self) -> None:
        args = argparse.Namespace(json=True)
        for function in (
            MODULE.command_seal_baseline,
            MODULE.command_start_session,
            MODULE.command_close_session,
        ):
            with self.subTest(function=function.__name__), mock.patch.object(MODULE, "virsh") as virsh_mock:
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    rc = function(args)
                self.assertEqual(rc, 1)
                self.assertFalse(json.loads(output.getvalue())["ok"])
                virsh_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
