# Tower ctos-core Install V1

Date: 2026-06-12

Scope: same-day preparation to wipe the recovered Windows tower and install EndeavourOS as the first `ctos-core` node.

## Decision

Proceed with a Windows wipe and bare-metal EndeavourOS install on the tower.

Install path:

1. Use the official EndeavourOS installer USB.
2. Install to the 1 TB WDC NVMe.
3. Use Xfce for V1 because the tower currently has only 8 GiB RAM and the priority is a recoverable central node.
4. Apply the CTOS role after first boot with `bootstrap/ctos-apply-role`.
5. Initialize the 500 GB Samsung SATA SSD separately as `/srv/ctos` with `bootstrap/ctos-init-core-storage`, only after confirming the disk identity with `lsblk` and `/dev/disk/by-id`.

## New Repo Artifacts

- `docs/TOWER_CTOS_CORE_INSTALL.md`: operator runbook for the afternoon install.
- `bootstrap/manifests/base.pacman`: recovery and base tools.
- `bootstrap/manifests/desktop-xfce.pacman`: first desktop baseline.
- `bootstrap/manifests/dev.pacman`: daily development baseline.
- `bootstrap/manifests/core.pacman`: core node virtualization/container packages.
- `bootstrap/manifests/aur.optional`: explicitly deferred AUR packages.
- `bootstrap/ctos-apply-role`: post-install role apply helper.
- `bootstrap/ctos-init-core-storage`: guarded SATA-to-`/srv/ctos` helper.
- `bootstrap/roles/ctos-core/README.md`: role scope.

## Guardrails

- No CTOS script wipes the OS disk.
- The SATA helper refuses the current root disk and mounted disks.
- AUR packages are not installed by V1 bootstrap.
- Secrets, private keys, tokens, logs, VM disks, and caches stay out of the repo and USB kit.
- Heavy AI/runtime services are deferred until RAM/PSU/GPU/CPU decisions are settled.

## Verification

Completed on the T480 before USB staging:

- `bash -n bootstrap/ctos-apply-role`
- `bash -n bootstrap/ctos-init-core-storage`
- `bootstrap/ctos-apply-role ctos-core plan`
- all non-group pacman package names in the manifests resolve with local `pacman -Si`
- `xfce4` and `xfce4-goodies` resolve as local pacman groups with `pacman -Sgq`
- `scripts/ctos-build-usb-kit /tmp/ctos-core-kit-clean3-2`
- staged kit contains the role scripts and `docs/TOWER_CTOS_CORE_INSTALL.md`

Physical USB copy status:

- `/tmp/ctos-usb` was initially present but stale; `/dev/sdb` disappeared while the mountpoint remained.
- After replug, the 3.8 GiB FAT USB mounted as `/dev/sdc` with about 3.8 GiB free.
- `ctos-core-kit` was copied to `/tmp/ctos-usb/ctos-core-kit`.
- Required files were verified:
  - `bootstrap/ctos-apply-role`
  - `bootstrap/ctos-init-core-storage`
  - `docs/TOWER_CTOS_CORE_INSTALL.md`
- `sync` completed.
- Unmount requires the operator sudo password: `sudo umount /tmp/ctos-usb`.

## Open Follow-Ups

- Confirm exact PSU model before RX 6600 installation.
- Update ASUS BIOS before Ryzen 7 5700X installation.
- Upgrade RAM to 32 GiB minimum, 64 GiB preferred, before making `ctos-core` an AI/VM-heavy node.
- Decide whether `ctos-core` should eventually expose LAN Git/package/model cache services.
- Network recovery after offline install: `ctos-core-netfix` is staged on the CTOS USB and should be used to capture tower-side reports until SSH/network works.
- Ethernet rescue after T480 cable link: `ctos-ethernet-rescue` is staged on the CTOS USB and should be run first with `sudo ./ctos-ethernet-rescue auto`.
- Latest Ethernet rescue result: tower can reach T480 over `10.42.0.2 -> 10.42.0.1`, but Internet egress still needs the T480-side `sudo scripts/ctos-firewall-fix-tower-egress` runtime fix.
- Latest T480-side test: `ping 10.42.0.2` works from T480. SSH is now enabled and key auth works for `ctos@10.42.0.2`.
- Internet and DNS work from the tower through the T480 shared Ethernet link.

## Live Tower Post-Install Snapshot

Date: 2026-06-14

