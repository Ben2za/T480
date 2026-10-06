# Source Registry

Sources consulted for project setup and future decisions.

## 2026-07-17

### Windows 11 Apple recovery VM architecture

Question:

How should the T480 host a reusable, supported Windows VM that uses official
Apple software to restore an iPhone XS without weakening the host boundary or
risking USB loss during recovery-state transitions?

Sources, accessed 2026-07-17:

- Microsoft Windows 11 ISO/current release and published hashes:
  https://www.microsoft.com/en-us/software-download/windows11
- Microsoft Windows 11 VM requirements:
  https://learn.microsoft.com/en-us/windows/whats-new/windows-11-requirements
- Microsoft Windows 11 lifecycle and release health:
  https://learn.microsoft.com/en-us/lifecycle/products/windows-11-home-and-pro
  https://learn.microsoft.com/en-us/windows/release-health/windows11-release-information
- Microsoft Windows 11 Enterprise Evaluation terms and media:
  https://www.microsoft.com/en-us/evalcenter/evaluate-windows-11-enterprise
- Microsoft Windows 11 virtual-desktop licensing guidance:
  https://www.microsoft.com/licensing/guidance/Windows-11-Licensing-for-Virtual-Desktops
- Microsoft Windows activation and Store administration:
  https://support.microsoft.com/en-us/windows/activation/activate-windows
  https://learn.microsoft.com/en-us/windows/configuration/store/
- Microsoft 2026 Secure Boot certificate transition and key guidance:
  https://support.microsoft.com/en-US/servicing/os/secure-boot/2025/06/windows-secure-boot-certificate-expiration-and-ca-updates
  https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/windows-secure-boot-key-creation-and-management-guidance?view=windows-11
- Apple Devices installation and official Windows distribution:
  https://support.apple.com/en-lamr/guide/devices-windows/mchl5ded2763/windows
  https://support.apple.com/en-us/118290
- Apple restore, recovery mode, and cable recognition:
  https://support.apple.com/en-us/118107
  https://support.apple.com/en-us/118106
  https://support.apple.com/en-gb/108643?device-type=windows-pc
- Libvirt domain hostdev/TPM and snapshot semantics:
  https://libvirt.org/formatdomain.html
  https://libvirt.org/formatsnapshot.html
- Arch libvirt, PCI passthrough, full-upgrade, and official package guidance:
  https://wiki.archlinux.org/title/Libvirt
  https://wiki.archlinux.org/title/PCI_passthrough_via_OVMF
  https://wiki.archlinux.org/index.php/Package_Management_FAQs
  https://archlinux.org/packages/extra/x86_64/swtpm/
  https://archlinux.org/packages/extra/any/virt-firmware/
  https://man.archlinux.org/man/extra/virt-firmware/virt-fw-vars.1.en
- Upstream stable virtio-win packaging and signature policy:
  https://github.com/virtio-win/virtio-win-pkg-scripts/blob/master/README.md
- Upstream virtio-win repository configuration and unresolved checksum issue:
  https://fedorapeople.org/groups/virt/virtio-win/virtio-win.repo
  https://github.com/virtio-win/virtio-win-pkg-scripts/issues/108
- Microsoft Update Catalog search for signed Red Hat `PCI\\VEN_1AF4` drivers:
  https://www.catalog.update.microsoft.com/Search.aspx?q=PCI%5CVEN_1AF4
- Libvirt Secure Boot and current domain capability semantics:
  https://www.libvirt.org/kbase/secureboot.html
  https://libvirt.org/formatdomaincaps.html
- Current Arch news reviewed before the full upgrade:
  https://archlinux.org/news/
  https://archlinux.org/news/iptables-now-defaults-to-the-nft-backend/
  https://archlinux.org/news/active-aur-malicious-packages-incident/

Local evidence:

- The live Microsoft connector returned French SKU `20050` and current filename
  `Win11_25H2_French_x64_v2.iso`; the signed CDN-link step rejected automation,
  so download is delegated to the same official page in Firefox.
- Intel Core i7-8550U, 8 logical CPUs, 15.5 GiB RAM.
- About 194.7 GiB available in the CTOS pools/filesystem.
- `ctos-kali` shut off; CTOS network and pools active.
- After the coherent 2026-07-17 Arch upgrade, QEMU is `11.0.2-3`, libvirt is
  `12.5.0-1`, `swtpm` is `0.10.1-2`, and `virt-firmware` is `26.7.1-1`.
- Q35 capabilities expose Secure Boot OVMF and TPM emulator 2.0. The packaged
  variable template has no enrolled keys, so a dedicated varstore was generated
  in `/tmp` and verified to contain Microsoft 2011 and 2023 KEK, Windows, UEFI,
  and Option ROM certificates with Secure Boot enabled. The temporary varstore
  was explicitly removed after inspection.
- ACPI DMAR and IRQ remapping are active, but no PCI `iommu_group` links exist;
  `/etc/kernel/cmdline` lacks `intel_iommu=on`.
- Candidate dedicated USB-C controller: JHL6240 xHCI `0000:3c:00.0`.
- The locked iPhone is currently visible as a Type-C `source/host` partner on
  that controller despite having no `lsusb` child. It must be unplugged before
  any controller detach or reboot qualification.
- SPICE/usbredir components are already installed but are not selected as the
  unproven primary restore path.
- The community virtio-win `0.1.285-1` ISO has no upstream SHA-256, signed RPM,
  signed repository metadata, or independent GPG trust path. Its drivers are
  Microsoft-attestation-signed, but the transport artifact is not an acceptable
  installation root under this repo's provenance gate.
- The operator confirmed that no Windows licence is available for the VM.
  Microsoft's current Enterprise Evaluation is Windows 11 25H2 x64/Arm64,
  includes French, requires registration and a Microsoft account, needs no
  product key, lasts 90 days, and shuts down hourly after expiry. Microsoft
  describes it as IT evaluation software, so it is not the durable baseline.
- Microsoft's activation page allows “I don't have a product key” during a
  first installation, then directs the user to Microsoft Store to purchase a
  digital licence. This is not evidence of a free durable entitlement. The
  same page requires either a digital licence or a product key for activation.
- Microsoft's virtualization guidance says an OEM Windows licence typically
  does not include VM rights and lists the commercial entitlements that do.
  The exact entitlement must therefore be established before durable install;
  activation alone is not treated as proof of virtualization rights.
- Libvirt documents that an explicit emulator TPM `<source>` makes the operator
  responsible for preventing state reuse across VMs. The helper therefore
  fixes one domain/path, stages NVRAM/TPM/attestation together, and refuses an
  existing partial state rather than overwriting it.
- Independent scaffold review identified missing code enforcement for licence,
  Type-C, live XML drift, Secure Boot evidence, and USB qualification. The
  corrected helper now enforces those live invariants; unfinished
  import/transition/session/seal/cleanup paths remain unavailable. Verification
  result: 46 combined tests, two libvirt XML validations, Python compilation,
  JSON parse, and diff check passed.
- A follow-up adversarial XML review proved that valid nested `serial/log`,
  SPICE `gl`, and interface `rom` nodes could bypass a field-only signature.
  The final signature therefore recursively allowlists device-child tags while
  tolerating only the small libvirt-generated structural set; negative tests
  also cover nested video acceleration and TPM encryption drift.
- Local account/config inspection found libvirt's packaged QEMU identity
  `libvirt-qemu`, swtpm identity `tss`, and operator group `libvirt`; no `swtpm`
  account exists. `/etc/libvirt/qemu.conf` retains the corresponding defaults
  with dynamic ownership and owner restoration enabled. Secure pre-install
  state therefore uses names resolved at runtime and exact ownership/modes:
  root `root:libvirt 0751`, NVRAM `libvirt-qemu:libvirt 0640`, empty TPM
  directory `tss:libvirt 0750`, and attestation `root:libvirt 0640`.
- The lifecycle helper now implements but does not authorize the future
  consumer-ISO import. `import-media` refuses before source access unless the
  exact durable entitlement, host, infrastructure, and XML gates pass; then it
  performs source/destination re-hashing, no-replace publication, a strict
  `root:libvirt 0640` attestation, pool refresh, and exact volume-path check.
  Unit tests cover root/entitlement ordering, a successful atomic import,
  idempotent recovery, and incompatible-target preservation.

Conclusion:

Implement a Windows 11 25H2 x64 Q35 VM with 8 GiB RAM, 4 vCPU, 96 GiB sparse
disk, UEFI Secure Boot, a private TPM 2.0 emulator, CTOS NAT, and Apple Devices
only from Microsoft Store product `9NP83LWLPZ9K`. Bootstrap with Windows inbox
AHCI/SATA and Intel e1000e drivers; do not import the unauthenticated community
VirtIO ISO. Optional `PCI\\VEN_1AF4` drivers may be introduced later only
through Windows Update/Microsoft Update Catalog, after publisher/signature
verification.
Prefer whole-controller passthrough for the JHL6240 USB-C xHCI so iPhone USB
re-enumeration remains inside Windows. This remains conditional on an explicit
`intel_iommu=on` reboot proving a safe isolated group and host charging/reattach.
Reject ACS override. If isolation fails, treat SPICE Apple-VID auto-redirection
as a separate test that must survive non-destructive re-enumeration before use.
Keep a clean offline baseline and per-phone disposable disk/NVRAM/TPM state.
The complete plan is `context/23_windows_apple_recovery_vm_plan.md`. Host and
domain scaffolding and implementation may proceed without a Windows licence,
but live media import, guest installation, and baseline sealing remain gated.
An official Enterprise
Evaluation may be built only as an explicitly authorized disposable 90-day
compatibility test, never as the reusable baseline.

### Personal iPhone forgotten-passcode recovery

Question:

What owner-authorized recovery path has the best chance of preserving family
photos when an iPhone is in a 15-minute Security Lockout and its passcode is
forgotten?

Sources, accessed 2026-07-17:

- Apple, Security Lockout/on-device reset:
  https://support.apple.com/en-ie/105090
- Apple, forgotten passcode and recovery-mode restore:
  https://support.apple.com/en-ie/118430
- Apple, temporary previous-passcode reset on iOS 17 or later:
  https://support.apple.com/en-au/105039
- Apple Platform Security, passcodes, Secure Enclave, delays, and optional
  erase-after-failed-attempts behavior:
  https://support.apple.com/en-lamr/guide/security/sec20230a10d/web
- Apple, iCloud Backup contents:
  https://support.apple.com/en-us/108770
