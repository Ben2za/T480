from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import shutil
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ctos-apple-host"
LOADER = importlib.machinery.SourceFileLoader("ctos_apple_host", str(SCRIPT))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
assert SPEC is not None
apple = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = apple
LOADER.exec_module(apple)


def safe_status(*, runtime_configured: bool = False) -> dict:
    configured = {
        "path": "/etc/kernel/cmdline",
        "readable": True,
        "runtime": False,
        "intel_iommu_on_count": 1,
        "configured": True,
        "conflicting_iommu_tokens": [],
        "duplicate": False,
        "acs_override_tokens": [],
    }
    runtime = dict(configured)
    runtime.update(
        {
            "path": "/proc/cmdline",
            "runtime": True,
            "intel_iommu_on_count": 1 if runtime_configured else 0,
            "configured": runtime_configured,
        }
    )
    return {
        "ac": {"online": True, "supplies": [], "error": ""},
        "kali": {"domain": "ctos-kali", "state": "shut off", "shut_off": True, "error": ""},
        "typec": {"partners": [], "unsafe": False, "errors": []},
        "usb": [],
        "usb_errors": [],
        "configured_cmdline": configured,
        "runtime_cmdline": runtime,
        "candidate": {
            "bdf": apple.CANDIDATE_BDF,
            "identity": {
                "bdf": apple.CANDIDATE_BDF,
                "vendor": apple.CANDIDATE_VENDOR,
                "device": apple.CANDIDATE_DEVICE,
                "class": "0x0c0330",
                "driver": "xhci_hcd",
            },
            "usb_children": [],
            "mapping_errors": [],
        },
        "iommu": {
            "nonempty": True,
            "groups": [
                {
                    "group": "17",
                    "members": [
                        {
                            "bdf": apple.CANDIDATE_BDF,
                            "vendor": apple.CANDIDATE_VENDOR,
                            "device": apple.CANDIDATE_DEVICE,
                            "class": "0x0c0330",
                            "driver": "xhci_hcd",
                        }
                    ],
                }
            ],
        },
        "refusals": [],
        "safe_for_apply": True,
    }


class CmdlineTests(unittest.TestCase):
    def test_selected_typec_role_uses_bracketed_active_value(self) -> None:
        self.assertEqual(apple.selected_role("source [sink]\n"), "sink")
        self.assertEqual(apple.selected_role("[host] device\n"), "host")
        self.assertEqual(apple.selected_role("device\n"), "device")

    def test_iommu_option_is_appended_once_and_is_idempotent(self) -> None:
        original = "quiet rw root=/dev/mapper/root\n"
        changed, did_change = apple.updated_cmdline(original)
        self.assertTrue(did_change)
        self.assertEqual(changed, "quiet rw root=/dev/mapper/root intel_iommu=on\n")

        unchanged, did_change_again = apple.updated_cmdline(changed)
        self.assertFalse(did_change_again)
        self.assertEqual(unchanged, changed)

    def test_conflict_and_duplicate_are_refused(self) -> None:
        with self.assertRaisesRegex(ValueError, "conflicting"):
            apple.updated_cmdline("quiet intel_iommu=off\n")
        with self.assertRaisesRegex(ValueError, "duplicated"):
            apple.updated_cmdline("intel_iommu=on quiet intel_iommu=on\n")


