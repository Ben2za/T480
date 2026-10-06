# Libvirt Inventory

Date: 2026-06-02

Scope: read-only libvirt inventory for the host cockpit. No VM disk contents, secrets, logs, or browser state were read.

Note: this file records the pre-CTOS-infra inventory. Live CTOS network/pool state after applying repo-owned infrastructure is recorded in `context/12_libvirt_infra_state.md`.

## Summary

The T480 has libvirt/QEMU installed and storage pools configured, but no libvirt domains are currently defined on either checked connection:

- `qemu:///system`: no domains.
- `qemu:///session`: no domains.

The existing Kali disk is a qcow2 allocation stub, not an installed Kali VM. Treat Kali as not yet built.

## Installed Virtualization Packages

- `libvirt 1:12.3.0-1`
- `virt-manager 5.1.0-3`
- `qemu-full 11.0.0-1`
- `dnsmasq 2.92.rel2-2`
- `edk2-ovmf 202605-1`
- `bridge-utils`: not installed

Runtime versions reported by `virsh -c qemu:///system --readonly version`:

- libvirt library: `12.3.0`
- QEMU API: `12.3.0`
- running hypervisor: `QEMU 11.0.0`

## Host Capacity Visible To Libvirt

`virsh -c qemu:///system --readonly nodeinfo`:

- CPU model: `x86_64`
- CPUs: `8`
- CPU topology: `1` socket, `4` cores per socket, `2` threads per core
- Memory size: `16257376 KiB`

This confirms the working constraint from the roadmap: with about 16 GiB RAM, Kali, Dev, AI workers, and game mode must be mode-budgeted rather than always-on.

## Domains

Commands:

- `virsh -c qemu:///system --readonly list --all`
- `virsh -c qemu:///session --readonly list --all`

Result:

- No system domains.
- No session domains.

## Networks

System connection:

- `default`: active, autostart yes, persistent yes
- bridge: `virbr0`
- UUID: `d7ff2733-4b32-48d8-a218-e01517daac62`

Session connection:

- No networks listed during the CLI inventory.

## Storage Pools And Volumes

System pools:

- `default`: active, autostart yes
  - capacity `236.46 GiB`
  - allocation `16.49 GiB`
  - available `219.96 GiB`
  - volume: `kali.qcow2`
  - path: `/var/lib/libvirt/images/kali.qcow2`
  - virtual capacity: `40.00 GiB`
  - allocation: `196.00 KiB`
- `iso`: active, autostart yes
  - capacity `236.46 GiB`
  - allocation `16.49 GiB`
  - available `219.96 GiB`
  - volume: `kali-linux-2025.4-installer-amd64.iso`
  - path: `/home/operator/iso/kali-linux-2025.4-installer-amd64.iso`
  - capacity/allocation: `4.41 GiB`

Session pools:

- `images`: active, autostart yes
  - volume: `kali.qcow2`
  - path: `/var/lib/libvirt/images/kali.qcow2`
  - virtual capacity: `40.00 GiB`
  - allocation: `196.00 KiB`
- `iso`: active, autostart yes
  - volume: `kali-linux-2025.4-installer-amd64.iso`
  - path: `/home/operator/iso/kali-linux-2025.4-installer-amd64.iso`
  - capacity/allocation: `4.41 GiB`

Filesystem metadata:

- `/var/lib/libvirt/images/kali.qcow2`: `197248` bytes, owner `nobody:nobody`, mode `-rw-r--r--`
- `/home/operator/iso/kali-linux-2025.4-installer-amd64.iso`: `4733116416` bytes, owner `nobody:nobody`, mode `-rw-r--r--`

`qemu-img info /var/lib/libvirt/images/kali.qcow2` reports:

- file format: `qcow2`
- virtual size: `40 GiB`
- disk size: `196 KiB`
- corrupt: `false`

## Domain XML Reality

Checked paths:

- `/etc/libvirt/qemu`
- `/home/operator/.config/libvirt/qemu`

Only `/etc/libvirt/qemu/networks/default.xml` exists. No domain XML file was found in the checked paths.

## Operational Conclusions

- Do not expose Kali as a real VM in the cockpit yet; expose it as planned/not built.
- The next safe automation layer is read-only `scripts/ctos-vm list/status/inspect`.
- Start/stop/snapshot actions remain out of scope until the VM lifecycle model, storage ownership, and snapshot policy are documented.
- Future Kali and Dev domains should be defined from repo-owned libvirt XML or an equivalent declarative script, not manual virt-manager state.

## Verification Commands

- `virsh -c qemu:///system --readonly list --all`
- `virsh -c qemu:///session --readonly list --all`
- `virsh -c qemu:///system --readonly net-list --all`
- `virsh -c qemu:///system --readonly pool-list --all`
- `virsh -c qemu:///session --readonly pool-list --all`
- `virsh -c qemu:///system --readonly vol-list default --details`
- `virsh -c qemu:///system --readonly vol-list iso --details`
- `virsh -c qemu:///session --readonly vol-list images --details`
- `virsh -c qemu:///session --readonly vol-list iso --details`
- `virsh -c qemu:///system --readonly version`
- `virsh -c qemu:///system --readonly nodeinfo`
- `qemu-img info /var/lib/libvirt/images/kali.qcow2`