- Apple, iCloud Photos behavior:
  https://support.apple.com/en-us/108782
- Apple, locating local iPhone backups:
  https://support.apple.com/en-us/108809
- Apple, trusted-computer requirements:
  https://support.apple.com/en-euro/109054
- Apple, Activation Lock:
  https://support.apple.com/en-ie/108794

Conclusion:

Stop guessing passcodes. If the passcode changed within 72 hours and the phone
runs iOS 17 or later, use `Forgot Passcode?` and the previous passcode. In all
other Apple-supported cases, regaining access requires erasing the phone.
Before erasure, verify iCloud Photos, the last iCloud Backup, and existing
Finder/Apple Devices/iTunes backups, and confirm access to the Apple Account
linked by Activation Lock. A newly connected Linux/Mac/Windows computer cannot
create a trusted backup from the locked phone because establishing trust
requires the device passcode. Do not install or run passcode-bypass,
brute-force, or forensic tools.

### Locked iPhone USB-C identification

Question:

Can the T480 identify a likely iPhone X over USB-C without unlocking, pairing,
entering recovery mode, or modifying either device?

Sources, accessed 2026-07-17:

- Apple, wired-accessory access while locked:
  https://support.apple.com/fr-fr/111806
- Apple, finding the physical model number:
  https://support.apple.com/en-us/106343
- Apple, iPhone model catalogue:
  https://support.apple.com/en-asia/108044

Local evidence:

- Intel Sunrise Point-LP and JHL6240 Thunderbolt 3 USB xHCI controllers use
  `xhci_hcd`.
- USB buses 3 and 4 exist as the Thunderbolt/USB-C root hubs but have no child.
- `lsusb -d 05ac: -v` returned no Apple device.
- The last 30 minutes of kernel events contained no Apple/USB connection event.
- No `usbguard` executable or service was found; no `usbmuxd` service exists.

Conclusion:

The host USB-C path is present, but the phone has not enumerated at the USB
layer. Apple documents that locked devices do not communicate with wired
accessories by default, so installing `usbmuxd` or another user-space tool
cannot reveal a device that the kernel never sees. Do not use recovery/DFU only
for identification because that changes the phone's boot state and conflicts
with data-preservation priority. For an iPhone 8 or later with a SIM tray, read
the `Axxxx` model number inside the slot on the upper/display side. An iPhone X
is `A1865`, `A1901`, or `A1902`; avoid collecting the IMEI printed on the tray.

## 2026-05-04

### Codex project instructions

Question:

What file should be used to configure Codex behavior for this repository, and how should detailed context be organized?

Sources:

- OpenAI Codex AGENTS.md docs: https://developers.openai.com/codex/guides/agents-md
- OpenAI Codex config basics: https://developers.openai.com/codex/config-basic
- OpenAI Codex sample config: https://developers.openai.com/codex/config-sample
- OpenAI Codex hooks docs: https://developers.openai.com/codex/hooks
- OpenAI Codex skills docs: https://developers.openai.com/codex/skills
- OpenAI `agents.md` repository: https://github.com/openai/agents.md
- OpenAI Codex repository AGENTS.md example: https://github.com/openai/codex/blob/main/AGENTS.md

Conclusion:

Use root `AGENTS.md` for short, durable instructions. Put detailed working memory in `context/`. Avoid large instruction files because Codex project-doc loading has a configured size limit by default.

### T480 VS Code and Codex installation

Question:

What should be installed on EndeavourOS/Arch for VS Code and OpenAI Codex?

Sources:

- Microsoft VS Code Linux setup: https://code.visualstudio.com/docs/setup/linux
- Microsoft VS Code download page: https://code.visualstudio.com/download
- AUR `visual-studio-code-bin`: https://aur.archlinux.org/packages/visual-studio-code-bin
- ArchWiki Visual Studio Code: https://wiki.archlinux.org/title/Visual_Studio_Code
- OpenAI Codex GitHub README: https://github.com/openai/codex
- npm `@openai/codex`: https://www.npmjs.com/package/%40openai/codex
- Visual Studio Marketplace OpenAI Codex extension: https://marketplace.visualstudio.com/items?itemName=OpenAI.chatgpt

Conclusion:

Install `visual-studio-code-bin` through AUR for the official Microsoft binary, `nodejs`/`npm` from Arch repositories, Codex CLI through npm global install, and the official VS Code extension `OpenAI.chatgpt`.

### OpenAI Docs MCP note

Question:

Is the OpenAI Docs MCP available in this session?

Result:

No MCP documentation resources were exposed by the local tool context. Fallback browsing was restricted to official OpenAI domains for OpenAI/Codex documentation, then GitHub was used only for public AGENTS.md examples.

## 2026-05-26

### Hyprland screenshots

Question:

What is the smallest reliable screenshot workflow for the current Hyprland setup?

Sources:

- Hyprland Wiki Screenshots & Recording: https://wiki.hypr.land/Useful-Utilities/Screenshots-and-Recording/
- Arch Linux `grim`: https://archlinux.org/packages/extra/x86_64/grim/
- Arch Linux `slurp`: https://archlinux.org/packages/extra/x86_64/slurp/

Conclusion:

Use already-installed `grim` and `slurp` for file-based screenshots. Defer clipboard and annotation tooling because those require extra packages not needed for the immediate request.

### Host workspace model

Question:

How should the host workspace labels be separated from the future Kali VM workspace labels?

Sources:

- Hyprland dispatchers/workspaces: https://wiki.hypr.land/Configuring/Basics/Dispatchers/
- Waybar Hyprland workspaces module: https://github.com/Alexays/Waybar/wiki/Module%3A-Hyprland
- Local project brief: `context/00_project_brief.md`
- Local working agreements: `context/01_working_agreements.md`

Conclusion:

Move cyber-specific labels to the future Kali guest. Use short host labels for cockpit/control, normal work, code/config, AI, VM control, vault, comms, and game mode.

### Control dashboard first iteration

Question:

What is the smallest useful implementation for the host control space without installing new packages?

Sources:

- Python `http.server`: https://docs.python.org/3/library/http.server.html
- Python `subprocess`: https://docs.python.org/3/library/subprocess.html
- MDN Canvas API: https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API

Conclusion:

Use Python stdlib for an immediate terminal cockpit plus a localhost-only web shell. Defer browser/frontend package choices until the repo has package manifests and dashboard architecture is researched as its own step.

### Wayland screenshot clipboard

Question:

What should be used so Hyprland screenshots can be pasted directly with `Ctrl+V`?

Sources:

- Arch Linux `wl-clipboard`: https://archlinux.org/packages/extra/x86_64/wl-clipboard/
- Upstream `wl-clipboard`: https://github.com/bugaevc/wl-clipboard
- ArchWiki Clipboard: https://wiki.archlinux.org/title/Clipboard

Conclusion:

Use `wl-copy` from `wl-clipboard` with existing `grim` and `slurp`. Wrap the workflow in `scripts/ctos-screenshot`.

## 2026-06-02

### Read-only libvirt inventory CLI

Question:

What is the safest first VM automation layer for the CTOS host cockpit?

Sources:

- libvirt `virsh` manpage: https://www.libvirt.org/manpages/virsh.html
- libvirt connection URI documentation: https://libvirt.org/uri.html
- libvirt VM lifecycle documentation: https://wiki.libvirt.org/VM_lifecycle.html
- Local libvirt inventory: `context/10_libvirt_inventory.md`

Conclusion:

Start with a read-only `scripts/ctos-vm` helper that checks both `qemu:///system` and `qemu:///session`. Expose `list`, `status`, and `inspect`; defer start/stop/snapshot actions until VM definitions, storage ownership, network policy, and snapshot policy are documented.

### CTOS VM lifecycle model

Question:

Where should CTOS-managed VMs live, and what storage/network/snapshot policy should the host cockpit use?

Sources:

- libvirt connection URI documentation: https://libvirt.org/uri.html
- libvirt FAQ on `qemu:///system` vs `qemu:///session`: https://wiki.libvirt.org/FAQ.html
- ArchWiki libvirt: https://wiki.archlinux.org/title/Libvirt
- libvirt network XML documentation: https://libvirt.org/formatnetwork.html
- libvirt storage management documentation: https://libvirt.org/storage.html
- libvirt storage pool/volume XML documentation: https://www.libvirt.org/formatstorage.html
- libvirt snapshot XML documentation: https://libvirt.org/formatsnapshot.html
- Local lifecycle model: `context/11_vm_lifecycle_model.md`

Conclusion:

Use `qemu:///system` for CTOS-managed domains, create dedicated CTOS network and storage pool definitions, keep domains non-autostart by default, and limit first snapshot automation to shutoff disk snapshots. Keep `qemu:///session` visible in read-only inventory only.

## 2026-06-03

### CTOS libvirt infra apply command

Question:

What is the smallest safe live mutation before defining Kali or Dev domains?

Sources:

- libvirt `virsh` manpage: https://www.libvirt.org/manpages/virsh.html
- libvirt network XML documentation: https://libvirt.org/formatnetwork.html
- libvirt storage management documentation: https://libvirt.org/storage.html
- libvirt storage pool/volume XML documentation: https://www.libvirt.org/formatstorage.html
- Local lifecycle model: `context/11_vm_lifecycle_model.md`

Conclusion:

Apply only the dedicated CTOS network and storage pools first. Use a separate idempotent script with `status`, `plan`, and `apply`, and refuse conflicting live resources instead of overwriting them.

Update:

The first Kali start attempt showed that installer media under `/home/operator` is not usable by QEMU because `/home/operator` is not traversable by the QEMU/libvirt process. Add `ctos-iso` as the dedicated installer ISO pool.

### Kali install-phase domain

Question:

How should the first Kali VM be defined without starting or silently installing it?

Sources:

- Kali installation requirements: https://www.kali.org/docs/installation/hard-disk-install/
- virt-install upstream manpage: https://github.com/virt-manager/virt-manager/blob/main/man/virt-install.rst
- libvirt domain XML documentation: https://www.libvirt.org/formatdomain.html
- Local lifecycle model: `context/11_vm_lifecycle_model.md`
- Local CTOS infra state: `context/12_libvirt_infra_state.md`

Conclusion:

Define `ctos-kali` as a shutoff install-phase libvirt domain with a 40 GiB qcow2 volume, 6 GiB RAM, 2 vCPU, virtio disk/network, SPICE graphics, and Kali installer ISO attached. Do not start the guest in this step.

## 2026-06-12

### Tower `ctos-core` same-day install path