- Hostname: `ctos-core`
- OS: EndeavourOS
- Kernel: `6.18.4-arch1-1`
- User: `ctos`
- Board: ASUS ROG STRIX B550-F GAMING
- BIOS: `1401`, firmware date 2020-12-03
- CPU: AMD Ryzen 5 2400G, 4 cores / 8 threads
- RAM visible: about 5.7 GiB
- Swap: about 512 MiB
- Network: `enp6s0` static `10.42.0.2/24`, gateway `10.42.0.1`
- Disk:
  - NVMe 1 TB WDC PC SN720: EndeavourOS Btrfs root/home/cache/log/swap
  - SATA 500 GB Samsung 850 EVO: unpartitioned / unused

Verified:

- `ssh -F /dev/null -o BatchMode=yes ctos@10.42.0.2 ...`
- `ping 1.1.1.1`: 0% packet loss
- `ping endeavouros.com`: 0% packet loss

## Bootstrap Apply Attempt 1

Date: 2026-06-15

The first `bootstrap/ctos-apply-role ctos-core apply` attempt reached `pacman -Syu --needed` dependency resolution but stopped before package transaction completion.

Observed afterward from the T480:

- `/etc/ctos-role`: missing
- `/var/lib/pacman/db.lck`: absent
- running `pacman`: absent
- running bootstrap process: absent
- `/opt/ctos/repo` and `/srv/ctos/*`: not created
- major role packages such as `qemu-full`, `libvirt`, `podman`, `xfce4-session`, and `lightdm`: still absent

Cause:

The manifests still contained pacman groups `xfce4` and `xfce4-goodies`, producing large interactive selection prompts. The package transaction was not committed.

Fix staged:

- Replaced `xfce4` and `xfce4-goodies` with explicit Xfce package names.
- Added explicit `crun` runtime provider for container tooling.
- Re-copied the corrected repo to `/home/ctos/T480` on the tower.
- Verified the remote plan now reports `NO_XFCE_GROUPS` and `CRUN_PRESENT`.

## Bootstrap Apply Completion

Date: 2026-06-15

The corrected `ctos-core` role apply completed after refreshing the Arch and EndeavourOS keyring packages first.

Verified from the T480 over SSH:

- `/etc/ctos-role` exists with `role=ctos-core`.
- `NetworkManager`, `sshd`, and `avahi-daemon` are active.
- Existing display manager was preserved: `/usr/lib/systemd/system/sddm.service`.
- `/opt/ctos/repo` exists.
- `/srv/ctos/cache`, `/srv/ctos/models`, `/srv/ctos/workers`, `/srv/ctos/snapshots`, and `/srv/ctos/packages` exist with group `ctos`.
- Key role packages are installed: `qemu-full`, `libvirt`, `podman`, `podman-compose`, `xfce4-session`, `lightdm`, and `crun`.
- DNS works through the T480 Ethernet rescue link.

Temporary sudo handling:

- User installed the temporary rule through `bootstrap/ctos-enable-bootstrap-sudo`.
- `bootstrap/ctos-apply-role ctos-core cleanup-sudo` removed `/etc/sudoers.d/ctos-bootstrap`.
- Follow-up `sudo -n` check now returns `sudo: a password is required`, confirming the passwordless bootstrap path is closed.

Remaining required action:

- Decide whether the SATA SSD should be initialized as `/srv/ctos`.

## Post-Reboot Validation

Date: 2026-06-15

After reboot, verified from the T480 over SSH:

- Hostname remains `ctos-core`.
- Running kernel is now `7.0.12-arch1-1`, matching installed package `linux 7.0.12.arch1-1`.
- `/etc/ctos-role` remains present.
- `NetworkManager`, `sshd`, and `avahi-daemon` are active.
- Existing display manager remains SDDM.
- Ethernet rescue link is up on `enp6s0 = 10.42.0.2/24`.
- Ping to the T480 gateway `10.42.0.1` works.
- DNS works through the T480 link.
- `sudo -n` reports that a password is required, confirming no passwordless bootstrap sudo remains.

## Post-Welcome Audit And SATA Candidate

Date: 2026-06-15

After the EndeavourOS Welcome tasks selected by the operator, verified from the T480 over SSH:

- Kernel remains `7.0.12-arch1-1`.
- SDDM remains active as display manager.
- `NetworkManager`, `sshd`, `avahi-daemon`, and `display-manager` are active.
- No failed systemd units.
- No pacman database lock.
- T480 gateway and DNS still work.
- RAM pressure is low: about 3.9 GiB available of 5.7 GiB visible, with swap unused.

Disk identity:

- OS disk: `/dev/disk/by-id/nvme-WDC_PC_SN720_SED_SDAQNTW-1T00_193915800317` -> `/dev/nvme0n1`.
- EFI partition: `/dev/nvme0n1p1` mounted at `/efi`.
- EndeavourOS Btrfs partition: `/dev/nvme0n1p2` mounted as `/`, `/home`, `/var/cache`, `/var/log`, and `/swap`.
- SATA service candidate: `/dev/disk/by-id/ata-Samsung_SSD_850_EVO_500GB_S3R3NF1JB01054J` -> `/dev/sda`.
- SATA size: 465.8 GiB.
- SATA current state: disk visible, unmounted, no filesystem/partition shown by `lsblk`.

Non-destructive storage plan verified:

```text
Target disk: /dev/sda
Mountpoint:  /srv/ctos
Filesystem:  Btrfs
Label:       CTOS_SRV
Fstab opts:  noatime,compress=zstd:3
```

The next destructive action, if accepted by the operator, is to run `bootstrap/ctos-init-core-storage apply` against the SATA by-id path.

## SATA Service Disk Initialized

Date: 2026-06-15

The operator ran the destructive storage apply for the Samsung SATA SSD.

Final verified state:

- Source disk: `/dev/disk/by-id/ata-Samsung_SSD_850_EVO_500GB_S3R3NF1JB01054J` -> `/dev/sda`.
- Partition: `/dev/sda1`.
- Filesystem: Btrfs.
- Label: `CTOS_SRV`.
- UUID: `d7db0dbc-63ea-4add-a609-5bde6783bd5f`.
- Mountpoint: `/srv/ctos`.
- Effective mount options include `rw,noatime,compress=zstd:3,ssd,discard=async,space_cache=v2`.
- Capacity: about 466 GiB, about 464 GiB available.
- `/etc/fstab` contains `UUID=d7db0dbc-63ea-4add-a609-5bde6783bd5f /srv/ctos btrfs noatime,compress=zstd:3 0 0`.
- `/srv/ctos` and expected subdirectories are group-owned by `ctos` with setgid permissions.
- A non-root write test as user `ctos` succeeded.

The NVMe OS disk remains unchanged:

- `/dev/nvme0n1p1` mounted at `/efi`.
- `/dev/nvme0n1p2` mounted as `/`, `/home`, `/var/cache`, `/var/log`, and `/swap`.

## T480 Control Link

Date: 2026-06-15

Added the first T480-side control integration for `ctos-core`.

- Helper: `scripts/ctos-core`.
- Default target: `ctos@10.42.0.2`.
- Commands: `status`, `status --json`, `ssh`, and `ping`.
- Boundary: status-only by default; no sudo, package changes, service mutation, reboot, or storage mutation.
- Cockpit: `control/status.py` includes cached `core` status; terminal TUI renders `CTOS CORE`; web dashboard renders a `Core Node` panel.

Verified:

- `scripts/ctos-core status`.
- `scripts/ctos-core status --json`.
- `control.status.snapshot()` includes `core.available=true`.
- Local `/api/status` includes `core.hostname=ctos-core`, `core.storage.srv.source=/dev/sda1`, `core.storage.srv.writable=true`, and `core.sudo_password_required=true`.

## Services V1 Layout

Date: 2026-06-15

Added and applied the first lightweight service/storage layout under `/srv/ctos`.

T480 commands:

- `scripts/ctos-core plan-services`
- `scripts/ctos-core apply-layout`
- `scripts/ctos-core sync-repo --dry-run`
- `scripts/ctos-core sync-repo`

Created directories:

- `/srv/ctos/repo/t480`
- `/srv/ctos/packages/pacman/pkg`
- `/srv/ctos/packages/incoming`
- `/srv/ctos/cache/git`
- `/srv/ctos/cache/python`
- `/srv/ctos/cache/node`
- `/srv/ctos/models/ollama`
- `/srv/ctos/models/huggingface`
- `/srv/ctos/workers/queue`
- `/srv/ctos/workers/active`
- `/srv/ctos/workers/done`
- `/srv/ctos/workers/failed`
- `/srv/ctos/state`

Verification:

- `/srv/ctos/state/layout-v1.json` exists.
- `scripts/ctos-core status --json` reports `layout.complete=true`.
- Repo subset synced to `/srv/ctos/repo/t480`.
- Repo copy size is about 804 KiB.
- Dashboard `/api/status` reports `core.layout.complete=true` and `core.layout.marker_exists=true`.

Boundary:

This step does not install packages, enable daemons, open LAN ports, run sudo, or change system services.
