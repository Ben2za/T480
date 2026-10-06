# Windows Apple Recovery VM Plan

Date: 2026-07-17

Status: architecture complete; implementation in progress with amendment below

Scope: reusable Windows 11 VM on the T480 for official Apple Devices recovery
and restore workflows. The first target device is an operator-confirmed iPhone
XS. No serial number, IMEI, ECID, Apple Account, passcode, or other device
identifier is stored in this repo.

## Outcome

Build a repo-defined `ctos-apple-recovery` domain on `qemu:///system` with:

- current supported Windows 11 x64 media from Microsoft;
- Q35, UEFI Secure Boot, Microsoft transition-era 2011 and 2023 certificates,
  and an emulated TPM 2.0;
- 4 vCPU, 8192 MiB RAM, and a sparse 96 GiB qcow2 system disk;
- Windows inbox AHCI/SATA storage and Intel e1000e network drivers;
- the Apple Devices app installed only from its Microsoft Store product page;
- CTOS NAT egress, no inbound forwarding, no host folder, and no VM autostart;
- an offline `apple-ready` baseline and disposable per-recovery working state;
- whole-controller USB-C passthrough only if IOMMU isolation is proven;
- explicit gates before recovery mode, firmware download, Restore, and cleanup.

No VM, media, package, boot configuration, or phone state is changed by this
planning document.

### Implementation amendment — 2026-07-17

The planned community virtio-win ISO is no longer an installation dependency.
Implementation research found that stable `0.1.285-1` has no signed RPM,
signed repository metadata, or supplier-published SHA-256 for the ISO; the
upstream repository explicitly sets `gpgcheck=0`. Under the repo's provenance
contract, a TLS-only artifact cannot become the driver trust root.

Bootstrap the VM with Windows 11 inbox AHCI/SATA storage and Intel e1000e
network drivers. These are adequate for an Apple restore workstation. Do not
download or attach the community VirtIO ISO. If a later measured need justifies
VirtIO, introduce only the specific `PCI\\VEN_1AF4` drivers delivered through
Windows Update/Microsoft Update Catalog and verified by Windows. QEMU Guest
Agent is optional and omitted from the first trusted baseline.

This amendment supersedes later references in this planning document that
require a VirtIO ISO, VirtIO system disk/NIC, or QEMU Guest Agent. All other
gates remain in force.

### Licensing amendment — 2026-07-17

The operator has no Windows licence for this VM. Host preparation and
declarative scaffolding may continue, but a consumer Windows edition must not
be installed or sealed as the reusable baseline until an entitlement that
explicitly covers the VM is identified. Microsoft's official Windows 11
Enterprise 25H2 Evaluation is a separate 90-day, no-key option intended for IT
evaluation; it requires a Microsoft account and shuts down hourly after expiry.
It may only be used after explicit approval as a disposable compatibility test.

## Confirmed Local Constraints

Host:

- ThinkPad T480, Intel Core i7-8550U, 4 cores / 8 threads.
- 15.5 GiB RAM visible to libvirt.
- 236.46 GiB root filesystem, about 194.7 GiB available on 2026-07-17.
- EndeavourOS/Arch rolling host, systemd-boot, dracut, and
  `kernel-install-for-dracut`.
- Current kernel entry: `linux-lts 6.18.33-1`.
- `/etc/kernel/cmdline` does not contain `intel_iommu=on`.
- Kernel logs parse the ACPI DMAR table and enable IRQ remapping, but no PCI
  device exposes an `iommu_group` link. VFIO readiness is therefore not proven.
- Host Secure Boot is disabled. That does not prevent an independent guest
  Secure Boot configuration.

Virtualization:

- `qemu:///system` is the existing CTOS authority boundary.
- `ctos-kali` exists and is shut off.
- `ctos-nat`, `ctos-images`, `ctos-snapshots`, and `ctos-iso` are active and
  persistent.
- QEMU 11.0.0, libvirt 12.3.0, virt-manager 5.1.0, and edk2-ovmf 202605 are
  installed locally; the synchronized Arch repositories already advertise
  newer QEMU packages, so a supported full upgrade is required before adding
  VM packages.
- Q35 domain capabilities expose Secure Boot firmware at
  `/usr/share/edk2/x64/OVMF_CODE.secboot.4m.fd`.
