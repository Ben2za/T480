# Kali Post-Install Boot

Date: 2026-06-03

Scope: transition `ctos-kali` from installer boot to installed-system boot.

## Result

`ctos-kali` now boots from its installed disk only.

Live result:

- state: `running`
- persistent boot: `hd`
- attached block devices: only disk `vda`
- disk path: `/var/lib/libvirt/ctos/images/ctos-kali.qcow2`
- installer ISO: no longer attached to the domain
- console: visible through virt-manager on Hyprland workspace 2

Update 2026-06-04:

- user reached the installed Kali Xfce desktop after login.
- host-to-guest network check succeeded:
  - `ping -c 2 -W 2 192.168.130.50`
  - result: 2 transmitted, 2 received, 0% packet loss

## Installer Notes

The installer DHCP step failed even though host-side `ctos-nat` was healthy. The guest network was configured manually:

- IP: `192.168.130.50`
- netmask: `255.255.255.0`
- gateway: `192.168.130.1`
- DNS: `192.168.130.1`
- hostname: `ctos-kali`
- domain: empty
- user: `ctos`

No guest password is recorded in this repository.

## Post-Install Transition

The installer VM reached completion but the domain was left in:

- `paused (user)`

There was no active libvirt domain job. The post-install command stopped the paused installer VM, redefined the persistent domain with `libvirt/domains/ctos-kali.xml`, started it, and opened the console:

- `scripts/ctos-kali finalize-install --force-stop --start`

The installed profile:

- removes the installer CDROM
- boots from `vda`
- keeps `ctos-nat`
- keeps 6 GiB RAM and 2 vCPU
- sets installed-guest reboot behavior to restart

## Verification Commands

- `python -m py_compile scripts/ctos-kali`
- `virt-xml-validate libvirt/domains/ctos-kali.xml domain`
- `xmllint --noout libvirt/domains/ctos-kali.xml libvirt/domains/ctos-kali.install.xml`
- `virsh -c qemu:///system --readonly domstate ctos-kali --reason`
- `virsh -c qemu:///system --readonly domjobinfo ctos-kali`
- `scripts/ctos-kali finalize-install --force-stop --start`
- `virsh -c qemu:///system --readonly domstate ctos-kali`
- `virsh -c qemu:///system --readonly domblklist ctos-kali --details`
- `virsh -c qemu:///system --readonly dumpxml --inactive ctos-kali`
- `hyprctl clients`

## Next Steps

- Log into Kali manually as `ctos`.
- Verify guest networking from inside Kali.
- Shut the guest down cleanly.
- Create a baseline snapshot only after the guest is verified.