Question:

What is the lowest-risk way to wipe the recovered tower, install EndeavourOS, and bring it online as the first CTOS core node?

Sources:

- EndeavourOS installer customization docs: https://discovery.endeavouros.com/installation/customizing-the-endeavouros-install-process/
- EndeavourOS latest release/install context: https://endeavouros.com/latest-release/
- Btrfs subvolume/filesystem docs: https://btrfs.readthedocs.io/en/latest/Subvolumes.html
- Arch Linux Xfce package group: https://archlinux.org/groups/x86_64/xfce4/
- Local tower diagnostic state: `context/18_tower_diagnostic_state.md`
- Local package checks with `pacman -Si` and `pacman -Sgq`

Conclusion:

Use the official EndeavourOS installer and a separate CTOS post-install bootstrap kit. For V1, install Xfce on the NVMe, then apply `bootstrap/ctos-apply-role`. Initialize the SATA SSD as `/srv/ctos` only after first boot with a guarded helper. Defer custom ISO, AUR, secrets, AI services, and LAN caches until the core node is reachable and stable.

### Offline tower network recovery

Question:

How should the first installed tower recover networking without a GUI and without an existing SSH link?

Sources:

- NetworkManager `nmcli` reference, accessed 2026-06-12: https://networkmanager.dev/docs/api/latest/nmcli.html
- NetworkManager Wi-Fi security setting reference, accessed 2026-06-12: https://networkmanager.dev/docs/api/latest/settings-802-11-wireless-security.html
- Local package checks for `networkmanager`, `usbmuxd`, `libimobiledevice`, and `ifuse` with `pacman -Si`, 2026-06-12.

Conclusion:

Use a USB round-trip helper rather than relying on GUI networking. `ctos-core-netfix` captures a diagnostic report, recreates Wi-Fi profiles with explicit `wifi-sec.key-mgmt`, and attempts iPhone USB tethering through available kernel modules/NetworkManager. It does not log Wi-Fi secrets.

### Kali install start

Question:

How should the Kali installer be started without hiding or automating guest installation?

Sources:

- Local `virsh help start`
- Local `virt-viewer --help`
- Local `virt-manager --help`
- Local `hyprctl clients`
- virt-viewer upstream project: https://gitlab.com/virt-viewer/virt-viewer
- libvirt `virsh` manpage: https://www.libvirt.org/manpages/virsh.html
- Local Kali domain state: `context/13_kali_domain_state.md`
- Local Kali install start state: `context/14_kali_install_start.md`

Conclusion:

Use an explicit `scripts/ctos-kali start-install` command that starts only a compatible shutoff install-phase domain. On Hyprland, open the visible console through `hyprctl dispatch exec` and `virt-manager`; keep installer interaction manual and visible.

### Kali post-install boot transition

Question:

How should the installed Kali guest be booted after the manual installer finishes?

Sources:

- libvirt domain XML documentation: https://www.libvirt.org/formatdomain.html
- libvirt `virsh` manpage: https://www.libvirt.org/manpages/virsh.html
- Local Kali install start state: `context/14_kali_install_start.md`
- Local Kali post-install state: `context/15_kali_post_install_boot.md`

Conclusion:

Keep the install profile as a separate repo XML and add `libvirt/domains/ctos-kali.xml` for the installed profile. The installed profile removes the installer CDROM, boots only from `hd`, and sets reboot behavior to `restart`. Apply the transition through `scripts/ctos-kali finalize-install` so the live domain remains reproducible.

### Kali guest egress through firewalld

Question:

How should Kali guest egress be allowed when the guest can reach `virbr-ctos` but not the internet?

Sources:

- libvirt firewall documentation: https://libvirt.org/firewall
- firewalld concepts: https://firewalld.org/documentation/concepts.html
- firewall-cmd manual: https://firewalld.org/documentation/man-pages/firewall-cmd.html

Conclusion:

Use firewalld policy semantics rather than ad hoc nftables rules. The host has `virbr-ctos` in zone `libvirt` and `wlan0` in zone `public`; firewalld denies inter-zone forwarding by default unless a policy permits it. Proposed fix: create a dedicated `ctos-vm-egress` policy from `libvirt` to `public`, set target `ACCEPT`, and enable masquerade.

## 2026-06-08

### Cockpit Kali controls

Question:

How should the local `CTRL` cockpit expose first VM actions for Kali?

Sources:

- Local VM lifecycle model: `context/11_vm_lifecycle_model.md`
- Local Kali baseline/checkpoint state: `context/16_kali_baseline_snapshot.md`
- Local `virsh` behavior verified through `domstate`, `domblklist`, `snapshot-list`, `start`, and `shutdown --mode agent`
- Local cockpit implementation: `control/server.py`, `control/status.py`, `control/tui.py`

Conclusion:

Expose only `ctos-kali` through a localhost-only dashboard action endpoint. Allow only fixed actions: `start`, guest-agent `shutdown`, `console`, and offline-only `checkpoint`. Do not accept arbitrary commands or arbitrary domain names.

### CTOS archipelago fleet model

Question:

How should the recovered tower and future machines fit into the EndeavourOS CTOS model without derailing the T480 cockpit mission?

Sources:

- EndeavourOS installer customization: https://discovery.endeavouros.com/installation/customizing-the-endeavouros-install-process/
- EndeavourOS latest release/install context: https://endeavouros.com/latest-release/
- Ansible inventory docs: https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html
- Local repo blueprint: `context/07_repo_blueprint.md`
- Local cockpit roadmap: `context/09_cockpit_roadmap.md`

Conclusion:

Keep EndeavourOS as the fleet target. Treat the T480 as the mobile admin/work machine, the recovered tower as pending `ctos-core`, and future PCs as worker nodes. Start with an official EndeavourOS install plus a CTOS bootstrap USB kit; defer custom installer automation and Ansible until manifests and role scripts are proven.

## 2026-06-15

### T480-to-ctos-core remote control V0

Question:

How should the T480 begin controlling the tower desktop without exposing an unsafe remote desktop service?

Sources:

- Local `ctos-core` SSH/session probe, 2026-06-15.
- Local package database check: `pacman -Si krdp krfb freerdp remmina tigervnc waypipe wayvnc moonlight-qt`.
- Local package file inspection: `krdp` provides `usr/bin/krdpserver`, `app-org.kde.krdpserver.service`, and `kcm_krdpserver`; `freerdp` provides `wlfreerdp3` and `xfreerdp3`.
- Local `xfreerdp3 /help`, 2026-06-15: confirms `/gdi: sw|hw`, `/bpp`, `/network`, fixed geometry, and `/cert:ignore` options.
- Operator FreeRDP log, 2026-06-15: `wlfreerdp3` reached KRDP authentication but the client window stayed blank while logging VAAPI/libavcodec initialization failures.
- Remote KRDP journal, 2026-06-15: software-only `xfreerdp3` profile was rejected with `Client does not support graphics pipeline which is required`.
- Remote KRDP journal, 2026-06-16: RDPGFX/no-AVC `xfreerdp3` profile was rejected with `Client does not support H.264 in YUV420 mode!`.
- Remote KRDP journal and operator test, 2026-06-16: RDPGFX/AVC `xfreerdp3` selected `RDPGFX_CAPVERSION_107` but the client stayed blank until cancellation.
- Local Remmina full-version check, 2026-06-16: VNC plugin file exists but fails to load without `libvncclient.so.1`; `libvncserver` provides the missing client library.
- Local/remote VNC runtime check, 2026-06-16: `krfb` launched in the active tower KDE session and listened on `0.0.0.0:5900` plus `[::]:5900`; user-added runtime firewalld rich reject rules made direct T480 access to `10.42.0.2:5900` return `Connection refused`; SSH tunnel `127.0.0.1:5901 -> 127.0.0.1:5900` TCP-tested successfully.
- Local Remmina/TigerVNC check, 2026-06-16: Remmina VNC launch blocked on a desktop keyring unlock prompt; `pacman -Si tigervnc` reported `tigervnc 1.16.2-2` in Arch `extra`, providing the VNC client/server suite with a 2.48 MiB download and 6.66 MiB installed size.
- KRFB/TigerVNC validation, 2026-06-16: TigerVNC authenticated to KRFB and displayed a desktop frame, but the frame stayed static and keyboard/mouse input did not work. Setting `allowDesktopControl=true` with `kwriteconfig6`, restarting KRFB, and launching `vncviewer -RemoteResize=0 -Shared 127.0.0.1:5901` did not fix refresh/input. KRFB is not a validated V1 backend.
- Local TigerVNC man/help checks, 2026-06-16: `tigervnc` provides `vncviewer`, `w0vncserver`, and `x0vncserver`; `w0vncserver` supports existing Wayland compositor sharing via RemoteDesktop portal; `x0vncserver` supports existing X displays and documents `-localhost` for SSH-tunneled use.
- KDE KRdp source inspection: `server/main.cpp` documents `--address`, `--port`, PAM auth, and username/password options; `krdpserversettings.kcfg` documents `ListenPort`, `Users`, `SystemUserEnabled`, and `Autostart`.
- KDE KRFB Desktop Sharing app page: https://apps.kde.org/krfb/
- FreeRDP project: https://www.freerdp.com/
- TigerVNC project: https://www.tigervnc.org/
- Waypipe project: https://gitlab.freedesktop.org/mstoeckl/waypipe

Conclusion:

Start with a tunnel-first model. Prefer testing KDE current-session remote desktop through `krdp` plus `freerdp`/`remmina`, with `krfb`/VNC as fallback. Bind KRDP to `127.0.0.1` through a user systemd override, use PAM for the existing `ctos` system user instead of storing a password in the repo/chat, and defer `xrdp`/AUR and high-performance Sunshine/Moonlight until explicitly chosen. KRDP is not visually validated yet; move the next test to VNC/KRFB with Remmina through an SSH tunnel.

## 2026-06-16

### T480 Hyprland boot cockpit and current window rules

Question:

How should the T480 boot the `CTRL`, `DESK`, and `VMS` operator windows, restore the repo wallpaper, and avoid current Hyprland config errors?

Sources:

- Hyprland Window Rules wiki, accessed 2026-06-16: https://wiki.hypr.land/Configuring/Window-Rules/
- Hyprland Workspace Rules wiki, accessed 2026-06-16: https://wiki.hypr.land/Configuring/Workspace-Rules/
- Local TigerVNC `vncviewer(1)` manpage, checked 2026-06-16.
- TigerVNC `DesktopWindow.cxx` source, checked 2026-06-16: https://github.com/TigerVNC/tigervnc/blob/master/vncviewer/DesktopWindow.cxx
- Local TigerVNC `vncviewer --help`, checked 2026-06-16.
- Local Remmina VNC fallback test, 2026-06-16: Remmina reopened the desktop keyring prompt and did not produce a clean unattended DESK session.
- Local Hyprland config and runtime checks: `hyprland/hyprland.conf`, `hyprctl reload`, `hyprctl configerrors`, and `hyprctl clients`.
- Local boot cockpit scripts: `scripts/ctos-session`, `scripts/ctos-wallpaper`, `scripts/ctos-desk-remote`, and `scripts/ctos-vms-panel`.
- Repo wallpaper asset: `Assets/BackGround/4.webp`.

Conclusion:

Use a repo-owned `scripts/ctos-session boot` launched from Hyprland `exec-once`. Place windows with current anonymous `windowrule = match:...` rules, not deprecated `windowrulev2`. Restore the wallpaper through `scripts/ctos-wallpaper`, keep the tower desktop tunnel-only on `DESK`, and keep Kali VM startup explicit through the `VMS` panel rather than autostarting the VM. Use Hyprland workspace rules for DESK-specific no-gap/no-border remote desktop framing.

Update:

For the tower dual-screen DESK profile, use TigerVNC full-screen mode because its manpage documents edge scrolling when the remote desktop is larger than the local screen. Normalize the tower X11 layout to `3840x1080` before launching the viewer so vertical scroll is avoided and only horizontal edge panning remains.

Update:

TigerVNC upstream source shows edge scrolling is triggered for drag events as well as normal pointer movement, but `vncviewer --help` exposes no edge-scroll speed/threshold setting. Keep TigerVNC as the V1 DESK viewer and tune pointer event interval to reduce drag latency. Remmina scaled mode is rejected for V1 because it reintroduces the keyring prompt blocker.

## 2026-06-17

### Restart-safe T480 and ctos-core cockpit contract

Question:

How should the T480 and tower recover `CTRL`, `DESK`, and `VMS` after reboot without exposing the tower desktop directly?

Sources:

- OpenSSH `sshd(8)`, accessed 2026-06-17: https://man.openbsd.org/sshd.8
- Local tower runtime checks, 2026-06-17: `systemctl status sshd`, `journalctl -u sshd`, `ss -lntp`, `ps -ef`, and active foreground `sshd` on port `2222`.
- Local SDDM/session inventory on `ctos-core`, 2026-06-17: `/usr/share/xsessions/plasmax11.desktop`, `/usr/share/wayland-sessions/plasma.desktop`, and `/etc/sddm.conf`.
- Local libvirt verification, 2026-06-17: `virsh -c qemu:///system --readonly domstate ctos-kali` and `virsh -c qemu:///system --readonly list --all`.
- Local Hyprland verification, 2026-06-17: `hyprctl configerrors` and `scripts/ctos-session status`.

Conclusion:

Keep the desktop stream tunnel-only: T480 starts `x0vncserver` on `ctos-core` bound to localhost and reaches it through SSH. Make the T480 DESK launcher try SSH/22 first and rescue SSH/2222 second. Add a tower-side root boot contract script for normal `sshd.service`, restricted rescue SSH, and optional SDDM autologin into Plasma X11 when unattended DESK is explicitly desired. Do not expose VNC on the LAN.

### Tower VS Code and Codex user-local install

Question:

How should VS Code and Codex be installed on `ctos-core` when sudo is not available non-interactively?

Sources:

- Microsoft VS Code Linux setup: https://code.visualstudio.com/docs/setup/linux
- Microsoft VS Code stable Linux x64 update endpoint checked from `ctos-core`: https://update.code.visualstudio.com/latest/linux-x64/stable
- AUR `visual-studio-code-bin`: https://aur.archlinux.org/packages/visual-studio-code-bin
- npm `@openai/codex`: https://www.npmjs.com/package/%40openai/codex
- Visual Studio Marketplace OpenAI Codex extension: https://marketplace.visualstudio.com/items?itemName=OpenAI.chatgpt
- Local `ctos-core` checks, 2026-06-17: `sudo -n true`, `npm view @openai/codex version`, `code --version`, `codex --version`, and `code --list-extensions`.

Conclusion:

For `ctos-core` V1, use a sudo-free user-local install: official VS Code stable tarball in `~/.local/opt/vscode`, `~/.local/bin/code`, Codex CLI installed with `npm --prefix ~/.local`, and extension `OpenAI.chatgpt`. Keep AUR `visual-studio-code-bin` as the later system-managed replacement when an intentional sudo package step is available.

### CTOS AI V0 architecture scan

Question:

How should CTOS begin a Jarvis-like assistant without handing a model unrestricted control of the T480, tower, or lab VMs?

Sources:

- OpenHands GitHub: https://github.com/All-Hands-AI/OpenHands
- Open Interpreter docs: https://docs.openinterpreter.com/getting-started/introduction
- LangGraph documentation: https://langchain-ai.github.io/langgraph/
- Model Context Protocol introduction: https://modelcontextprotocol.io/docs/getting-started/intro
- Model Context Protocol security best practices: https://modelcontextprotocol.io/specification/2025-06-18/basic/security_best_practices
- OpenAI Agents SDK guide: https://developers.openai.com/api/docs/guides/agents-sdk
- OpenAI computer-use tool guide: https://platform.openai.com/docs/guides/tools-computer-use
- Ollama GitHub: https://github.com/ollama/ollama
- openWakeWord GitHub: https://github.com/dscripka/openWakeWord
- whisper.cpp GitHub: https://github.com/ggerganov/whisper.cpp
- Piper project note: https://github.com/rhasspy/piper

Conclusion:

Start CTOS AI with a small repo-owned tool contract and agenda/memory layer. Borrow ideas from open-source agent frameworks, but do not adopt a full generic assistant stack as the V0 architecture. Defer model/provider choice, MCP exposure, voice, external calendar connectors, and computer-use automation until the deterministic tool layer and approval boundaries exist.

### GLM-5.2 and AirLLM scan

Question:

Can GLM-5.2 or AirLLM materially change the next CTOS AI implementation step?

Sources:

- Z.ai GLM-5 GitHub README, accessed 2026-06-19: https://github.com/zai-org/GLM-5
- Z.ai GLM-5.2 model links and local serving framework list in the same README, accessed 2026-06-19.
- AirLLM GitHub README, accessed 2026-06-19: https://github.com/lyogavin/airllm
- AirLLM PyPI package page, accessed 2026-06-19: https://pypi.org/project/airllm/

Conclusion:

GLM-5.2 is relevant as a frontier-scale long-context coding/agentic model candidate, especially through an API or future larger compute, but its 744B-A40B distribution is not a realistic local runtime target for the current T480/ctos-core hardware. AirLLM is useful inspiration for disk/layer offload and low-VRAM experiments, but its PyPI release is from 2024-09-21 and its architecture is better treated as an experimental batch path than the V1 CTOS assistant runtime. The next CTOS step remains an approval surface and provider-agnostic tool boundary, not a model install.

### CTOS AI provider/runtime profile abstraction

Question:

How should CTOS describe future model/provider choices before installing or activating any runtime?

Sources:

- OpenAI Responses API reference, accessed 2026-06-19: https://platform.openai.com/docs/api-reference/responses
- Ollama API documentation, accessed 2026-06-19: https://docs.ollama.com/api
- Ollama OpenAI compatibility documentation, accessed 2026-06-19: https://docs.ollama.com/openai
- llama.cpp server documentation, accessed 2026-06-19: https://github.com/ggml-org/llama.cpp/tree/master/tools/server
- Z.ai GLM-5 GitHub README, accessed 2026-06-19: https://github.com/zai-org/GLM-5
- AirLLM GitHub README, accessed 2026-06-19: https://github.com/lyogavin/airllm
- AirLLM PyPI package page, accessed 2026-06-19: https://pypi.org/project/airllm/

Conclusion:

Represent runtimes as inert declarative profiles under `ai/runtime_profiles.json`. Keep `active_profile` unset until a separate secrets/privacy, benchmark, and service decision exists. Treat Ollama as the first local candidate for `ctos-core`, OpenAI Responses API as the first external candidate after secrets policy, llama.cpp server as a more tunable local candidate, GLM-5.2 as a future external/frontier candidate, and AirLLM as a lab/offload experiment.

### CTOS AI runtime dry-run adapter

Question:

How should CTOS test runtime/provider profiles before allowing prompts, private context, or model calls?

Sources:

- CTOS runtime profiles: `ai/runtime_profiles.json`
- CTOS AI tool contract: `context/20_ctos_ai_v0_model.md`
- Prior provider/runtime source set in this registry entry: "CTOS AI provider/runtime profile abstraction"
- Live owned-node probe on 2026-06-19: `ctos-ai runtime-check ollama-core-local --target-probe`

Conclusion:

Use `ctos-ai runtime-check <id>` as the first adapter contract. The default path validates profile metadata, endpoint shape, readiness labels, and secret environment variable presence by name only, while refusing endpoint/model contact. Optional `--target-probe` is limited to owned CTOS node checks such as `ctos-core` reachability and model-cache storage readiness.

### CTOS Ollama localhost benchmark plan

Question:

How should CTOS run the first local model benchmark on `ctos-core` without prematurely selecting a runtime or exposing a LAN service?

Sources:

- Arch Linux `ollama` package, accessed 2026-06-20: https://archlinux.org/packages/extra/x86_64/ollama/
- Ollama Linux documentation, accessed 2026-06-20: https://docs.ollama.com/linux
- Ollama API introduction, accessed 2026-06-20: https://docs.ollama.com/api/introduction
- Ollama pull API, accessed 2026-06-20: https://docs.ollama.com/api/pull
- Ollama generate API, accessed 2026-06-20: https://docs.ollama.com/api/generate
- Ollama running models API, accessed 2026-06-20: https://docs.ollama.com/api/ps
- Ollama Qwen2.5-Coder 0.5B model card, accessed 2026-06-20: https://ollama.com/library/qwen2.5-coder:0.5b
- Ollama Qwen2.5-Coder 1.5B model card, accessed 2026-06-20: https://ollama.com/library/qwen2.5-coder:1.5b
- Local preflight on 2026-06-20: `ctos-ollama-bench preflight`

Conclusion:

Prepare a CPU-safe Ollama benchmark before activating a runtime. Use the Arch `ollama` package, bind the service to `127.0.0.1:11434`, store models under `/srv/ctos/models/ollama`, and benchmark small Qwen2.5-Coder models first. Keep GPU packages, LAN exposure, final runtime selection, and model-backed assistant integration deferred until benchmark data and the RX6600 hardware path are stable.

### CTOS Voice Backend V2 spike

Question:

What open-source/local voice stack should CTOS evaluate after the Vosk push-to-talk V1 proves useful but fragile?

Sources:

- Home Assistant local voice assistant docs, accessed 2026-07-07: https://www.home-assistant.io/voice_control/voice_remote_local_assistant/
- Home Assistant voice control docs, accessed 2026-07-07: https://www.home-assistant.io/voice_control/
- Home Assistant custom sentences docs, accessed 2026-07-07: https://www.home-assistant.io/voice_control/custom_sentences/
- Speech-to-Phrase repo, accessed 2026-07-07: https://github.com/OHF-Voice/speech-to-phrase
- Wyoming Piper repo, accessed 2026-07-07: https://github.com/rhasspy/wyoming-piper
- OpenVoiceOS repo, accessed 2026-07-07: https://github.com/OpenVoiceOS/OpenVoiceOS
- Leon repo, accessed 2026-07-07: https://github.com/leon-ai/leon

Conclusion:

Do not keep making the Vosk command matcher larger as the main strategy. Keep Vosk V1 as fallback, but evaluate a mature local voice stack around Home Assistant Assist/Wyoming and a phrase/intent recognizer. Add a CTOS-owned intent catalog first, then connect one backend to it. Do not install persistent services until the install path, ports, storage, and permission boundary are documented.

### CTOS Voice backend export adapter

Question:

What inert export format should CTOS generate so the local intent catalog can be tested with mature voice backends?

Sources:

- Home Assistant custom sentences docs, accessed 2026-07-07: https://www.home-assistant.io/voice_control/custom_sentences/
- Home Assistant local voice assistant docs, accessed 2026-07-07: https://www.home-assistant.io/voice_control/voice_remote_local_assistant/
- Speech-to-Phrase README, accessed 2026-07-07: https://github.com/OHF-Voice/speech-to-phrase
- CTOS intent catalog: `ai/voice_intents_fr.json`

Conclusion:

Export Home Assistant-compatible custom sentences under `custom_sentences/fr/ctos.yaml` and keep a separate `ctos_intent_map.json` sidecar for CTOS command/tier mapping. Speech-to-Phrase can consume custom-sentence directories for fixed command recognition, while CTOS retains the action and approval boundary. Add local validation before any real backend test so phrase recognition artifacts cannot silently drift away from CTOS permissions.

### CTOS Voice Speech-to-Phrase preflight

Question:

How should CTOS move toward Speech-to-Phrase without pretending it is already a complete local Jarvis backend?

Sources:

- Speech-to-Phrase repo/README, accessed 2026-07-07: https://github.com/OHF-Voice/speech-to-phrase
- Home Assistant custom sentences docs, accessed 2026-07-07: https://www.home-assistant.io/voice_control/custom_sentences/
- Home Assistant custom sentence YAML docs, accessed 2026-07-07: https://www.home-assistant.io/voice_control/custom_sentences_yaml/
- CTOS generated backend bundle contract: `scripts/ctos-voice-v2`, `docs/VOICE_BACKEND_V2.md`

Conclusion:

Add `ctos-voice-v2 backend-preflight` before any service install. The preflight should verify CTOS bundle readiness, local tools, Python runtime imports, optional `ctos-core` readiness, and whether a temporary Home Assistant websocket/token-file context exists. Missing Speech-to-Phrase runtime or Home Assistant context should be reported as blockers for full recognition, not hidden behind a vague install command.

### CTOS Speech-to-Phrase smoke install

Question:

Can Speech-to-Phrase be imported and inspected locally without installing a daemon?

Sources:

- Speech-to-Phrase repo/README, accessed 2026-07-07: https://github.com/OHF-Voice/speech-to-phrase
- Speech-to-Phrase package metadata/help from the temporary venv, checked 2026-07-07 with `/tmp/ctos-speech-to-phrase-smoke-venv/bin/python -m speech_to_phrase --help`
- Local pip/GitHub install result, checked 2026-07-07: `git+https://github.com/OHF-Voice/speech-to-phrase.git` resolved to commit `b4ecef9519e84fefd5dc35c0384c50efa13a0bad`

Conclusion:

PyPI lookup did not expose an installable `speech-to-phrase`/`speech_to_phrase` package for the current environment, but installing from the official GitHub repo into a disposable `/tmp` venv succeeded. The runtime is importable as `speech_to_phrase 1.4.3` with `wyoming 1.5.4`. The invocation surface is `python -m speech_to_phrase`, not a dedicated console script. Full recognition remains blocked on a temporary Home Assistant websocket/token-file context.

### CTOS Speech-to-Phrase no-HA training boundary

Question:

Can CTOS get a useful Speech-to-Phrase step before standing up Home Assistant/Wyoming?

Sources:

- Speech-to-Phrase installed source inspected from the disposable venv on 2026-07-07:
  - `speech_to_phrase/train.py`
  - `speech_to_phrase/train_kaldi.py`
  - `speech_to_phrase/models.py`
  - `speech_to_phrase/speech_tools.py`
- Runtime help checked on 2026-07-07: `/tmp/ctos-speech-to-phrase-smoke-venv/bin/python -m speech_to_phrase.train --help`
- CTOS preflight checked on 2026-07-07: `ctos-voice-v2 backend-preflight --backend speech-to-phrase --dir /tmp/ctos-voice-backend-preflight-test --runtime-python /tmp/ctos-speech-to-phrase-smoke-venv/bin/python`

Conclusion:

Yes, but only as an offline training stage, not as a full live recognizer. `speech_to_phrase.train` can consume the generated CTOS YAML directly and does not require a Home Assistant token. It does require the `fr_FR-rhasspy` Kaldi model and a speech-tools cache containing Kaldi, OpenFST, OpenGRM, and Phonetisaurus. The CTOS preflight now reports this as `offline_training_context_ready`, separate from `backend_runtime_ready` and the later Home Assistant/Wyoming `full_recognition_ready`.

### CTOS Speech-to-Phrase cache placement

Question:

Where should CTOS place the Speech-to-Phrase model and speech-tool caches?

Sources:

- Speech-to-Phrase repo/README, accessed 2026-07-07: https://github.com/OHF-Voice/speech-to-phrase
- Home Assistant Wyoming integration docs, accessed 2026-07-07: https://www.home-assistant.io/integrations/wyoming/
- Local Speech-to-Phrase source inspected from the disposable venv on 2026-07-07:
  - `speech_to_phrase/models.py`
  - `speech_to_phrase/train.py`
  - `speech_to_phrase/train_kaldi.py`
  - `speech_to_phrase/speech_tools.py`
- Live owned-node cache probe on 2026-07-07: `ctos-voice-v2 stp-cache --runtime-python /tmp/ctos-speech-to-phrase-smoke-venv/bin/python --target-probe`

Conclusion:

Use `ctos-core` under `/srv/ctos`, not the T480 user home, for model and speech-tool caches. The first helper is read-only: `ctos-voice-v2 stp-cache` checks expected model/tool paths and can probe `ctos-core` over SSH. On 2026-07-07 the probe reached `ctos-core` and confirmed that the `fr_FR-rhasspy` model and Kaldi/OpenFST/OpenGRM/Phonetisaurus tool cache are not present yet.

### CTOS Speech-to-Phrase official container path

Question:

Should the first live Speech-to-Phrase backend test use a local Python/Kaldi toolchain or the official Wyoming container?

Sources:

- Speech-to-Phrase repo/README, accessed 2026-07-07: https://github.com/OHF-Voice/speech-to-phrase
- Speech-to-Phrase Docker Hub image page, accessed 2026-07-07: https://hub.docker.com/r/rhasspy/wyoming-speech-to-phrase
- Home Assistant Wyoming integration docs, accessed 2026-07-07: https://www.home-assistant.io/integrations/wyoming/
- Local installed source inspected on 2026-07-07: `speech_to_phrase/__main__.py`, `train.py`, `train_kaldi.py`, `models.py`, `speech_tools.py`
- Live owned-node probe on 2026-07-07: `ctos-voice-v2 stp-container-plan --target-probe`
- Live owned-node image inspection on 2026-07-07: `ctos-voice-v2 stp-container-inspect`
- Remote container image filesystem inspection on 2026-07-07: `podman image inspect docker.io/rhasspy/wyoming-speech-to-phrase` and `podman run --rm --entrypoint /bin/sh ... sed -n '1,220p' /run.sh`

Conclusion:

Use the official `docker.io/rhasspy/wyoming-speech-to-phrase` container as the first live backend route on `ctos-core`. The local Python package remains useful for parsing, bundle validation, and offline trainer inspection, but the first live loop should avoid a custom host-level Kaldi/OpenFST/OpenGRM/Phonetisaurus build. `ctos-core` already has `/usr/bin/podman`; the CTOS custom-sentence bundle has been copied to `/srv/ctos/voice/backend/speech-to-phrase`. Podman rejected the short image name, so CTOS must keep the fully qualified `docker.io/...` reference. The pulled image digest was `sha256:9ef75f4a4f21484ebbe7e0c0f81a53bb7670e6b57430c7d8fa632239ba318289`. Its `/run.sh` uses image-internal `/usr/src/tools`; do not mount a host `/tools` directory for the first live test.

### CTOS temporary Home Assistant context

Question:

What is the smallest Home Assistant context CTOS should use so Speech-to-Phrase can run one live recognition loop without installing a permanent assistant platform?

Sources:

- Home Assistant Linux/Container installation docs, accessed 2026-07-07: https://www.home-assistant.io/installation/linux
- Home Assistant WebSocket API docs, accessed 2026-07-07: https://developers.home-assistant.io/docs/api/websocket/
- Home Assistant local voice assistant docs, accessed 2026-07-07: https://www.home-assistant.io/voice_control/voice_remote_local_assistant/
- Speech-to-Phrase repo/README, accessed 2026-07-07: https://github.com/OHF-Voice/speech-to-phrase
- CTOS Speech-to-Phrase container decision: `context/02_decision_log.md` ADR-0054

Conclusion:

Use a temporary `ghcr.io/home-assistant/home-assistant:stable` container on `ctos-core`, rootless through `podman`, with config under `/srv/ctos/voice/home-assistant-test/config` and UI/API bound only to `127.0.0.1:8123`. Access it from the T480 through an SSH tunnel, create a long-lived token manually, and store only the token value in `/run/user/$UID/ctos-ha-token` outside Git and shell history. This gives Speech-to-Phrase the websocket/token surface it expects while avoiding Home Assistant OS/Supervisor, LAN exposure, hardware mounts, or a persistent daemon for the first test.

Live check 2026-07-07:

`ctos-voice-v2 hass-context start` pulled and started the temporary container. `ctos-voice-v2 hass-context status --json` reported the container running and HTTP `302`. The image observed on `ctos-core` had id `ceb81d836a0b125a4ec14a754231a5dd1cc5f2feb2594107320c3cea345dd9d1` and digest `sha256:21e0d1bae299819d8cf4ef8aa197593205a5fae51c69031c13bfd1eac8c56204`.

Browserless onboarding verification 2026-07-07:

The T480 lacks a classic browser for `http://127.0.0.1:8123`, so the Home Assistant server-side onboarding schemas were inspected inside the running temporary container before adding an API helper:

- `/usr/src/homeassistant/homeassistant/components/onboarding/views.py`
- `/usr/src/homeassistant/homeassistant/components/auth/__init__.py`

The verified flow is: create first user through `/api/onboarding/users`, exchange `auth_code` through `/auth/token`, complete the lightweight onboarding steps with the returned access token, create a long-lived token through websocket command `auth/long_lived_access_token`, and store only the long-lived token through the existing CTOS token-file path. `ctos-voice-v2 hass-context onboard-api` implements this flow without printing secrets.

### CTOS Jarvis mature voice-stack pivot

Question:

Should CTOS keep iterating phrase fixes for the current voice command path, or adopt a more mature local open-source voice stack as the base?

Sources:

- Home Assistant voice control documentation, accessed 2026-07-07: https://www.home-assistant.io/voice_control/
- Home Assistant local voice assistant documentation, accessed 2026-07-07: https://www.home-assistant.io/voice_control/voice_remote_local_assistant/
- Home Assistant Wyoming integration documentation, accessed 2026-07-07: https://www.home-assistant.io/integrations/wyoming/
- Speech-to-Phrase repository, accessed 2026-07-07: https://github.com/OHF-Voice/speech-to-phrase
- OpenVoiceOS core repository, accessed 2026-07-07: https://github.com/OpenVoiceOS/ovos-core
- Open Interpreter documentation, accessed 2026-07-07: https://docs.openinterpreter.com/
- Open Interpreter 01 repository, accessed 2026-07-07: https://github.com/OpenInterpreter/01
- AirLLM reference implementation lookup, accessed 2026-07-07: https://github.com/lyogavin/Anima/tree/main/air_llm
- GLM-5.2 / GLM-family repository lookup, accessed 2026-07-07: https://github.com/zai-org/GLM-5

Conclusion:

Adopt a hybrid mature-stack strategy. Home Assistant Assist/Wyoming is the best fit for the current CTOS direction because it integrates local voice adapters and keeps Speech-to-Phrase/Piper/Wyoming aligned. Speech-to-Phrase remains the deterministic command rail; a local Whisper-compatible STT rail should be added for natural requests. OpenVoiceOS and Open Interpreter/01 are useful design references or sandbox experiments, but should not become the unattended authority layer for CTOS machines. AirLLM and GLM-family work are model-serving questions and should be evaluated after the voice/action boundary is stable. GLM-5.2 is interesting for future agent/model research, but no GLM-5.x model is selected as the local runtime for the current T480/core hardware pass.

Implementation note 2026-07-07:

`ctos-voice-v2 open-stt-plan` now records this planned Whisper-class rail as a non-destructive preflight. It emits placement, policy, local tool checks, optional `ctos-core` path probing, and explicitly refuses to install models/services or enable an always-on microphone at this stage. `--target-prepare --target-probe` was used once on 2026-07-07 to create and verify only the planned `/srv/ctos` directories on `ctos-core`.

### CTOS open-ended STT candidate selection

Question:

Which local open-ended STT backend should CTOS test first so the Jarvis path does not depend on exact one-word command recognition?

Sources:

- Wyoming faster-whisper repository, accessed 2026-07-07: https://github.com/rhasspy/wyoming-faster-whisper
- Wyoming Whisper image, accessed/tested 2026-07-07: https://hub.docker.com/r/rhasspy/wyoming-whisper
- Wyoming protocol repository, accessed 2026-07-07: https://github.com/rhasspy/wyoming
- faster-whisper repository, accessed 2026-07-07: https://github.com/SYSTRAN/faster-whisper
- whisper.cpp repository, accessed 2026-07-07: https://github.com/ggml-org/whisper.cpp
- Home Assistant local voice assistant documentation, accessed 2026-07-07: https://www.home-assistant.io/voice_control/voice_remote_local_assistant/

Conclusion:

Use `wyoming-faster-whisper` as the first open-ended STT smoke candidate, but use the official `docker.io/rhasspy/wyoming-whisper` container as the first runnable path on `ctos-core`. It keeps the backend aligned with the Wyoming/Home Assistant voice bus already chosen for CTOS while producing free-form French transcripts for the CTOS planner. Keep `whisper.cpp` and direct `faster-whisper` as fallbacks if the Wyoming wrapper or container path is unreliable. The first helper remains plan-only: it renders a manual smoke sequence and does not install a persistent service or enable an always-on microphone.

Live check 2026-07-07:

The direct upstream venv path cloned and inspected successfully, but `script/setup` failed while building `pysilero-vad` under Python 3.14. `podman run --rm --pull=missing docker.io/rhasspy/wyoming-whisper --help` passed on `ctos-core`. A temporary localhost-only `ctos-open-stt-smoke` container on port `10301` accepted a synthetic French WAV through the CTOS Wyoming client; live microphone samples reached the backend but returned empty transcripts, making T480 audio capture/gain cleanup the next blocker.

### CTOS Jarvis stack selection

Question:

Which open-source/local stack should CTOS use so the Jarvis target becomes usable without months of phrase-by-phrase tuning?

Sources:

- Home Assistant voice control documentation, accessed 2026-07-07: https://www.home-assistant.io/voice_control/
- Home Assistant local voice assistant documentation, accessed 2026-07-07: https://www.home-assistant.io/voice_control/voice_remote_local_assistant/
- Home Assistant Wyoming integration documentation, accessed 2026-07-07: https://www.home-assistant.io/integrations/wyoming/
- Wyoming protocol repository, accessed 2026-07-07: https://github.com/rhasspy/wyoming
- Speech-to-Phrase repository, accessed 2026-07-07: https://github.com/OHF-Voice/speech-to-phrase
- Wyoming faster-whisper repository, accessed 2026-07-07: https://github.com/rhasspy/wyoming-faster-whisper
- Wyoming Whisper container page, accessed 2026-07-07: https://hub.docker.com/r/rhasspy/wyoming-whisper
- Wyoming Piper repository, accessed 2026-07-07: https://github.com/rhasspy/wyoming-piper
- OpenVoiceOS core repository, accessed 2026-07-07: https://github.com/OpenVoiceOS/ovos-core
- Open Interpreter 01 repository, accessed 2026-07-07: https://github.com/OpenInterpreter/01
- AirLLM reference implementation lookup, accessed 2026-07-07: https://github.com/lyogavin/Anima/tree/main/air_llm
- GLM-5.2 / GLM-family repository lookup, accessed 2026-07-07: https://github.com/zai-org/GLM-5

Conclusion:

Use a hybrid mature-stack strategy. Home Assistant Assist/Wyoming is the primary local voice ecosystem target. Speech-to-Phrase remains the deterministic fixed-command rail. Wyoming Whisper/faster-whisper is the open-ended French transcript rail. Piper is the likely local TTS path. Ollama on `ctos-core` remains the first local model runtime. OpenVoiceOS, Leon, Open Interpreter/01, GLM-5.2 family work, and AirLLM-style offload stay in research or sandbox lanes until CTOS has stronger action schemas and hardware headroom. The durable selection is recorded in `ai/jarvis_stack.json`, `context/22_jarvis_stack_selection.md`, and exposed through `ctos-jarvis stack`.

Refresh 2026-07-08:

The operator concern remains valid: tuning missed words one by one will not
scale to the requested Jarvis target. Rechecked the current source set and kept
the same decision. Home Assistant/Wyoming-compatible local components remain the
primary substrate; OpenVoiceOS and Open Interpreter/01 remain references or
sandboxes; GLM-5.2-family and AirLLM-style work remain model/runtime research
after the speech/action boundary is reliable and `ctos-core` has more RAM/GPU
headroom. No new package, service, or action authority was selected in this
refresh.

### CTOS token/cost-efficient AI lane scan

Question:

Can CTOS add a free/cheap AI lane now so routine work does not consume Codex
budget while preserving the existing CTOS action boundary?

Sources:

- 9Router repository and README, accessed 2026-07-09:
  https://github.com/decolua/9router
- 9Router package/API claims via GitHub repository metadata, accessed
  2026-07-09: https://api.github.com/repos/decolua/9router
- Agent Reach repository and README, accessed 2026-07-09:
  https://github.com/Panniantong/Agent-Reach
- Agent Reach English README, accessed 2026-07-09:
  https://github.com/Panniantong/Agent-Reach/blob/main/docs/README_en.md

Conclusion:

9Router is relevant as a local OpenAI-compatible routing/proxy and token-saver
candidate, not as a replacement for CTOS authority. Agent Reach is relevant as
a free read/search capability layer for web, GitHub, YouTube, RSS, and selected
social platforms, but it should be tested in safe/dry-run mode because some
platform paths rely on cookies or browser sessions. The immediate CTOS path is
to add an explicit "cheap/free lane" behind `ctos-jarvis`/`ctos-ai`: local
Ollama first, optional 9Router adapter second, Codex only for high-value edits,
architecture, review, or risky execution.

### CTOS cheap coding client candidate

Question:

Can CTOS try a free/open-source coding client without treating it as a free
Codex replacement or widening the machine-control boundary?

Sources:

- Aider repository, accessed 2026-07-10: https://github.com/Aider-AI/aider
- Aider documentation index, accessed 2026-07-10: https://aider.chat/docs/

Conclusion:

Aider is the first coding-client candidate for the cheap lane, but not an
active CTOS backend yet. It should be tried only through an isolated user-level
install path and explicit file scopes. For now, CTOS exposes `ctos-ai
cheap-lane`, `ctos-ai cheap-plan`, and `ctos-ai code-draft` so the operator can
get local cheap drafts before spending Codex budget. No Aider package, external
provider, or repo-wide context routing was enabled in this step.