- The installed OVMF variable template has no enrolled keys.
- `swtpm` and `virt-firmware` are not installed.
- SPICE USB redirection components are present: `spice-gtk 0.42-5`,
  `usbredir 0.15.0`, and `virt-viewer 11.0-4`.

USB topology:

- Intel Sunrise Point-LP xHCI at `0000:00:14.0` serves internal/ordinary USB.
- Intel JHL6240 Thunderbolt 3 xHCI at `0000:3c:00.0` is the candidate dedicated
  USB-C controller.
- USB buses 3/4 belong to the JHL6240 path and were empty during inspection.
- The locked iPhone did not enumerate. Apple documents that a locked iPhone
  does not communicate with a new wired accessory by default.
- Passing `0000:3c:00.0` through VFIO is not authorized until its IOMMU group
  and physical port mapping are verified after the host preflight reboot.

## Selected Operating System

For the durable baseline, use the current Microsoft Windows 11 x64 ISO and
edition covered by an entitlement that explicitly permits this VM, downloaded
directly from Microsoft's official Windows download page.

As of 2026-07-17, Microsoft labels Windows 11 25H2 as the current downloadable
x64 release. Microsoft lists 25H2 Home/Pro support through 2027-10-12. Do not
pin the implementation to a stale release string: at implementation time,
record the release, filename, size, language, download time, and Microsoft-
published SHA-256 again.

The Microsoft page currently publishes this French x64 SHA-256:

```text
A02693BEB8EB166AFDFDB7DB49176A2B547F81E61030A695FE172277DB6A1977
```

This value is evidence for the 2026-07-17 planning snapshot only. The future
download must be compared with the hash displayed by Microsoft during that
download session; do not accept this recorded hash if Microsoft has changed
the release or filename.

Edition policy:

- The ISO is multi-edition.
- Use Home or Pro only with a license the operator is entitled to use.
- Prefer Pro when a valid Pro license exists; Apple Devices does not require Pro.
- Do not use activation bypasses, unofficial ISOs, modified installers, or
  unsupported Windows 11 requirement bypasses.
- Record the licensing decision before installation. Do not store a product key
  in Git, scripts, shell history, screenshots, or VM metadata.
- Current state: no licence is available, so durable media acquisition and
  installation are blocked.
- Do not substitute Enterprise Evaluation silently. If separately approved,
  keep it disposable, label it non-baseline, and delete/rebuild it before the
  90-day period expires.

## Domain Architecture

Planned identity:

- domain: `ctos-apple-recovery`
- connection: `qemu:///system`
- machine: versioned Q35 selected from current domain capabilities
- firmware: OVMF Secure Boot pflash
- autostart: disabled
- clock: localtime for Windows
- lifecycle: graceful shutdown; hard destroy only through an explicit force path

Resources:

- memory: 8192 MiB, fixed; no balloon-based overcommit during restores
- vCPU: 4, one socket / two cores / two threads or a topology verified against
  the current libvirt model
- CPU mode: `host-model`, validated as Windows-compatible before define
- disk: `/var/lib/libvirt/ctos/images/ctos-apple-recovery.qcow2`
- disk virtual size: 96 GiB, sparse qcow2
- installer ISO: imported into `ctos-iso`, never referenced from `/home`
- driver media: none; use Windows inbox AHCI/SATA and e1000e
- network: one emulated e1000e NIC on `ctos-nat`
- display: SPICE for local console; no RDP listener and no remote exposure
- USB guest controller: qemu-xHCI
- no shared filesystem, no host drive mapping, no inbound port forward

Resource exclusion:

- `ctos-kali` must be shut off before this VM starts.
- Heavy local AI workers should be stopped for install/restore sessions.
- Host free memory and AC power must be checked before start.
- Host and guest suspend must be inhibited for the entire phone restore window.

## UEFI, Secure Boot, And TPM

Windows 11 VM requirements include UEFI/Secure Boot capability, TPM 2.0,
64 GiB storage, at least 4 GiB RAM, and at least two virtual processors. The
planned VM exceeds those resource minima.

Host packages required after a full Arch upgrade:

- `swtpm` from official Arch `extra`;
- `virt-firmware` from official Arch `extra`;
- existing `edk2-ovmf`, `qemu-full`, `libvirt`, and `virt-manager`.

Installation must use a full supported Arch upgrade, conceptually:

```text
sudo pacman -Syu --needed swtpm virt-firmware
```

