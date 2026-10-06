# Tower `ctos-core` Install Runbook

Date: 2026-06-12

Goal: wipe the recovered Windows tower and install EndeavourOS as the first `ctos-core` node.

## Current Tower Baseline

- Board: ASUS ROG STRIX B550-F GAMING.
- Current CPU: Ryzen 5 2400G.
- Current RAM: 8 GiB.
- Current GPU: GTX 1650 plus Vega iGPU.
- Future parts: Ryzen 7 5700X and RX 6600.
- Current disks:
  - 1 TB WDC NVMe with Windows.
  - 500 GB Samsung SATA SSD, currently empty from Windows.

## V1 Decision

Install EndeavourOS now on the 1 TB NVMe and remove Windows.

Use a simple Xfce desktop for the first boot. The tower currently has only 8 GiB RAM, and the first mission is a stable central node, not visual polish. KDE/Hyprland can come after RAM/GPU/CPU upgrades and after the CTOS role scripts are proven.

Do not automate destructive disk selection inside CTOS scripts. The EndeavourOS installer handles the OS disk. The SATA disk is initialized only after first boot with `bootstrap/ctos-init-core-storage`.

## Before Booting The Installer

1. Keep the T480 nearby with this repo open.
2. Plug power and Ethernet if available. Wi-Fi is acceptable but Ethernet is better.
3. If installing the RX 6600 before the OS install:
   - verify the PSU model and a native PCIe 8-pin cable first;
   - plug the monitor into the RX 6600, not the motherboard.
4. If swapping to Ryzen 7 5700X before install:
   - update the ASUS BIOS first;
   - install a proper cooler;
   - keep a discrete GPU installed because 5700X has no iGPU.

For same-day install, the safest path is: install EndeavourOS on current hardware first, upgrade GPU/CPU after the system is recoverable.

## EndeavourOS Installer Choices

Use the official EndeavourOS USB.

Suggested choices:

- Install method: Online if network works; Offline/Xfce if online mirrors are slow.
- Desktop: Xfce for V1.
- Boot mode: UEFI.
- Partitioning: erase the 1 TB NVMe.
- Filesystem: Btrfs if offered; otherwise ext4 is acceptable for the first install.
- Swap: enable swap. With 8 GiB RAM, do not skip it.
- Hostname: `ctos-core`.
- User: your normal local user. Do not use `operator` if you want to keep tower and T480 accounts mentally separate.

Important disk check:

- The NVMe is the 1 TB WDC PC SN720.
- The SATA SSD is the 500 GB Samsung 850 EVO.
- If you are unsure which disk is selected, stop and send a screenshot.

## First Boot

After first login:

```bash
sudo pacman -Syu --needed git rsync
```

Mount or copy the CTOS kit, then from the kit root:

```bash
bootstrap/ctos-apply-role ctos-core plan
sudo bootstrap/ctos-apply-role ctos-core apply
```

If you want the non-interactive path after reading the plan:

```bash
sudo bootstrap/ctos-apply-role ctos-core apply --yes
```

Reboot.

## T480 Connectivity Check

From the T480:

```bash
ssh <tower-user>@ctos-core.local
```

If mDNS is not visible yet, use the tower IP from its network panel:

```bash
ssh <tower-user>@<tower-ip>
```

## SATA `/srv/ctos` Initialization

Only after the OS is booted and the NVMe install is confirmed, inspect disks:

```bash
lsblk -o NAME,SIZE,TYPE,FSTYPE,LABEL,MOUNTPOINTS,MODEL
```

Find the Samsung 500 GB SATA disk. Prefer a stable path:

```bash
ls -l /dev/disk/by-id/ | grep -i samsung
```

Dry-run the CTOS storage helper:

```bash
sudo bootstrap/ctos-init-core-storage plan --device /dev/disk/by-id/<samsung-ssd-id>
```

Apply only if the plan shows the Samsung 500 GB SATA SSD, not the NVMe:

```bash
sudo bootstrap/ctos-init-core-storage apply --device /dev/disk/by-id/<samsung-ssd-id> --yes-i-understand-this-wipes
```

## After Install

First real checks:

```bash
hostnamectl
systemctl status sshd --no-pager
systemctl status avahi-daemon --no-pager
findmnt /srv/ctos
fastfetch
```

Then we can continue from the T480 and turn `ctos-core` into the fleet brain step by step.

## Offline Network Recovery

If the tower boots but Wi-Fi or iPhone tethering is unstable, use the CTOS USB netfix pack:

```bash
cd /run/media/*/*/ctos-core-netfix 2>/dev/null || cd /mnt/ctos-core-netfix
./ctos-core-netfix diag
sudo ./ctos-core-netfix iphone
sudo ./ctos-core-netfix wifi
```

Bring the USB back to the T480 and inspect `outputs/netdiag-*/report.txt` if it still fails.

## Ethernet Rescue Through T480

If the tower is connected directly to the T480 by Ethernet, the T480 can share its Wi-Fi connection on `10.42.0.1/24`.

On the tower, from the CTOS USB:

```bash
cd /run/media/*/*/ctos-ethernet-rescue 2>/dev/null || cd /mnt/ctos-ethernet-rescue
sudo ./ctos-ethernet-rescue auto
```

If `auto` fails, run:

```bash
sudo ./ctos-ethernet-rescue dhcp
sudo ./ctos-ethernet-rescue static
./ctos-ethernet-rescue diag
```

Bring the USB back to the T480 and inspect `ctos-ethernet-rescue/outputs/` if it still fails.