### CTOS OpenJarvis / Free Claude Code scan

Question:

Can OpenJarvis or Free Claude Code help CTOS get a more capable free/local
Jarvis and cheaper coding-agent workflow without breaking the current action
boundary?

Sources:

- OpenJarvis repository, accessed 2026-07-10:
  https://github.com/open-jarvis/OpenJarvis
- OpenJarvis project documentation, accessed 2026-07-10:
  https://open-jarvis.github.io/OpenJarvis/
- OpenJarvis project site, accessed 2026-07-10:
  https://openjarvis.stanford.edu/
- OpenJarvis paper, accessed 2026-07-10:
  https://arxiv.org/abs/2605.17172
- Free Claude Code repository, accessed 2026-07-10:
  https://github.com/Alishahryar1/free-claude-code

Conclusion:

OpenJarvis is relevant as a sandbox and architecture source for the CTOS Jarvis
track. It matches the local-first/personal-device target, uses Ollama/local
runtime paths, and exposes useful primitives: skills, scheduled agents,
deep-research, monitoring, local trace optimization, and cost/latency/energy
evaluation. It should not be installed on the host through its one-line
installer yet because its presets include code execution, file I/O, shell
access, scheduled/continuous agents, and OAuth integrations.

Free Claude Code is relevant as a high-risk optional proxy candidate for the
cheap coding lane. It can route Claude Code and Codex traffic through provider
or local backends, including Ollama and llama.cpp, and exposes a local Admin UI.
It is not a free frontier model: useful results still depend on free quotas,
external providers, or local models. Because it injects Codex/Claude launcher
config, proxies prompts/tool traffic, and strips official `OPENAI_*`
credentials from the launched Codex process, CTOS should only test it in an
isolated synthetic repo with no secrets before considering integration.

### CTOS OpenJarvis sandbox install

Question:

Can CTOS install OpenJarvis now as a local voice/chat substrate without giving
it host-wide authority or adding another model runtime?

Sources:

- OpenJarvis repository cloned on 2026-07-10:
  https://github.com/open-jarvis/OpenJarvis
- Upstream OpenJarvis installer inspected on 2026-07-10:
  `scripts/install/install.sh`
- OpenJarvis engine/config docs inspected on 2026-07-10:
  `docs/architecture/engine.md`
- OpenJarvis simple chat guide inspected on 2026-07-10:
  `docs/user-guide/chat-simple.md`
- OpenJarvis env-aware path code inspected on 2026-07-10:
  `src/openjarvis/core/paths.py`
- OpenJarvis update-check code inspected on 2026-07-10:
  `src/openjarvis/cli/_version_check.py`
- uv installer inspected on 2026-07-10:
  https://astral.sh/uv/install.sh

Conclusion:

Yes, but only as a CTOS sandbox. OpenJarvis is installed under
`~/.local/share/ctos/openjarvis` with `OPENJARVIS_HOME` pointed at a dedicated
state directory. CTOS does not run the upstream installer, does not install a
new Ollama runtime, does not pull the upstream default model, does not start
the OpenJarvis background orchestrator, and disables analytics/update checks in
the wrapper environment/config. `ctos-openjarvis` uses the existing
T480-to-ctos-core Ollama tunnel and keeps all system actions behind the CTOS
planner/approval/Codex handoff boundary.

### CTOS browser voice console

Question:

Can CTOS provide a usable voice-chat UI now without adding a new framework,
daemon, network exposure, or direct voice-command authority?

Sources:

- Local CTOS voice wrapper: `scripts/ctos-voice`
- Local CTOS OpenJarvis wrapper: `scripts/ctos-openjarvis`
- Local CTOS dashboard/server pattern: `control/server.py`,
  `scripts/ctos-control`
- Browser APIs used by implementation: `MediaRecorder`, `getUserMedia`
- Python standard library used by implementation: `http.server`,
  `subprocess`

Conclusion:

Yes. Add a separate localhost-only voice console on `127.0.0.1:8770`. Browser
audio is explicitly started/stopped by the operator, converted through existing
`ffmpeg`, transcribed through `ctos-voice`, then sent to `ctos-openjarvis`.
The console has `Chat` and `Codex` modes, but neither mode executes actions.
Audio files stay in `/tmp` and are deleted after each request by default.

### CTOS browser and network visibility V0

Question:

Can CTOS open local web tools now and begin planning traffic visibility without
adding risky or noisy tooling?

Sources:

- Local package metadata: `pacman -Si firefox`, 2026-07-10.
- Arch Firefox package page, accessed 2026-07-10:
  https://archlinux.org/packages/extra/x86_64/firefox/
- Mozilla Firefox project page:
  https://www.mozilla.org/firefox/
- Local packet tooling ownership: `pacman -Qo /usr/bin/tcpdump /usr/bin/tshark`,
  2026-07-10.
- Local versions: `tcpdump --version`, `tshark --version`.
- TShark manual:
  https://www.wireshark.org/docs/man-pages/tshark.html
- tcpdump manual:
  https://www.tcpdump.org/manpages/tcpdump.1.html

Conclusion:

Firefox from Arch `extra` is the right first browser for localhost CTOS tools,
but Codex cannot complete the install without the operator entering sudo in a
real terminal. For traffic visibility, the host already has `tcpdump` and
`tshark`, so CTOS can start with metadata-first `ctos-netwatch` snapshots and
leave Wireshark GUI/ntopng for a later explicit decision.

### CTOS TTS voice quality axis

Question:

Why is the current Jarvis voice hard to understand, and what should CTOS
investigate next?

Sources:

- Local `scripts/ctos-voice` speaker fallback order inspected on 2026-07-10.
- Local command availability on 2026-07-10: `command -v spd-say espeak-ng
  espeak piper mimic3 festival flite`.
- Local packages on 2026-07-10: `pacman -Q speech-dispatcher espeak-ng
  piper-tts flite`.

Conclusion:

The host currently has only `espeak-ng` and `espeak` for TTS output, so harsh
robotic speech is expected. Add a dedicated voice-quality axis before changing
the default: research local French-capable TTS, test Piper voices first, keep
cloud TTS out of scope by default, and add a selector/A-B test path to
`ctos-voice`.

### CTOS Piper TTS trial

Question:

What local voice can replace the harsh `espeak-ng` output without adding cloud
TTS or a broad new authority layer?

Sources:

- Piper project note, accessed 2026-07-10:
  https://github.com/rhasspy/piper
- OHF-Voice Piper continuation, accessed 2026-07-10:
  https://github.com/OHF-Voice/piper1-gpl
- Hugging Face `rhasspy/piper-voices` French `fr_FR/siwis/medium` directory,
  accessed 2026-07-10:
  https://huggingface.co/rhasspy/piper-voices/tree/main/fr/fr_FR/siwis/medium
- Local Arch package search on 2026-07-10: no suitable official `piper-tts`
  package was available; `extra/piper` was unrelated gaming mouse tooling.
- Live local install on 2026-07-10: PyPI `piper-tts 1.4.2` and
  `onnxruntime 1.27.0` installed into
  `~/.local/share/ctos-ai/venvs/piper`.

Conclusion:

Use a local Piper trial with the `fr_FR-siwis-medium` voice. Keep the binary in
a user venv and the model under `~/.local/share/ctos-ai/tts/piper/`. Add
explicit `ctos-voice` probe/setup/test/engine controls and let the Voice
Console use Piper only when readiness is verified. Do not introduce cloud TTS
or a persistent voice daemon in this slice.

### CTOS Voice Console Action Queue V0

Question:

Can the browser voice console start turning speech into real PC actions without
granting arbitrary command execution?

Sources:

- Local CTOS action allowlist: `scripts/ctos-ai actions --json`.
- Local deterministic router: `scripts/ctos-ai route-text --json`.
- Local approval queue commands: `ctos-ai propose`, `approvals`, `show`,
  `approve`, `reject`.
- Local agenda proposal commands: `ctos-ai agenda-propose`,
  `agenda-proposals`, `agenda-confirm`, `agenda-reject`.
- Local parsers: `ai/action_planner.py`, `ai/agenda_parser.py`.

Conclusion:

Yes, but only through the existing CTOS approval stores. Voice Console `Action`
mode previews intent, `Queue last` creates a pending approval or agenda
proposal, and `Approve` executes through `ctos-ai`. Unknown text is not queued,
and the browser has no arbitrary shell endpoint.

### CTOS Voice Console Action Vocabulary V0.1

Question:

How should CTOS handle STT mistakes on high-frequency action words such as
`Kali` without opening broad fuzzy command execution?

Sources:

- Operator voice test on 2026-07-10: transcript missed `Kali`.
- Local Voice Console action router: `control/voice_console.py`.
- Local approval allowlist: `scripts/ctos-ai actions --json`.

Conclusion:

Use a small bounded alias list for observed `Kali` variants and add quick
buttons for Kali start/console/shutdown/checkpoint. The buttons and aliases do
not execute directly; they only feed the existing pending approval queue.

### CTOS-core local large-model feasibility

Question:

What can the current `ctos-core` tower realistically run for local LLM work, and
what would be required for a genuinely large local model?

Sources:

- Local `ctos-core` SSH hardware probe on 2026-07-12:
  ASUS ROG STRIX B550-F GAMING, Ryzen 5 2400G, 5.7 GiB RAM, GTX 1650,
  NVMe 953.9 GiB, SATA SSD 465.8 GiB.
- Local `nvidia-smi` on 2026-07-12:
  NVIDIA GeForce GTX 1650, 4096 MiB VRAM, driver 610.43.02, CUDA UMD 13.3.
- Ollama hardware support, accessed 2026-07-12:
  https://docs.ollama.com/gpu
- llama.cpp README, accessed 2026-07-12:
  https://raw.githubusercontent.com/ggml-org/llama.cpp/master/README.md
- NVIDIA CUDA GPU compute capability reference, accessed 2026-07-12:
  https://developer.nvidia.com/cuda-gpus

Conclusion:

The current tower is suitable for always-on CTOS services, voice/Jarvis
plumbing, and small local models. The GTX 1650 is supported by Ollama's NVIDIA
path, but 4 GiB VRAM and 5.7 GiB system RAM are not enough for a large local
model. A practical large-model target needs a RAM upgrade first, then ideally a
GPU with much more VRAM. CPU/RAM GGUF inference can run larger quantized models
slowly; GPU-backed interactive large models need 12-24+ GiB VRAM depending on
model size and quantization.