The next iteration must first review Arch news, the transaction plan, `.pacnew`
files, and reboot requirements. Do not run a partial upgrade.

TPM XML target:

```xml
<tpm model="tpm-crb">
  <backend type="emulator" version="2.0"/>
</tpm>
```

Libvirt must own a private persistent TPM state for this domain. Never pass the
host physical TPM to the guest.

Secure Boot variable-store policy:

- copy the packaged OVMF variable template to libvirt-owned per-domain state;
- use `virt-fw-vars` from the official Arch package to enroll the required
  Microsoft Windows boot certificates and enable Secure Boot;
- include the Microsoft 2011 and 2023 transition certificates and KEKs needed
  by current install media and post-June-2026 updates;
- do not add arbitrary local, distro, option-ROM, or third-party keys unless a
  signed component demonstrably requires one;
- inspect the resulting store with `virt-fw-vars --print` before first boot;
- verify inside Windows with `Confirm-SecureBootUEFI`, `msinfo32`, and `tpm.msc`.

Exact `virt-fw-vars` flags must be selected from the installed 26.x manual at
implementation time. The tool exposes separate 2011/2023 Microsoft DB and KEK
choices; do not copy an older command blindly because Microsoft's 2011 Secure
Boot certificates began expiring in June 2026.

## Windows Drivers

The trusted bootstrap uses only Windows inbox AHCI/SATA and Intel e1000e
drivers. Do not download or attach the community virtio-win ISO, install its
broad guest-tools bundle, add a QEMU Guest Agent channel, or enable a balloon
device. The VM does not need VirtIO performance for Apple firmware recovery.

If a later measured need justifies a `PCI\\VEN_1AF4` device, allow only the
specific driver delivered by Windows Update/Microsoft Update Catalog and
verify the publisher/signature in Windows. That is a separate recorded change,
not an automatic optimization or media fallback.

## Official Apple Software

Install only Apple Devices from Microsoft Store product ID:

```text
9NP83LWLPZ9K
```

The selected reproducible path is:

1. Finish all Windows Updates and reboot until no restart is pending.
2. Verify date/time and Microsoft Store health.
3. Query the Store product and confirm the publisher is Apple Inc.
4. Install Apple Devices from the Store page or the same Store product through
   `winget --source msstore`; this is one official distribution channel, not two
   different packages.
5. Update Microsoft Store apps.
6. Start Apple Devices once with no phone connected.
7. Verify the installed package publisher, version, and Apple device services.
8. Shut down cleanly and create the `apple-ready` baseline.

Do not install iTunes alongside Apple Devices. Apple documents iTunes only for
systems that cannot run the newer apps. If Apple Devices cannot install or run
on this supported Windows 11 VM, stop and diagnose the Store/app requirement;
do not silently fall back to a third-party mirror or old standalone installer.

No Apple Account is required in the VM for recovery-mode factory restore. Do
not sign the owner's Apple Account into Windows or Apple Devices. Activation
Lock is completed on the erased iPhone itself after restore.

## USB-C Handoff Decision

### Preferred: pass the whole JHL6240 xHCI controller

Candidate PCI device:

```text
0000:3c:00.0  Intel JHL6240 Thunderbolt 3 USB 3.1 Controller [8086:15c1]
```

Why this is preferred:

- an iPhone disconnects and re-enumerates during recovery and restore;
- normal, recovery, and other boot states can expose different USB product IDs;
- the guest owns the physical USB port rather than one ephemeral bus/device ID;
- Apple Devices and its Windows driver see the same physical controller across
  the reset sequence;
- the path does not depend on a live SPICE viewer continuing USB redirection.

Mandatory preflight before defining the hostdev:

1. Back up `/etc/kernel/cmdline` with timestamp and permissions preserved.
2. Add only `intel_iommu=on`; do not add `iommu=pt` or ACS override initially.
3. Rebuild the existing dracut/systemd-boot entries with the installed
   `reinstall-kernels` mechanism.
4. Inspect the generated boot entry before reboot.
5. Reboot with explicit operator approval.
6. Confirm `intel_iommu=on` in `/proc/cmdline`.
7. Confirm DMAR without errors and non-empty `/sys/kernel/iommu_groups`.
8. Resolve the complete group containing `0000:3c:00.0`.
9. Reject controller passthrough unless that group is isolated or every member
   is proven to be part of the same disposable USB-C function.
