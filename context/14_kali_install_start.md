# Kali Install Start

Date: 2026-06-03

Scope: first visible start of the CTOS Kali install-phase domain.

## Result

`ctos-kali` is running and the graphical console is visible through virt-manager on Hyprland workspace 2.

The Kali installer remains manual. No unattended install, guest credential, post-install package selection, or snapshot was created in this step.

## Important Blocker And Fix

Initial `scripts/ctos-kali start-install` failed because QEMU could not open:

- `/home/operator/iso/kali-linux-2025.4-installer-amd64.iso`

Root cause:

- `/home/operator` is mode `drwx------`, so the QEMU/libvirt process cannot traverse the operator home directory even though the ISO file itself was readable.

Fix:

- Added pool `ctos-iso`: `/var/lib/libvirt/ctos/iso`
- Imported the Kali ISO into `ctos-iso` through libvirt storage APIs:
  - `virsh vol-create-as ctos-iso kali-linux-2025.4-installer-amd64.iso <size> --format raw`
  - `virsh vol-upload kali-linux-2025.4-installer-amd64.iso /home/operator/iso/kali-linux-2025.4-installer-amd64.iso ctos-iso`
- Updated `libvirt/domains/ctos-kali.install.xml` so the CDROM points to:
  - `/var/lib/libvirt/ctos/iso/kali-linux-2025.4-installer-amd64.iso`
- Redefined the inactive domain using a temporary XML containing the live UUID; the repo XML remains UUID-free.

## Current Live State

`ctos-kali`:

- state: `running`
- domain id: `2`
- vCPU: `2`
- memory: `6291456 KiB`
- autostart: disabled
- managed save: no
- snapshots: none

Block devices:

- disk `vda`: `/var/lib/libvirt/ctos/images/ctos-kali.qcow2`
- cdrom `sda`: `/var/lib/libvirt/ctos/iso/kali-linux-2025.4-installer-amd64.iso`

Network:

- interface: `vnet1`
- source: `ctos-nat`
- model: `virtio`

Viewer:

- `virt-viewer` could connect in foreground but did not remain detached reliably in this session.
- `virt-manager --show-domain-console` launched correctly when started through:
  - `hyprctl dispatch exec "virt-manager -c qemu:///system --show-domain-console ctos-kali"`

## Verification Commands

- `scripts/ctos-kali start-install`
- `scripts/ctos-libvirt-infra apply`
- `scripts/ctos-kali prepare-media`
- `scripts/ctos-kali define`
- `scripts/ctos-kali start-install`
- `scripts/ctos-kali start-install --no-viewer`
- `scripts/ctos-vm inspect ctos-kali`
- `virsh -c qemu:///system --readonly domstate ctos-kali`
- `virsh -c qemu:///system --readonly domblklist ctos-kali --details`
- `virsh -c qemu:///system --readonly domiflist ctos-kali`
- `hyprctl clients`

## Next Steps

- Complete the Kali installer manually in the visible console.
- After install, shut down the guest cleanly.
- Add a post-install domain transition that removes or deprioritizes the installer ISO.
- Create a baseline snapshot only after the installed guest is cleanly shut off.
