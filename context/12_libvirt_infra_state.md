# Libvirt CTOS Infra State

Date: 2026-06-03

Scope: live state after applying the repo-owned CTOS libvirt infrastructure. No VM domains or VM disks were created in this step.

## Applied Resources

Command:

- `scripts/ctos-libvirt-infra apply`

Result:

- `ctos-nat`: defined, active, autostart yes.
- `ctos-images`: defined, active, autostart yes.
- `ctos-snapshots`: defined, active, autostart yes.
- `ctos-iso`: defined, active, autostart yes.

The apply command reported no post-apply drift:

- `ctos-nat`: ready, no pending actions.
- `ctos-images`: ready, no pending actions.
- `ctos-snapshots`: ready, no pending actions.
- `ctos-iso`: ready, no pending actions.

## Domain State

No libvirt domains exist after this step:

- `virsh -c qemu:///system --readonly list --all`: no domains.
- `scripts/ctos-vm status`: system and session domains none.

## Network State

System networks:

- `ctos-nat`: active, autostart yes, persistent yes.
- `default`: active, autostart yes, persistent yes.

`ctos-nat` live XML:

- bridge: `virbr-ctos`
- forward mode: NAT
- host IP: `192.168.130.1/24`
- DHCP range: `192.168.130.100` to `192.168.130.254`

Observed routes:

- host LAN: `192.168.1.0/24` via `wlan0`
- libvirt default: `192.168.122.0/24` via `virbr0`
- CTOS NAT: `192.168.130.0/24` via `virbr-ctos`

## Storage Pool State

System pools:

- `ctos-images`: active, autostart yes.
- `ctos-snapshots`: active, autostart yes.
- `ctos-iso`: active, autostart yes.
- `default`: active, autostart yes.
- `iso`: active, autostart yes.

CTOS paths:

- `/var/lib/libvirt/ctos`
- `/var/lib/libvirt/ctos/images`
- `/var/lib/libvirt/ctos/snapshots`
- `/var/lib/libvirt/ctos/iso`

Observed filesystem metadata:

- `/var/lib/libvirt/ctos`: owner `nobody:nobody`, mode `drwxr-xr-x`
- `/var/lib/libvirt/ctos/images`: owner `nobody:nobody`, mode `drwx--x--x`
- `/var/lib/libvirt/ctos/snapshots`: owner `nobody:nobody`, mode `drwx--x--x`
- `/var/lib/libvirt/ctos/iso`: created later for installer media; see `context/14_kali_install_start.md`

Live `pool-dumpxml` reports target paths:

- `ctos-images`: `/var/lib/libvirt/ctos/images`
- `ctos-snapshots`: `/var/lib/libvirt/ctos/snapshots`
- `ctos-iso`: `/var/lib/libvirt/ctos/iso`

## Verification Commands

- `scripts/ctos-libvirt-infra plan`
- `scripts/ctos-libvirt-infra apply`
- `scripts/ctos-libvirt-infra status`
- `scripts/ctos-vm status`
- `virsh -c qemu:///system --readonly list --all`
- `virsh -c qemu:///system --readonly net-list --all`
- `virsh -c qemu:///system --readonly pool-list --all`
- `virsh -c qemu:///system --readonly net-dumpxml ctos-nat`
- `virsh -c qemu:///system --readonly pool-dumpxml ctos-images`
- `virsh -c qemu:///system --readonly pool-dumpxml ctos-snapshots`
- `ip addr show virbr-ctos`
- `ip route`
- `stat -c "%n %U:%G %A" /var/lib/libvirt/ctos /var/lib/libvirt/ctos/images /var/lib/libvirt/ctos/snapshots`

## Operational Conclusion

The host is now ready for the next VM step: define `ctos-kali` against `qemu:///system`, `ctos-nat`, and `ctos-images`.

Do not define or install Kali until the domain XML/profile and disk creation command are documented.