10. Map the physical USB-C port with a non-sensitive test device.
11. Confirm no keyboard, internal camera, Bluetooth, storage, network adapter,
    or host-critical device is lost when the controller is detached.
12. Confirm the laptop remains on AC power and charging while the controller is
    guest-owned.

If the group is not safe, stop. Do not use `pcie_acs_override`, do not split an
unsafe group, and do not bind unrelated bridge/NHI devices merely to force the
design through.

Libvirt target, only after that preflight:

```xml
<hostdev mode="subsystem" type="pci" managed="yes">
  <source>
    <address domain="0x0000" bus="0x3c" slot="0x00" function="0x0"/>
  </source>
</hostdev>
```

`managed="yes"` makes libvirt detach the controller on VM start and reattach it
after guest shutdown. The launcher must refuse start if the device is missing,
already bound elsewhere, or currently carries a host USB child.

### Conditional investigation: SPICE usbredir

SPICE USB redirection is not the default restore path. It is the smallest
explicit investigation if safe PCI isolation fails.

Required proof before acceptance:

- auto-redirect only Apple vendor ID `0x05ac`, any product ID;
- keep `remote-viewer` connected throughout the test;
- demonstrate repeated disconnect/reconnect and changed product IDs without
  manual reselection;
- demonstrate Windows retains the device through a non-destructive recovery-
  mode enter/exit test;
- document host ACL behavior and failure recovery.

If this proof fails, the VM is not approved for phone restore. Use a physical
supported Mac/Windows computer rather than risking a cable drop during flash.

### Rejected USB approaches

- single libvirt USB hostdev by bus/device: bus/device changes on re-enumeration;
- one hard-coded Apple product ID: recovery transitions can change product ID;
- broad redirect of all USB devices: unnecessary host exposure;
- USB hub as a reliability fix: it adds another reset/power failure point;
- recovery/DFU solely for model discovery: no longer needed; model is confirmed;
- ACS override: weakens the isolation evidence required for VFIO.

## Network And Privacy Boundary

The VM needs outbound Internet for Windows Update, Microsoft Store, Apple
Devices updates, and signed iOS firmware downloads.

Policy:

- one NIC on `ctos-nat`;
- no inbound forwarding or bridged LAN presence;
- no shared host folders, clipboard synchronization, drag-and-drop, or USB mass
  storage redirection by default;
- no owner's Apple Account or personal Microsoft account retained in the VM;
- no browser use beyond official Microsoft/Apple verification if required;
- no third-party unlock, jailbreak, driver-download, firmware, or cleanup tool;
- Windows telemetry cannot be eliminated completely; use supported privacy
  settings, not unofficial debloat scripts.

During an actual restore, the Apple firmware cache, Windows device logs, and
Apple driver logs are sensitive generated artifacts. They belong only in the
disposable session layer and are not committed or copied to the host.

## Baseline And Session Model

Do not restore phones directly from the maintenance disk.

Baseline states:

1. `windows-installed`: Windows installation complete, current updates applied,
   Secure Boot and TPM verified, required drivers installed.
2. `apple-ready`: Apple Devices current and opened once, no phone ever attached,
   no personal account, no pending reboot.

Both checkpoints are made only while the domain is cleanly shut off.

Per-phone session:

- create a new qcow2 overlay backed by the immutable `apple-ready` disk;
- create matching disposable copies of the clean NVRAM and TPM state;
- keep the same stable virtual hardware identity required for Windows licensing;
- boot the disposable state, update Windows/Store/Apple Devices, then restore;
- preserve the session until the phone reaches the Hello screen and the owner
  confirms that setup/Activation Lock can proceed;
- destroy the session overlay, session NVRAM, TPM state, cached IPSW, and logs
  only after a separate explicit cleanup confirmation.

Disk-only libvirt snapshots do not capture all NVRAM/TPM state. Therefore the
future helper must treat disk, NVRAM, and TPM state as one consistency unit.
Do not enable BitLocker/device encryption on this recovery VM; verify it remains
off before sealing the baseline. This avoids recovery-key coupling to rolled-
back virtual TPM state. If encryption is later required, redesign the snapshot
model first and store its recovery key outside Git.

Maintenance mode:

- phone physically disconnected;
- boot a writable maintenance layer;
- apply Windows and Store updates;
- verify Secure Boot certificate state, TPM, drivers, Apple Devices, network,
  shutdown, and no pending reboot;
