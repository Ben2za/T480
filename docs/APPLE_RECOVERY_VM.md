# CTOS Apple Recovery Windows VM

This runbook builds and operates `ctos-apple-recovery`, a Windows 11 virtual
workstation for Apple's official Apple Devices application. It is intentionally
split into two authorization windows:

1. build a clean Apple-ready baseline and validate USB-C with a non-sensitive
   peripheral;
2. only in a later, explicit session, connect an owner-authorized iPhone and
   approve any destructive Restore action.

The first window never connects the iPhone to the VM, enters recovery/DFU,
attempts a passcode, reads phone data, erases the phone, or restores it.

## Trust and isolation model

- Host authority: `qemu:///system` only.
- Guest: current Windows 11 x64 from Microsoft, with an entitlement that
  explicitly covers this VM. The recorded French 25H2 consumer ISO is not an
  installation authorization.
- Hardware: `pc-q35-11.0`, 4 vCPU, 8192 MiB fixed RAM, 96 GiB qcow2.
- Firmware: OVMF Secure Boot with explicit Microsoft 2011 and 2023 transition
  certificates; private emulated TPM 2.0.
- Bootstrap drivers: Windows inbox AHCI/SATA and Intel e1000e.
- Network: `ctos-nat`; no bridge, inbound forward, shared folder, clipboard,
  file transfer, USB redirection, audio, QEMU Guest Agent, or autostart.
- Apple software: Microsoft Store product `9NP83LWLPZ9K`, publisher Apple Inc.
- USB: whole JHL6240 xHCI `0000:3c:00.0` only after real IOMMU isolation and
  detach/reattach tests; never use an ACS override.
- State: clean offline baseline plus complete disposable disk/NVRAM/TPM units.

The community virtio-win ISO is not used. Its stable repository and RPM are
unsigned, its repository declares `gpgcheck=0`, and the ISO has no
supplier-published SHA-256. Optional `PCI\\VEN_1AF4` drivers are allowed only
when delivered and validated by Windows Update/Microsoft Update Catalog.

## Repo-owned controls

```text
scripts/ctos-apple-host
scripts/ctos-apple-recovery
libvirt/domains/ctos-apple-recovery.install.xml
libvirt/domains/ctos-apple-recovery.xml
libvirt/profiles/ctos-vms.json
context/24_windows_apple_recovery_vm_state.md
```

Generated ISO files, disks, varstores, TPM state, logs, caches, and device data
remain outside Git.

## 1. Host package and boot preflight

The coherent Arch package transaction must already be complete. Confirm:

```bash
pacman -Q qemu-full libvirt edk2-ovmf swtpm virt-firmware
pacman -Qu
scripts/ctos-apple-host status
scripts/ctos-apple-host plan
```

Required gates:

- AC power online;
- `ctos-kali` shut off;
- no Apple vendor `05ac` USB device;
- no Type-C partner in `source` or `host` role on the candidate controller;
- no `pcie_acs_override` configured or active.

Important local detail: a locked iPhone can be present as
`/sys/class/typec/port1-partner` even when `lsusb` has no Apple device. Physically
unplug it before continuing. Keep the charger on the separate `sink/device`
port.

Apply the single boot parameter only from a visible local terminal:

```bash
sudo /home/operator/T480/scripts/ctos-apple-host apply-iommu
```

The helper:

- creates a timestamped metadata-preserving backup of `/etc/kernel/cmdline`;
- adds exactly one `intel_iommu=on` and refuses conflicts/duplicates;
- runs `reinstall-kernels`;
- inspects at least two kernel entries;
- never reboots or detaches PCI automatically.

Read its output before an explicit reboot. A recovery entry and the original
cmdline backup must exist. Then reboot deliberately from the host UI or a local
terminal.

After reboot:

```bash
scripts/ctos-apple-host status
scripts/ctos-apple-host verify-iommu
virt-host-validate qemu
```

