# Kali Baseline Snapshot

Date: 2026-06-05 01:25 CEST

Scope: `ctos-kali` post-install baseline, recovery after host battery power-off, and current running disk chain.

## Summary

`ctos-kali` has a post-install disk-only snapshot:

- snapshot: `ctos-kali-post-install-20260604`
- baseline disk: `/var/lib/libvirt/ctos/images/ctos-kali.qcow2`
- active overlay: `/var/lib/libvirt/ctos/snapshots/ctos-kali-post-install-20260604.overlay.qcow2`
- current state after recovery: `running (booted)`

The host battery power-off did not lose the snapshot. After reboot, libvirt still saw the snapshot metadata and the domain still used the overlay as `vda`.

## Verified After Recovery

- `ctos-nat`, `ctos-images`, `ctos-snapshots`, and `ctos-iso` are active, autostarted, and compatible.
- `ctos-kali` started successfully from the overlay disk.
- Guest agent responded after boot.
- Kali internet egress works:
  - `ping -c 2 -W 2 1.1.1.1`: 0% packet loss
- Kali DNS works:
  - `getent hosts deb.debian.org`: returned Debian/Fastly records
- No active voice processes remain:
  - no active `orca`, `speech-dispatcher`, `sd_espeak-ng`, or `sd_dummy`

## Voice Disable State

The reboot revealed that `orca` was being launched by the LightDM greeter as user `lightdm`, not by the `ctos` user session.

Applied guest-side controls:

- `lightdm` GSettings `org.gnome.desktop.a11y.applications screen-reader-enabled=false`
- `ctos` GSettings `org.gnome.desktop.a11y.applications screen-reader-enabled=false`
- XDG autostart override for `lightdm`:
  - `/var/lib/lightdm/.config/autostart/orca-autostart.desktop`
- XDG autostart override for `ctos`:
  - `/home/ctos/.config/autostart/orca-autostart.desktop`
- LightDM greeter config:
  - `a11y-states = -contrast;-font;-keyboard;-reader`
  - `reader = /bin/false`
  - removed `~a11y` from `indicators`
- Reversible package diversion:
  - `/usr/bin/orca` diverted to `/usr/bin/orca.distrib`
  - replacement `/usr/bin/orca` exits immediately

The diversion was necessary because LightDM still launched `orca` despite the greeter and GSettings controls.

## Verification Commands

- `virsh -c qemu:///system --readonly domstate ctos-kali --reason`
- `virsh -c qemu:///system --readonly snapshot-list ctos-kali --tree`
- `virsh -c qemu:///system --readonly domblklist ctos-kali --details`
- `scripts/ctos-libvirt-infra --json status`
- `scripts/ctos-kali snapshot-baseline post-install-20260604 --shutdown --timeout 180`
- `scripts/ctos-kali-agent ping`
- `scripts/ctos-kali-agent run /usr/bin/ping -c 2 -W 2 1.1.1.1`
- `scripts/ctos-kali-agent run /usr/bin/getent hosts deb.debian.org`
- `scripts/ctos-kali-agent run /bin/sh -lc 'ps -eo pid=,stat=,args= ...'`

## Follow-Up

Completed: the user confirmed Kali was clean after login, so a second checkpoint snapshot was created for the voice-fixed state.

## Voice-Fixed Checkpoint

Date: 2026-06-05

Snapshot:

- snapshot: `ctos-kali-voice-fixed-20260605`
- parent disk: `/var/lib/libvirt/ctos/snapshots/ctos-kali-post-install-20260604.overlay.qcow2`
- active overlay: `/var/lib/libvirt/ctos/snapshots/ctos-kali-voice-fixed-20260605.overlay.qcow2`
- current state after restart: `running (booted)`

Snapshot tree:

```text
ctos-kali-post-install-20260604
  |
  +- ctos-kali-voice-fixed-20260605
```

Post-checkpoint verification:

- `virsh -c qemu:///system --readonly domblklist ctos-kali --details`: `vda` points to the voice-fixed overlay.
- `scripts/ctos-kali-agent run /usr/bin/ping -c 2 -W 2 1.1.1.1`: 0% packet loss.
- `scripts/ctos-kali-agent run /usr/bin/getent hosts deb.debian.org`: returned Debian/Fastly records.
- Active voice-process check found no non-zombie `orca`, `speech-dispatcher`, `sd_espeak-ng`, or `sd_dummy`.

Next follow-up: integrate this healthy Kali state into the host `CTRL` cockpit controls.