class SafetyTests(unittest.TestCase):
    def test_source_host_partner_and_apple_usb_are_refusals(self) -> None:
        state = safe_status()
        state["typec"] = {
            "partners": [
                {
                    "port": "port1",
                    "power_role": "source",
                    "data_role": "host",
                    "unsafe_source_or_host": True,
                }
            ],
            "unsafe": True,
        }
        state["usb"] = [
            {
                "sysfs_name": "4-1",
                "vendor": "05ac",
                "product": "12a8",
                "apple": True,
            }
        ]
        reasons = apple.safety_refusals(state)
        self.assertTrue(any("source/host" in item for item in reasons))
        self.assertTrue(any("Apple USB" in item for item in reasons))

    def test_ac_and_kali_are_mandatory(self) -> None:
        state = safe_status()
        state["ac"]["online"] = False
        state["kali"]["shut_off"] = False
        reasons = apple.safety_refusals(state)
        self.assertTrue(any("AC power" in item for item in reasons))
        self.assertTrue(any("ctos-kali" in item for item in reasons))

    def test_typec_sysfs_active_roles_are_audited(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "port0").mkdir()
            (root / "port0-partner").mkdir()
            (root / "port0" / "power_role").write_text("sink [source]\n", encoding="utf-8")
            (root / "port0" / "data_role").write_text("device [host]\n", encoding="utf-8")
            with mock.patch.object(apple, "TYPEC_ROOT", root):
                result = apple.typec_state()
        self.assertTrue(result["unsafe"])
        self.assertEqual(result["partners"][0]["power_role"], "source")
        self.assertEqual(result["partners"][0]["data_role"], "host")

    def test_unknown_typec_roles_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "port1").mkdir()
            (root / "port1-partner").mkdir()
            (root / "port1" / "power_role").write_text("sink source\n", encoding="utf-8")
            (root / "port1" / "data_role").write_text("\n", encoding="utf-8")
            with mock.patch.object(apple, "TYPEC_ROOT", root):
                result = apple.typec_state()
        self.assertTrue(result["unsafe"])
        self.assertTrue(result["errors"])
        self.assertTrue(result["partners"][0]["unsafe_source_or_host"])

    def test_usb_vendor_inventory_errors_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            device = root / "4-1"
            device.mkdir()
            vendor_path = device / "idVendor"
            vendor_path.write_text("05ac\n", encoding="utf-8")
            original_read_text = Path.read_text

            def guarded_read_text(path: Path, *args, **kwargs):
                if path == vendor_path:
                    raise PermissionError("denied")
                return original_read_text(path, *args, **kwargs)

            with mock.patch.object(apple, "USB_ROOT", root), mock.patch.object(
                Path, "read_text", guarded_read_text
            ):
                inventory = apple.usb_inventory()
        self.assertEqual(inventory["devices"], [])
        self.assertTrue(any("PermissionError" in error for error in inventory["errors"]))
        state = safe_status()
        state["usb_errors"] = inventory["errors"]
        self.assertTrue(any("USB inventory unsafe" in item for item in apple.safety_refusals(state)))


class QualificationTests(unittest.TestCase):
    def test_isolated_expected_controller_qualifies_without_acs(self) -> None:
        state = safe_status(runtime_configured=True)
        result = apple.qualification(state)
        self.assertTrue(result["qualified"])
        self.assertFalse(result["acs_override_used"])
        self.assertFalse(result["automatic_detach_performed"])

    def test_shared_group_is_not_auto_qualified(self) -> None:
        state = safe_status(runtime_configured=True)
        state["iommu"]["groups"][0]["members"].append(
            {
                "bdf": "0000:3d:00.0",
                "vendor": "0x8086",
                "device": "0x15c0",
                "class": "0x088000",
                "driver": "thunderbolt",
            }
        )
        result = apple.qualification(state)
        self.assertFalse(result["qualified"])
        self.assertTrue(any("not isolated" in item for item in result["reasons"]))

    def test_non_xhci_host_driver_is_not_qualified(self) -> None:
        state = safe_status(runtime_configured=True)
        state["candidate"]["identity"]["driver"] = "vfio-pci"
        result = apple.qualification(state)
        self.assertFalse(result["qualified"])
        self.assertTrue(any("host-bound" in item for item in result["reasons"]))

    def test_acs_override_is_never_accepted(self) -> None:
        state = safe_status(runtime_configured=True)
        state["runtime_cmdline"]["acs_override_tokens"] = ["pcie_acs_override=downstream"]
        state["refusals"] = ["ACS override is configured or active"]
        result = apple.qualification(state)
        self.assertFalse(result["qualified"])
        self.assertTrue(result["acs_override_used"])

    def test_two_installed_kernel_entries_must_contain_option(self) -> None:
        entries = [
            {"version": "6.18.38-4-lts", "options": "quiet intel_iommu=on"},
            {"version": "7.1.3-arch2-2", "options": ["quiet", "intel_iommu=on"]},
        ]
        with (
            mock.patch.object(
                apple,
                "installed_kernel_versions",
                return_value=["6.18.38-4-lts", "7.1.3-arch2-2"],
            ),
            mock.patch.object(apple, "boot_entries", return_value=(entries, "")),
        ):
            result = apple.inspect_kernel_entries()
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["inspected"]), 2)