The controller qualifies only if the running kernel has exactly one
`intel_iommu=on`, IOMMU groups are non-empty, `0000:3c:00.0` has the expected
Intel `8086:15c1` xHCI identity, and its complete group contains no other
device. A bridge, Thunderbolt NHI, or any host-critical member blocks this
path. Do not add an ACS override.

## 2. Resolve licensing before acquiring media

The operator confirmed on 2026-07-17 that no Windows licence is available for
this VM. Continue host and repository preparation, but stop before importing
media, creating a durable guest disk, or installing Windows.

For a durable baseline, first identify an entitlement that expressly permits
running and accessing this local Windows VM. Do not assume that a Windows OEM
licence on another computer provides virtualization rights. Record only the
entitlement type and decision; never record its key or account credential.

Microsoft separately offers Windows 11 Enterprise 25H2 Evaluation:

- official Evaluation Center ISO, French x64 available;
- no product key, 90-day evaluation;
- intended for IT evaluation and requires a Microsoft account;
- after expiration, persistent warnings and hourly shutdown;
- never eligible for `seal-baseline` in this workflow.

Creating that disposable test VM requires explicit operator approval. Its ISO,
hash, disk, NVRAM, TPM state, domain name, and deletion deadline must be kept
separate from the durable profile. Do not reuse the consumer-media allowlist
below for an Evaluation ISO.

Selecting “I don't have a product key” is not the selected workaround.
Microsoft documents it as a first-install path followed by purchase of a
digital licence from Microsoft Store. The repo therefore keeps both the
durable entitlement and Evaluation statuses blocked; it contains no generic
key, activation bypass, KMS workaround, or rearm path.

## 2a. Acquire durable Microsoft media after entitlement resolution

Use only:

```text
https://www.microsoft.com/fr-fr/software-download/windows11
```

Select:

- Windows 11 multi-edition ISO for x64;
- French;
- current file `Win11_25H2_French_x64_v2.iso`.

Microsoft download links expire after 24 hours. Do not save or reuse an old
signed CDN URL, and do not use a mirror. Verify before import:

```bash
sha256sum /home/operator/Downloads/Win11_25H2_French_x64_v2.iso
```

Expected SHA-256 as published for French 25H2 on 2026-07-17:

```text
a02693beb8eb166afdfdb7db49176a2b547f81e61030a695fe172277db6a1977
```

Recheck the live Microsoft page if the release or filename changes. Do not copy
the ISO manually or weaken pool permissions. After a durable entitlement is
explicitly recorded, import it from a visible local root terminal:

```bash
chmod go-w /home/operator/Downloads/Win11_25H2_French_x64_v2.iso
sudo /home/operator/T480/scripts/ctos-apple-recovery import-media \
  --source /home/operator/Downloads/Win11_25H2_French_x64_v2.iso
/home/operator/T480/scripts/ctos-apple-recovery verify-media
```

`import-media` checks the entitlement before it accesses the source. It then
requires a canonical operator-owned single-link file with the exact basename,
re-hashes the open source before and after copying, hashes its staging copy,
publishes without replacement, records a strict managed attestation, refreshes
`ctos-iso`, and verifies the exact libvirt volume path. An exact prior import is
idempotent. A different target or attestation is preserved and blocks; there is
no overwrite or silent cleanup.

With the current `blocked-no-eligible-vm-entitlement` state, the import command
must fail before source access. You can still run the read-only verifier:

```bash
scripts/ctos-apple-recovery verify-media
```

A missing or different hash is a hard stop. There is no media fallback.

## 3. Review and define the install domain

```bash
scripts/ctos-apple-recovery status
scripts/ctos-apple-recovery plan
scripts/ctos-apple-recovery apply-infra
sudo /home/operator/T480/scripts/ctos-apple-recovery prepare-secure-state
scripts/ctos-apple-recovery define --profile install
virt-xml-validate libvirt/domains/ctos-apple-recovery.install.xml domain
virsh -c qemu:///system --readonly dumpxml --inactive ctos-apple-recovery
```

