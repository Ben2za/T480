# Windows Apple Recovery VM Implementation State

Date: 2026-07-17

Goal boundary: build and verify a clean Windows/Apple recovery workstation and
test its USB-C path only with a non-sensitive peripheral. The iPhone must not be
attached to the VM, placed in recovery/DFU, erased, restored, queried, or used
for passcode attempts in this goal.

## Current Phase State

| Phase | State | Evidence / gate |
| --- | --- | --- |
| 0 — preflight | complete | AC online, about 195 GiB free, Kali shut off, CTOS pools/network active, Arch news reviewed. |
| 1 — host packages | applied; reboot pending | Full signed Arch transaction completed. `swtpm`, `virt-firmware`, QEMU, libvirt, systemd, and both kernels were upgraded. Two mirror-list `.pacnew` files remain for explicit review. |
| 2 — IOMMU/controller | blocked before reboot | `intel_iommu=on` is absent and groups are empty. The iPhone remains a Type-C `source/host` partner on the candidate controller and must be physically unplugged first. |
| 3 — media | implementation ready; live import blocked | `import-media` now provides authenticated no-replace import and strict attestation, but no eligible Windows VM entitlement exists, no ISO was read/imported, and the official Enterprise Evaluation remains a separate unauthorized option. |
| 4 — repo/domain | pre-install scaffold complete | XML/profile/helpers/tests/runbook are present. Licence and non-enumerated Type-C gates are code-enforced; active/inactive XML is allowlisted; Secure Boot inspection is live. Risky unfinished phases refuse with no fallback. No live domain is defined. |
| 5 — Windows | blocked | Requires an eligible durable VM entitlement, or explicit authorization for a disposable 90-day Enterprise Evaluation VM, plus verified matching Microsoft ISO and post-reboot host checks. |
| 6 — Apple baseline | not started | Requires fully updated Windows and official Store product `9NP83LWLPZ9K`. |
| 7 — non-sensitive USB | not started | Requires an isolated IOMMU group, safe controller detach/reattach, and a non-sensitive test peripheral. |

## Applied Host Package State

- QEMU: `11.0.2-3`
- libvirt: `12.5.0-1`
- systemd: `261.1-1`
- `linux-lts`: `6.18.38-4`
- `swtpm`: `0.10.1-2`
- `virt-firmware`: `26.7.1-1`

Post-transaction `pacman -Qu` returned no pending repository upgrade. The
running kernel is still the pre-transaction `6.18.33-1-lts`, so a controlled
reboot is required.

The two `.pacnew` files were reviewed. Arch's new `mirrorlist.pacnew` is the
full all-commented package template, while the active file is a working
Reflector-generated HTTPS ranking. The EndeavourOS `.pacnew` is only a newer
ranked mirror ordering; the active ranking completed this full transaction.
Both are intentionally retained for later mirror maintenance and are not
silently substituted during VM work.

## Secure Boot / TPM Evidence

Post-upgrade libvirt domain capabilities for `pc-q35-11.0` expose:

- OVMF Secure Boot firmware;
- `tpm-crb`;
- TPM emulator backend version 2.0.

The packaged OVMF descriptor still reports `enrolledKeys=no`. A temporary
varstore generation test with `virt-fw-vars` succeeded and inspection showed:

- Microsoft KEK CA 2011 and Microsoft KEK 2K CA 2023;
- Microsoft Windows Production PCA 2011 and Windows UEFI CA 2023;
- Microsoft UEFI CA 2011, UEFI CA 2023, and Option ROM UEFI CA 2023;
- Microsoft 2023 OEM platform key;
- `SecureBootEnable=ON`, `CustomMode=off`.

The temporary file was not a VM state or baseline and was explicitly removed
after inspection. No test varstore remains under `/tmp`.

## Driver Provenance Amendment

The community virtio-win stable repository sets `gpgcheck=0`; its RPM and
repository metadata are unsigned, and no supplier SHA-256 is published for the
ISO. The reproducible ISO digest embedded in the unsigned RPM is therefore only
a TLS-linked integrity check, not independent publisher authentication.

Decision: use Windows 11 inbox AHCI/SATA and Intel e1000e drivers for the first
baseline. Do not download or attach the community VirtIO ISO. Optional
`PCI\\VEN_1AF4` drivers are allowed only through Windows Update/Microsoft
Update Catalog after signature/publisher validation. QEMU Guest Agent is not a
first-baseline dependency.

## Licensing Gate