### Voice-to-Codex orchestrator intake and current component gate

Question:

Which parts of the operator's proposed voice-to-Codex pipeline already exist,
which requested local components fit the three live nodes, and what is the
smallest supported Codex integration that does not forward a raw transcript?

Sources accessed 2026-07-18:

- Official Codex non-interactive mode and CLI reference:
  https://learn.chatgpt.com/docs/non-interactive-mode
  https://learn.chatgpt.com/docs/developer-commands?surface=cli
- Official Codex sandbox/approval, MCP, and IDE configuration:
  https://learn.chatgpt.com/docs/agent-approvals-security
  https://learn.chatgpt.com/docs/extend/mcp
  https://learn.chatgpt.com/docs/developer-settings?surface=ide
- Qwen3 official release/model cards and Ollama exact tags:
  https://qwenlm.github.io/blog/qwen3/
  https://huggingface.co/Qwen/Qwen3-1.7B
  https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507
  https://ollama.com/library/qwen3/tags
- Gemma 3 official model/QAT documentation and Ollama tags:
  https://ai.google.dev/gemma/docs/core/model_card_3
  https://developers.googleblog.com/en/gemma-3-quantized-aware-trained-state-of-the-art-ai-to-consumer-gpus/
  https://ollama.com/library/gemma3/tags
- Meta Llama family/card and Ollama Llama 3.3 tags:
  https://github.com/meta-llama/llama-models
  https://github.com/meta-llama/llama-models/blob/main/models/llama3_3/MODEL_CARD.md
  https://ollama.com/library/llama3.3/tags
- Ollama context, thinking, and GPU behavior:
  https://docs.ollama.com/context-length
  https://docs.ollama.com/capabilities/thinking
  https://docs.ollama.com/gpu
- faster-whisper/CTranslate2 upstream runtime and release information:
  https://github.com/SYSTRAN/faster-whisper
  https://github.com/SYSTRAN/faster-whisper/releases/tag/v1.2.1
  https://opennmt.net/CTranslate2/hardware_support.html
- whisper.cpp and current release:
  https://github.com/ggml-org/whisper.cpp
  https://github.com/ggml-org/whisper.cpp/releases/tag/v1.9.1
- Silero VAD and current release:
  https://github.com/snakers4/silero-vad
  https://github.com/snakers4/silero-vad/releases/tag/v6.2.1
- Maintained Piper engine, current release, voice documentation, and selected
  French model card:
  https://github.com/OHF-Voice/piper1-gpl
  https://github.com/OHF-Voice/piper1-gpl/releases/tag/v1.5.0
  https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/VOICES.md
  https://huggingface.co/rhasspy/piper-voices/blob/0c9c5d340496a47205a799eb046aab69334a88e9/fr/fr_FR/siwis/medium/MODEL_CARD
- Kokoro official runtime/model/voice inventory:
  https://github.com/hexgrad/kokoro
  https://pypi.org/project/kokoro/
  https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md
- Live local checks on 2026-07-18: T480 OS/CPU/RAM/GPU/tool versions,
  `ctos-audio doctor`, `ctos-voice tts-probe`, `ctos-jarvis status --full`,
  `ctos-voice-v2 doctor`, `ctos-openjarvis status`, `codex --version`,
  `codex exec --help`, `codex login status`, `codex mcp list`, VS Code and
  extension inventory.
- Live key-only SSH checks on 2026-07-18: `ctos-core` and `BXEB` OS, CPU, RAM,
  GPU/driver, tool versions, Ollama version/model inventory, service state,
  runtime backend files, and root-storage headroom. No model was loaded.

Conclusion:

Do not rebuild the voice stack or bulk-install the proposed dependency/model
list. Make Codex the primary coding/reasoning executor through stable
`codex exec`; keep local Ollama only for bounded voice/spec preprocessing.
Replace the current raw printable handoff with a strict local spec compiler,
deterministic validator/redactor, operator preview, and an initial
`--ephemeral --sandbox read-only` Codex runner. Keep MCP optional until a
concrete tool/context need exists. Authentication/quota failures must remain
visible, with no silent local-model downgrade.

For local model evaluation, benchmark the current Qwen2.5 1.5B against exact
`qwen3:1.7b-q4_K_M` and `gemma3:1b-it-qat`; defer 4B until RAM/CUDA work and
reject Llama 3.3 on current hardware because the official family is 70B. The
live `ctos-core` Ollama installation is CPU-only despite the supported GTX
1650; enabling CUDA is a separate coherent package/update decision.

Keep Wyoming/faster-whisper as the integration baseline, compare it with
whisper.cpp using the same real French corpus, and test native Silero VAD in
both instead of adding a VAD service. Keep the existing CTOS energy and
hallucination guards until measurement supports removal. Piper remains the
working TTS default; Kokoro is only a measured `ctos-core` quality challenger.
Use primary upstream material as the decision base; issue trackers, Reddit,
and recent blogs may add secondary operational evidence but are not a required
substitute for official docs/releases.

### EliteBook-to-home private access boundary

Question:

How should an operator on `BXEB` reach the T480-hosted Voice Console from
outside the home without publishing SSH or the loopback web service?

Sources accessed 2026-07-18:

- Tailscale Linux installation and Arch package/unit inventory:
  https://tailscale.com/docs/install/linux
  https://archlinux.org/packages/extra/x86_64/tailscale/
  https://archlinux.org/packages/extra/x86_64/tailscale/files/
- Tailscale NAT traversal, relay, encryption, stable addressing, and MagicDNS:
  https://tailscale.com/docs/reference/connection-types
  https://tailscale.com/docs/integrations/firewalls
  https://tailscale.com/kb/1504/encryption
  https://tailscale.com/docs/concepts/ip-and-dns-addresses
  https://tailscale.com/docs/features/magicdns
- Tailscale policy, device approval, key expiry, standard SSH distinction, and
  public Funnel distinction:
  https://tailscale.com/docs/concepts/device-visibility
  https://tailscale.com/docs/features/access-control/grants
  https://tailscale.com/docs/features/access-control/device-management/device-approval
  https://tailscale.com/docs/features/access-control/auth-keys
  https://tailscale.com/docs/features/tailscale-ssh
  https://tailscale.com/docs/features/tailscale-funnel
- WireGuard and Ubuntu peer-to-site/current boot-persistence guidance:
  https://www.wireguard.com/quickstart/
  https://ubuntu.com/server/docs/how-to/wireguard-vpn/on-an-internal-system/
  https://ubuntu.com/server/docs/how-to/wireguard-vpn/common-tasks/
- OpenSSH server configuration reference:
  https://man.openbsd.org/sshd_config
- Live read-only checks on 2026-07-18: key-only nested `BXEB` -> T480 SSH,
  current LAN addresses, T480 loopback Voice Console behavior, and current
  browser/TTS execution path. Tailscale is not installed on the T480;
  `wireguard-tools` and OpenSSH are present. Service/sleep state still requires
  a live implementation preflight outside the restricted system bus.

Conclusion:

Do not create a public endpoint. The smallest recommended V1 is a private
Tailscale transport with existing key-based OpenSSH kept inside it and the
Voice Console still accessed through a loopback local forward. Do not enable
Tailscale SSH or Funnel initially. Require MFA, device approval, a minimum
`BXEB` -> T480 TCP `22` grant, and hotspot/reboot/sleep tests. This recommendation
still requires operator acceptance of the hosted control-plane/identity tradeoff.
Direct WireGuard remains a slower self-hosted alternative. Neither transport
solves T480 power/sleep availability.

### Voice-to-Codex implementation verification

Question:

Which supported interfaces and local controls are sufficient for a
transcript-free, reviewed, read-only Voice Console handoff to Codex, plus
EliteBook-side Piper playback?

Primary sources accessed 2026-07-18:

- OpenAI Codex non-interactive mode, including `codex exec`, stdin input,
  `--ephemeral`, sandbox selection, and `--output-schema`:
  https://learn.chatgpt.com/docs/non-interactive-mode
- Ollama structured outputs, including supplying a JSON schema through
  `format` and using temperature zero for more deterministic results:
  https://docs.ollama.com/capabilities/structured-outputs
- Ollama generate API, including `stream: false` response behavior:
  https://docs.ollama.com/api/generate
- Live local help/cache verification on 2026-07-18: current Codex manual,
  `codex exec --help`, local Ollama `0.30.8`, Qwen2.5 Coder 1.5B availability,
  Voice Console status, and Piper readiness.

Conclusion:

Use the stable non-interactive Codex CLI with a fixed read-only/ephemeral
argument vector and structured result schema. Ignore user config, suppress
automatic project-instruction loading, and disable web search for this runner.
Use Ollama only as an untrusted local structured compiler; enforce exact
workspace, fields, path ceiling, secrets policy, canonicalization, digest, and
confirmation deterministically. Keep the live cloud run disabled by default
because read-only does not mean non-disclosing, and declared per-file scope is
not an OS read jail. Deliver Piper as a bounded no-store WAV to the browser
rather than playing it on the T480.

Implementation evidence 2026-07-18:

- 48 focused tests pass across schemas, validators, exact runner invocation,
  local compiler failure modes, console preview/run gates, and Piper cleanup.
- Live local compilation, EliteBook-tunnel preview, and EliteBook-tunnel WAV
  transport passed. Human audibility and five French samples remain manual.
- The live Codex task did not start because informed external-disclosure
  approval remains unresolved in open question 52. No fallback was used.

Incident follow-up 2026-07-19:

- HTTP caching standard, `no-store` response semantics:
  https://www.rfc-editor.org/rfc/rfc9111.html#section-5.2.2.5
- Live evidence: the EliteBook used legacy `/api/voice/say` and played Piper on
  the T480 while current source uses `/api/voice/synthesize`; static responses
  lacked explicit cache controls. Build `2026-07-19.3` subsequently loaded
  versioned assets with no-store/no-cache headers; legacy `/api/voice/say`
  returned HTTP 410 without T480 playback.
- Post-fix tunnel evidence: Chat `OK` in about 11 seconds, local Codex preview
  in about 53 seconds with exact explicit-file scope and `runnable=false`, and
  Piper HTTP 200 `audio/wav` with 73260 bytes.

Conclusion: operational browser controls must not rely on heuristic cache
freshness. Version the assets, prohibit storage, detect client/server build
drift, and bind asynchronous results to the mode used at submission.