`prepare-secure-state` resolves the installed service accounts by name and
creates only canonical pre-install state: root `root:libvirt 0751`, NVRAM
`libvirt-qemu:libvirt 0640`, an empty TPM directory `tss:libvirt 0750`, and
attestation `root:libvirt 0640`. If the operator's current login does not yet
have effective `libvirt` group membership, re-login after the pending host
reboot; do not loosen these modes.

`plan` must show every intended mutation. Before `define`, confirm the phone is
absent, media hash is exact, RAM/storage/AC gates pass, Kali is off, TPM emulator
support is present, and a dedicated NVRAM was generated with the expected
Microsoft certificates. The install/maintenance XML contains no PCI hostdev.

The first definition creates only allowlisted state below the CTOS pools. It
must not start Windows implicitly.

## 4. Install Windows 11

The Windows edition must match an entitlement that explicitly covers this VM.
Do not enter a product key into scripts, chat, logs, or repository files. With
the current `blocked-no-eligible-vm-entitlement` profile state, `define`, guest
start, console access, and Windows installation must refuse to proceed.

Start visibly:

```bash
scripts/ctos-apple-recovery start-maintenance --profile install
scripts/ctos-apple-recovery open-console
```

Installation rules:

- phone physically disconnected;
- accept only the verified Microsoft ISO;
- select the licensed edition;
- install to the 96 GiB SATA disk;
- do not load or run any driver ISO;
- do not enter an Apple Account;
- do not use a personal Microsoft account for the reusable baseline;
- let Windows Setup complete all required reboots before detaching the ISO.

After the desktop appears, run Windows Update repeatedly until no update or
reboot remains. Do not install optional preview updates. Device Manager must
have no unexplained device, and the storage/network devices must use Microsoft
inbox or Microsoft Update-delivered drivers.

The install-to-maintenance transition is implemented and fail-closed. It
requires authenticated guest evidence, an ACPI-shutdown receipt, fresh
NVRAM/TPM/disk attestations, and an unchanged pre-install blank-disk
provenance record. The live transition remains unavailable until a licensed
Windows entitlement and a safe USB partner gate are present. Do not edit live
domain or attestation JSON by hand to bypass these gates.

From an elevated PowerShell window, collect the non-sensitive baseline checks:

```powershell
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsBuildNumber
Confirm-SecureBootUEFI
Get-Tpm | Select-Object TpmPresent, TpmReady, ManufacturerIdTxt, SpecVersion
Get-NetFirewallProfile | Select-Object Name, Enabled, DefaultInboundAction
Get-MpComputerStatus | Select-Object AntivirusEnabled, RealTimeProtectionEnabled, AntivirusSignatureLastUpdated
Get-BitLockerVolume | Select-Object MountPoint, VolumeStatus, ProtectionStatus
powercfg /a
```

Required results:

- supported Windows 11 25H2 build;
- Secure Boot `True`;
- TPM present and ready, specification 2.0;
- firewall and Defender active/current;
- no pending reboot or Windows Update;
- BitLocker/device encryption off for reproducible disk/NVRAM/TPM session
  handling;
- sleep and hibernation disabled while on AC.

Disable hibernation and AC sleep from elevated PowerShell:

```powershell
powercfg /hibernate off
powercfg /change standby-timeout-ac 0
powercfg /change monitor-timeout-ac 0
```

Shut down Windows cleanly. Do not seal a running or hibernated state.

## 5. Install and verify Apple Devices

Apple directs Windows users to Microsoft Store. Use only the Store source and
the exact product ID. In a non-elevated PowerShell session:

```powershell
winget source list
winget show 9NP83LWLPZ9K --source msstore
winget install 9NP83LWLPZ9K --source msstore --accept-source-agreements --accept-package-agreements --disable-interactivity
```

`--disable-interactivity` is intentional: if Microsoft Store requires personal
account interaction, installation fails and the workflow stops for an explicit
identity decision. Do not sideload an Appx/MSIX or use a third-party download.

Verify the installed package:

```powershell
Get-AppxPackage -Name 'AppleInc.AppleDevices*' |
  Select-Object Name, Publisher, Version, PackageFamilyName, Status
```

Expected identity:

- product: Apple Devices;
- publisher: Apple Inc.;
- package family: `AppleInc.AppleDevices_nzyj5cx40ttqa`;
- product ID: `9NP83LWLPZ9K`.

Open Apple Devices once with no phone, verify it starts, close it, complete any
Store/Windows updates, then shut down Windows cleanly.

## 6. Seal the Apple-ready consistency set

This operation is prohibited for Enterprise Evaluation or any unlicensed guest.
It requires a recorded eligible durable entitlement and activated Windows.

```bash
scripts/ctos-apple-recovery status
scripts/ctos-apple-recovery seal-baseline
```

The operation must refuse a running/managed-saved domain, block job, Apple USB
device, Type-C source/host partner, inconsistent state, missing verification,
or arbitrary path. The baseline unit contains disk, NVRAM, TPM state, and a
manifest together. It contains no phone identifier or account credential.

Do not use libvirt disk-only snapshots for this Windows baseline. Disk, NVRAM,
and TPM state must remain consistent.

## 7. Non-sensitive USB-C qualification

Use a removable, non-sensitive USB peripheral. Never substitute the iPhone.

The sequence is deliberately two-stage:

1. host-only detach/reattach of the empty qualified controller;
2. managed controller ownership in a disposable VM session.

Before each stage confirm the phone is absent, the test peripheral is removed,
AC charging is stable, and buses 3/4 contain no unexpected child. The helper
must refuse any IOMMU group drift or Type-C source/host partner.

Then:

```bash
scripts/ctos-apple-recovery usb-preflight
scripts/ctos-apple-recovery start-session
scripts/ctos-apple-recovery open-console
```

Insert the non-sensitive peripheral into the mapped recovery port and verify:

- it is visible only inside Windows while the controller is assigned;
- unplug/replug and re-enumeration work;
- the host remains powered, charged, and responsive;
- Windows shuts down cleanly;
- libvirt reattaches `0000:3c:00.0` to `xhci_hcd`;
- USB buses 3/4 return on the host without an error.

Any detach, reset, power, re-enumeration, or reattach failure blocks phone use.
Do not try usbredir or ACS override as an automatic workaround.

Close a failed disposable session without declaring success. Successful
session deletion requires its exact allowlisted identifier and explicit
confirmation:

```bash
scripts/ctos-apple-recovery close-session
```

## 8. Later iPhone restore window

The iPhone restore is a separate goal and authorization window. Before it:

- verify iCloud Photos/backups and existing computer backups;
- confirm access to the linked Apple Account and Activation Lock;
- have the owner present and explicitly accept uncovered data loss;
- ensure current Windows, Apple Devices, AC power, cable, network, and the
  tested controller path;
- start from a disposable Apple-ready session.

Apple's Restore confirmation erases local information and settings. Stop at
that confirmation until the owner gives explicit approval. Never use this VM
for brute force, passcode bypass, jailbreak, Activation Lock bypass, data
extraction, or third-party firmware tools.

## Recovery and rollback

- Failed `intel_iommu=on` boot: select the known recovery kernel entry and
  restore the timestamped `/etc/kernel/cmdline` backup from a local root
  session; run `reinstall-kernels` again.
- Controller absent after shutdown: do not connect the phone. Confirm the VM
  is off, inspect driver binding, and reattach through the allowlisted helper.
  A host reboot is an explicit recovery action, never an automatic fallback.
- Secure Boot off/setup mode: discard the untrusted maintenance varstore,
  regenerate it from the packaged OVMF template with explicit Microsoft
  2011+2023 keys, inspect it, and redefine before starting Windows.
- Microsoft ISO hash mismatch: delete/quarantine only the exact failed
  download and regenerate a link from Microsoft. Do not import it.
- Apple Devices Store failure: verify time, region, Store registration,
  Windows Update, and product ID. Do not sideload or fall back to iTunes while
  the official path has not been explicitly reassessed.

Durable implementation state and unresolved gates are tracked in
`context/24_windows_apple_recovery_vm_state.md` and
`context/04_open_questions.md`.