- seal a new versioned `apple-ready` baseline;
- keep the previous baseline until one clean smoke boot passes;
- prune only with explicit confirmation and documented recovery impact.

## Implementation Phases And Gates

### Phase 0 — authorization and prerequisites

- Resolve an entitlement that explicitly covers this Windows VM. Current state:
  blocked because the operator has no licence; Enterprise Evaluation remains a
  separate, unapproved disposable option.
- Confirm official Microsoft ISO language.
- Confirm at least 120 GiB host free space before media/disk creation.
- Confirm `ctos-kali` is shut off.
- Confirm host backup/recovery path and AC power.
- Review current Arch news before the full upgrade.

Gate: no package or boot change until these checks pass.

### Phase 1 — host update and required packages

- Full `pacman -Syu`, including required reboot handling.
- Install `swtpm` and `virt-firmware` in the same supported transaction or after
  the completed full upgrade.
- Verify package signatures, versions, commands, libvirt capabilities, and
  `.pacnew` state.

Gate: libvirt/Kali status must still be healthy after the update.

### Phase 2 — IOMMU and USB-C controller qualification

- Apply the one-parameter boot change described above.
- Rebuild entries, reboot, inventory IOMMU groups, map ports, and detach/reattach
  the empty controller without the phone.

Gate: isolated group, safe port mapping, and host reattachment must all pass.
If not, mark controller passthrough blocked and investigate usbredir separately.

### Phase 3 — media acquisition

- Download Windows ISO only from Microsoft.
- Record release/language/filename/size/SHA-256 and compare with Microsoft.
- Import the Windows ISO into `ctos-iso` through an idempotent repo helper.
- Do not acquire driver media; Windows inbox AHCI/e1000e is the bootstrap.

Gate: mismatched or unavailable hash blocks implementation; no mirror fallback.

### Phase 4 — declarative domain and dry run

- Add repo-owned install and installed XML definitions.
- Add a profile entry and a dedicated `ctos-apple-recovery` lifecycle helper.
- Generate inspected NVRAM and empty private TPM state atomically outside Git;
  create the guest disk only after the entitlement/media gates pass.
- Validate XML with `virt-xml-validate`.
- Compare the expected signature against live defined XML.
- `plan` must show every mutation before `apply`.

Gate: no start until domain diff, storage paths, Secure Boot variables, and TPM
backend are verified.

### Phase 5 — Windows installation

- Phone disconnected.
- Install Windows from verified ISO.
- Use the inbox AHCI/SATA storage and e1000e network drivers; attach no driver ISO.
- Finish setup without entering device-owner Apple credentials.
- Apply Windows updates until no update/reboot remains.
- Verify Device Manager has no unexplained devices.
- Verify Secure Boot, TPM 2.0, activation state, firewall, Defender, clock, and
  `ctos-nat` egress.
- Disable guest sleep/hibernation during AC operation and confirm BitLocker/
  device encryption is off.

Gate: create offline `windows-installed` state only after all checks pass.

### Phase 6 — Apple Devices baseline

- Install Apple Devices from Store product `9NP83LWLPZ9K`.
- Verify publisher/version and update it.
- Open once without a phone.
- Verify no pending reboot and clean shutdown.
- Create the consistent disk/NVRAM/TPM `apple-ready` baseline.

Gate: no iPhone connection before the clean baseline exists.

### Phase 7 — non-sensitive USB validation

- Start a disposable session.
- Pass the qualified USB-C controller.
- Use a non-sensitive USB test device to verify guest-only visibility, unplug/
  replug, controller reset, VM shutdown, and host driver reattachment.
- Confirm host stays charged and responsive.

Gate: any detach, power, reset, or reattach failure blocks phone use.

### Phase 8 — iPhone XS recovery session

Preconditions:

- owner present and authorizes erase;
- iCloud Photos/backups and Apple Account/Activation Lock checked;
- data-loss decision recorded outside the repo without personal identifiers;
- Windows, Apple Devices, host, cable, network, and AC power ready;
- no host/guest pending update or automatic restart;
- direct known-good data-capable USB-C-to-Lightning cable, no hub;
- sleep/shutdown inhibited on host and guest;
- disposable session active.

Recovery sequence from Apple for iPhone 8 or later, including XS:

1. Open Apple Devices.
2. Connect the iPhone to the VM-owned physical port.
3. Press and quickly release Volume Up.
4. Press and quickly release Volume Down.
5. Hold the side button until the connect-to-computer screen appears.
6. Confirm Apple Devices sees the recovery device.
7. If firmware download takes more than 15 minutes and the phone exits recovery,
   let the download complete, then repeat the recovery-button sequence.
8. Stop at the Apple Devices `Restore` confirmation.

Destructive gate:

- State plainly that Restore erases all local information and settings.
- Require the owner's explicit confirmation at that moment.
- Do not choose Update as a passcode-removal mechanism; it does not satisfy the
  forgotten-passcode recovery requirement.

After confirmation:

- select Restore once;
- do not detach USB, close the viewer, suspend either OS, reboot, or change
  network during download/flash/verification;
- wait for Apple Devices completion and the iPhone Hello screen;
- let the owner complete Activation Lock/account setup on the phone;
- do not enter account credentials into the VM.

Cleanup gate:

- preserve the disposable session until the owner confirms the phone is usable;
- then explicitly approve deletion of the session overlay/NVRAM/TPM/log/cache
  unit;
- baseline remains clean and reusable.

## Failure Matrix

### Windows installer cannot see disk

- Stop: the defined SATA/AHCI disk should be supported by Windows inbox.
- Verify the exact XML/disk path and Windows ISO before changing hardware.
- Do not attach unverified driver media or silently switch disk models.

### No network in Windows

- Verify CTOS NAT and host firewall first.
- Verify the emulated e1000e device and Microsoft inbox driver in Device Manager.
- Do not bridge the VM to LAN as a quick workaround.

### Secure Boot reports off or setup mode

- Stop before Apple baseline.
- Inspect OVMF loader, SMM, NVRAM path, PK/KEK/DB, and 2011/2023 certificates.
- Do not bypass Windows requirements.

### TPM emulator unavailable

- Verify `swtpm`, libvirt domain capabilities, and per-domain state permissions.
- Do not pass through the host TPM.

### Apple Devices unavailable in Store

- Verify supported Windows release, Store health, region, time, updates, and the
  exact product ID/publisher.
- The Store GUI and `winget --source msstore` are equivalent access paths to the
  same official package.
- Do not sideload or use third-party download sites.

### Phone absent in normal locked mode

- Expected under Apple's wired-accessory policy.
- Verify cable/port using a non-sensitive device, then enter recovery only at
  the authorized session phase.

### Phone disappears during state transition

- With PCI controller passthrough, inspect Windows USB/controller events and
  Apple Devices; do not move the cable mid-restore.
- With experimental usbredir, failure invalidates that path for restore.

### Firmware download exceeds 15 minutes

- Let the download finish.
- Re-enter recovery mode as Apple directs.
- Do not restart the download blindly or change USB ownership.

### Apple restore error

- Record only the numeric error and non-sensitive timing/state.
- Follow the matching Apple support path.
- Check direct cable, port, network, current Windows/Apple Devices, and service
  requirements before retrying.
- Do not use jailbreak/unlock/firmware tools.

### Activation Lock appears

- Expected when Find My was enabled.
- Owner enters the Apple Account on the phone.
- The VM does not bypass Activation Lock and does not retain those credentials.

### Host loses the USB-C controller after VM shutdown

- Do not reconnect the phone.
- Verify domain stopped and libvirt attempted managed reattach.
- Inspect driver binding and PCI state.
- A host reboot is an explicit recovery action, never an automatic fallback.

## Repo Deliverables For The Next Iteration

Planned files:

- `libvirt/domains/ctos-apple-recovery.install.xml`
- `libvirt/domains/ctos-apple-recovery.xml`
- `libvirt/profiles/ctos-vms.json` update
- `scripts/ctos-apple-recovery`
- optional narrowly scoped host IOMMU installer with backup/plan/apply/status
- `docs/APPLE_RECOVERY_VM.md` operator runbook
- context state document after each applied phase

The helper should expose at least:

- `status` / `status --json`
- `plan`
- `apply-infra`
- `prepare-secure-state`
- `verify-media`
- `define`
- `start-maintenance`
- `seal-baseline`
- `start-session`
- `usb-preflight`
- `open-console`
- `shutdown`
- `close-session` with explicit deletion confirmation

It must refuse:

- concurrent `ctos-kali` execution;
- start with insufficient RAM/disk or no AC power;
- controller passthrough without verified group/port state;
- phone restore from maintenance/base state;
- snapshot or cleanup while running;
- cleanup before explicit success confirmation;
- arbitrary domains, PCI addresses, USB vendors, shell commands, or media paths.

## Verification Checklist

Host:

- full update completed and rebooted if required;
- no libvirt regression; Kali remains defined and healthy;
- non-empty IOMMU groups after preflight boot;
- candidate controller group and port mapping recorded;
- managed detach/reattach tested with no phone;
- host AC charging survives guest ownership.

Media:

- Microsoft URL/release/language/filename/size/hash recorded;
- ISO hash matches Microsoft's current page;
- Windows ISO imported into `ctos-iso` and path verified;
- no community VirtIO or other driver ISO attached.

VM:

- XML validates;
- Q35/UEFI/Secure Boot/SMM active;
- Microsoft 2011+2023 transition keys inspected;
- TPM 2.0 present and ready;
- Windows supported/current with no pending reboot;
- only required signed drivers installed;
- Defender/firewall active;
- BitLocker/device encryption off;
- no shares, inbound listener, owner account, or phone data in baseline.

Apple:

- Store product ID and Apple publisher verified;
- Apple Devices current and starts cleanly;
- clean `apple-ready` consistency set sealed offline;
- USB test survives detach/reconnect and host recovery;
- iPhone recovery detection proven before destructive confirmation.

## Explicit Next Goal

Suggested goal objective:

```text
Implement the researched ctos-apple-recovery Windows 11 VM through the clean
apple-ready baseline and non-sensitive USB-C validation, following
context/23_windows_apple_recovery_vm_plan.md. Stop before connecting the iPhone
or entering recovery mode unless I explicitly extend the goal.
```

This separates infrastructure construction from the destructive phone session.
The first implementation goal should end with a verified, clean baseline and a
tested USB controller; the owner-authorized iPhone restore should be a distinct
goal/approval window.

## Primary Sources

Microsoft:

- Windows 11 ISO/current release and hashes:
  https://www.microsoft.com/en-us/software-download/windows11
- Windows 11 VM requirements:
  https://learn.microsoft.com/en-us/windows/whats-new/windows-11-requirements
- Windows 11 Home/Pro lifecycle:
  https://learn.microsoft.com/en-us/lifecycle/products/windows-11-home-and-pro
- Windows 11 release health:
  https://learn.microsoft.com/en-us/windows/release-health/windows11-release-information
- Secure Boot certificate transition:
  https://support.microsoft.com/en-US/servicing/os/secure-boot/2025/06/windows-secure-boot-certificate-expiration-and-ca-updates
- Secure Boot key guidance:
  https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/windows-secure-boot-key-creation-and-management-guidance?view=windows-11

Apple:

- Apple Devices for Windows:
  https://support.apple.com/en-lamr/guide/devices-windows/mchl5ded2763/windows
- Official Apple Windows downloads:
  https://support.apple.com/en-us/118290
- Factory restore warning and procedure:
  https://support.apple.com/en-us/118107
- Recovery-mode procedure:
  https://support.apple.com/en-us/118106
- Forgotten-passcode procedure:
  https://support.apple.com/en-ie/118430
- Windows recognition/cable troubleshooting:
  https://support.apple.com/en-gb/108643?device-type=windows-pc
- Locked wired-accessory policy:
  https://support.apple.com/fr-fr/111806

Virtualization/Arch:

- Libvirt domain/hostdev/TPM format:
  https://libvirt.org/formatdomain.html
- Libvirt snapshot semantics:
  https://libvirt.org/formatsnapshot.html
- ArchWiki libvirt/Windows/TPM guidance:
  https://wiki.archlinux.org/title/Libvirt
- ArchWiki PCI passthrough guidance:
  https://wiki.archlinux.org/title/PCI_passthrough_via_OVMF
- Arch full-upgrade requirement:
  https://wiki.archlinux.org/index.php/Package_Management_FAQs
- Arch `swtpm` package:
  https://archlinux.org/packages/extra/x86_64/swtpm/
- Arch `virt-firmware` package:
  https://archlinux.org/packages/extra/any/virt-firmware/
- `virt-fw-vars` manual:
  https://man.archlinux.org/man/extra/virt-firmware/virt-fw-vars.1.en
- virtio-win stable packaging/signature policy:
  https://github.com/virtio-win/virtio-win-pkg-scripts/blob/master/README.md