class ApplyTests(unittest.TestCase):
    def test_sudo_wrapper_always_uses_sudo_separator(self) -> None:
        with mock.patch.object(
            apple,
            "run",
            return_value=apple.CommandResult(0, "", ""),
        ) as mocked:
            apple.sudo(["reinstall-kernels"], timeout=123)
        mocked.assert_called_once_with(
            ["sudo", "--", "reinstall-kernels"],
            timeout=123,
            input_text=None,
        )

    def test_apply_backs_up_preserving_metadata_rebuilds_and_never_reboots(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cmdline = Path(directory) / "cmdline"
            cmdline.write_text("quiet rw\n", encoding="utf-8")
            cmdline.chmod(0o640)
            commands: list[list[str]] = []

            def fake_sudo(args, *, timeout=30.0, input_text=None):
                commands.append(list(args))
                if args[0] == "cp":
                    shutil.copy2(args[-2], args[-1])
                    return apple.CommandResult(0, "", "")
                if args[0] == "stat":
                    info = os.stat(args[-1])
                    mode = stat.S_IMODE(info.st_mode)
                    return apple.CommandResult(
                        0,
                        f"{mode:o}:{info.st_uid}:{info.st_gid}:{info.st_size}",
                        "",
                    )
                if args[0] == "tee":
                    Path(args[-1]).write_text(input_text, encoding="utf-8")
                    return apple.CommandResult(0, input_text, "")
                if args[0] == "reinstall-kernels":
                    return apple.CommandResult(0, "rebuilt", "")
                raise AssertionError(f"unexpected sudo command: {args}")

            status_state = safe_status(runtime_configured=False)
            status_state["configured_cmdline"]["configured"] = False
            status_state["configured_cmdline"]["intel_iommu_on_count"] = 0
            with (
                mock.patch.object(apple, "CMDLINE_PATH", cmdline),
                mock.patch.object(apple, "collect_status", return_value=status_state),
                mock.patch.object(apple, "sudo", side_effect=fake_sudo),
                mock.patch.object(
                    apple,
                    "inspect_kernel_entries",
                    return_value={
                        "installed_kernel_versions": ["kernel-a", "kernel-b"],
                        "minimum_two_entries": True,
                        "inspected": [
                            {"version": "kernel-a", "ok": True},
                            {"version": "kernel-b", "ok": True},
                        ],
                        "ok": True,
                        "error": "",
                    },
                ),
            ):
                result, rc = apple.apply_iommu()

            self.assertEqual(rc, 0)
            self.assertTrue(result["changed"])
            self.assertTrue(result["reinstall_kernels_run"])
            self.assertTrue(result["reboot_required"])
            self.assertFalse(result["reboot_performed"])
            self.assertFalse(result["pci_detach_performed"])
            self.assertEqual(cmdline.read_text(encoding="utf-8").count(apple.IOMMU_TOKEN), 1)
            self.assertEqual(stat.S_IMODE(cmdline.stat().st_mode), 0o640)
            backup = Path(result["backup"])
            self.assertTrue(backup.exists())
            self.assertEqual(stat.S_IMODE(backup.stat().st_mode), 0o640)
            invoked = [item[0] for item in commands]
            self.assertIn("cp", invoked)
            self.assertIn("tee", invoked)
            self.assertIn("reinstall-kernels", invoked)
            self.assertNotIn("reboot", invoked)
            self.assertNotIn("virsh", invoked)

    def test_apply_refuses_before_any_sudo_mutation(self) -> None:
        state = safe_status()
        state["refusals"] = ["Apple USB device present: 4-1"]
        state["safe_for_apply"] = False
        with (
            mock.patch.object(apple, "collect_status", return_value=state),
            mock.patch.object(apple, "sudo") as sudo_mock,
        ):
            result, rc = apple.apply_iommu()
        self.assertEqual(rc, 2)
        self.assertIn("Apple USB", result["refusals"][0])
        sudo_mock.assert_not_called()

    def test_apply_is_idempotent_when_config_and_entries_are_ready(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cmdline = Path(directory) / "cmdline"
            cmdline.write_text("quiet intel_iommu=on\n", encoding="utf-8")
            with (
                mock.patch.object(apple, "CMDLINE_PATH", cmdline),
                mock.patch.object(apple, "collect_status", return_value=safe_status()),
                mock.patch.object(
                    apple,
                    "inspect_kernel_entries",
                    return_value={"ok": True, "installed_kernel_versions": ["a", "b"]},
                ),
                mock.patch.object(apple, "sudo") as sudo_mock,
            ):
                result, rc = apple.apply_iommu()
        self.assertEqual(rc, 0)
        self.assertFalse(result["changed"])
        self.assertFalse(result["reinstall_kernels_run"])
        self.assertTrue(result["reboot_required"])
        sudo_mock.assert_not_called()


class CliTests(unittest.TestCase):
    def test_json_flag_is_accepted_before_or_after_command(self) -> None:
        before, before_json = apple.parse_args(["--json", "status"])
        after, after_json = apple.parse_args(["status", "--json"])
        self.assertEqual(before.command, "status")
        self.assertEqual(after.command, "status")
        self.assertTrue(before_json)
        self.assertTrue(after_json)

    def test_status_json_is_machine_readable(self) -> None:
        state = safe_status()
        with (
            mock.patch.object(apple, "collect_status", return_value=state),
            mock.patch("builtins.print") as print_mock,
        ):
            rc = apple.main(["status", "--json"])
        self.assertEqual(rc, 0)
        payload = json.loads(print_mock.call_args.args[0])
        self.assertEqual(payload["operation"], "status")


if __name__ == "__main__":
    unittest.main()