The operator confirmed on 2026-07-17 that no Windows licence is available for
this VM. The durable `apple-ready` baseline is therefore blocked before media
acquisition and installation. Microsoft documents a no-key Windows 11
Enterprise 25H2 Evaluation for 90 days, but it is intended for IT evaluation,
requires a Microsoft account, and shuts down hourly after expiration. It may
only be used as an explicitly approved disposable compatibility test and must
never be sealed or represented as the reusable recovery baseline.

## Scaffold Verification And Closed Features

The repository now contains two libvirt-valid hostdev-free XML profiles and
helpers for host IOMMU preflight, read-only status/plan, exact entitlement and
media checks, install-domain definition, ACPI shutdown, and atomic generation
of inspected pre-install NVRAM plus an empty private TPM state directory.

Independent review found and the implementation corrected these fail-open
risks before use:

- the lifecycle helper now reads the exact durable entitlement state;
- a Type-C source/host partner blocks mutations even without Apple USB
  enumeration;
- active and inactive domain XML must both match an exact device allowlist;
- `virt-fw-vars --print --verbose` must actually expose Secure Boot and the
  Microsoft 2011/2023 transition certificates;
- real Mains telemetry, exact PCI identity/group/driver, and no ACS override
  are required;
- parser profiles are explicit, and maintenance transition is closed.
- the secure-state root, NVRAM, TPM directory, and attestation now require
  exact canonical paths, owner identities resolved by name, and modes
  `root:libvirt 0751`, `libvirt-qemu:libvirt 0640`, `tss:libvirt 0750`, and
  `root:libvirt 0640`; the pre-install TPM directory must be strictly empty;
- unreadable or malformed USB `idVendor` inventory blocks instead of being
  silently skipped, and emulator/serial/console/video/PCR/image settings plus
  recursively allowlisted device-child tags are part of the XML signature;
  host serial logs, SPICE rendernodes, interface ROMs, nested video acceleration,
  and TPM encryption/profile drift are refused.

`seal-baseline`, `start-session`, `close-session`, maintenance transition, and
trusted USB qualification still return a hard refusal with no fallback.
Authenticated ISO import is implemented but its preflight refuses before
source access while the durable entitlement is absent. It uses a fixed
filename/hash, canonical single-link source, before/after source hashing,
same-filesystem no-replace publication, exact managed ownership/modes, a
strict attestation, libvirt pool refresh, and exact volume-path verification.
At this checkpoint `53` combined unit tests passed; both XML documents passed
`virt-xml-validate`; Python compilation, JSON parsing, and `git diff --check`
passed. A read-only live libvirt plan confirmed Kali shut off, CTOS network and
pools active, no Apple domain/volume, the licence refusal, and the live
`port1` Type-C refusal.

## USB-C Safety Finding

`lsusb` has no Apple child, but `/sys/class/typec/port1-partner` exists with
`port1` in `source/host` roles. That is the locked iPhone on the JHL6240 xHCI
candidate `0000:3c:00.0`. A helper that checks only USB children would be
unsafe. All IOMMU apply, controller detach, and guest start paths must also
refuse a Type-C partner on the controller-facing source/host port.

## Exact Next Gates

1. Physically unplug the iPhone; keep the charger on the separate sink/device
   Type-C port.
2. Verify `port1-partner` disappeared and USB buses 3/4 contain no children.
3. Apply only `intel_iommu=on`, after a root-owned backup of
   `/etc/kernel/cmdline`; rebuild and inspect both kernel entries.
4. Reboot deliberately, then prove non-empty IOMMU groups and inspect the full
   group containing `0000:3c:00.0`.
5. With the phone absent, generate the pre-install NVRAM/TPM scaffold through
   the guarded `prepare-secure-state` command; this does not create/start a VM.
6. Resolve the licensing choice. For a durable VM, obtain an entitlement that
   expressly covers the virtual machine, then re-check the current matching
   ISO and hash on Microsoft's live page. If a disposable Enterprise
   Evaluation is explicitly authorized instead, use its separate Evaluation
   Center ISO/hash and never the consumer hash recorded below.
7. Only after the durable entitlement record changes, run the guarded
   `import-media --source /absolute/path/Win11_25H2_French_x64_v2.iso`; do not
   copy the ISO into the pool manually.

The previously observed consumer French 25H2 hash was
`a02693beb8eb166afdfdb7db49176a2b547f81e61030a695fe172277db6a1977`;
it is not an authorization to install that edition.

No managed NVRAM/TPM state, VM disk, VM definition, Windows installation,
Apple software installation, USB controller detach, reboot, or phone mutation
has occurred as of this state record.
