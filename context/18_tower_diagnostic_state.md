# Tower Diagnostic State

Date: 2026-06-12

Scope: recovered Windows tower intended to become `ctos-core`.

## Identity

- Current hostname: `DESKTOP-LALFAJ9`
- Current OS: Windows 10 Home / Famille
- Build: `10.0.19045`
- Firmware type: UEFI
- Secure Boot: disabled
- TPM: not present / not ready

## Hardware Summary

- Motherboard: ASUS ROG STRIX B550-F GAMING
- CPU: AMD Ryzen 5 2400G, 4 cores / 8 threads
- RAM visible to Windows: about 6 GiB total
- GPUs:
  - NVIDIA GeForce GTX 1650, about 4 GiB VRAM
  - AMD Radeon Vega 11 integrated graphics
- Network:
  - Intel I225-V Ethernet present but disconnected
  - TP-Link USB Wi-Fi active at `192.168.1.18`
  - TAP-Windows Adapter V9 present with link-local `169.254.123.35`

## Storage Summary

- Disk 1: WDC PC SN720 1 TB NVMe, GPT, current Windows boot/system disk.
- Disk 0: Samsung SSD 850 EVO 500 GB SATA, GPT, healthy, no partitions.
- USB diagnostic key: about 4 GB FAT32.

Important install implication:

The 500 GB Samsung SATA SSD appears empty/unpartitioned from Windows and is the best candidate for a non-destructive first EndeavourOS install target. Do not touch the 1 TB NVMe until Windows preservation is explicitly decided.

## OpenSSH State

- `OpenSSH.Server` capability is installed.
- Installed OpenSSH binaries are coherent at version `9.5.4.1`.
- `sshd -t` passes with `LASTEXITCODE=0`.
- Firewall rule `OpenSSH-Server-In-TCP` exists, is enabled, and allows TCP/22.
- `Start-Service sshd` fails; service exit code is `1067`.
- Manual debug run `sshd.exe -ddd -e` successfully listened on:
  - `::`:22
  - `0.0.0.0`:22

Conclusion:

The network, firewall, binary, host keys, and config are sufficient for `sshd` to listen manually. The remaining failure is specific to running `sshd` through Windows Service Control Manager.

## Health Checks

- DISM CheckHealth: no component store corruption detected.
- SFC verify-only: no integrity violation found.
- WSL executable exists, but no useful WSL distribution state is established yet.
- Hyper-V requirements report firmware virtualization disabled.

## Current Workaround

A temporary USB pack was staged as:

- `ctos_tower_ssh_link/`

It installs the T480 public SSH key into `C:\ProgramData\ssh\administrators_authorized_keys` and starts `sshd` in foreground mode through `sshd.exe -D -e`.

This is a temporary local admin bridge, not a final service policy.

## SSH Bridge Validation

Date: 2026-06-12

- TCP/22 on `192.168.1.18` is reachable from the T480.
- Public-key authentication succeeds as local Windows account `desktop-lalfaj9\admin`.
- Verified command output:
  - `DESKTOP-LALFAJ9`
  - `desktop-lalfaj9\admin`
- Repo helper added and verified:
  - `scripts/ctos-tower test`
  - `scripts/ctos-tower inventory`

Operational note:

The debug foreground mode may exit after one connection. For multi-command work, run `sshd.exe -D -e` in an elevated foreground PowerShell and keep that window open.

Current direct inventory through SSH confirms:

- OS: Windows 10 Famille `10.0.19045` build `19045`.
- CPU: AMD Ryzen 5 2400G, 4 cores / 8 threads.
- RAM: 8 GiB Crucial DIMM visible as physical memory; Windows usable memory remains lower because of reservation/usage.
- Disk 1: 953.87 GiB NVMe, boot/system, 4 partitions.
- Disk 0: 465.76 GiB Samsung SATA SSD, 0 partitions, best EndeavourOS target candidate.
- Network: `Wi-Fi 2` at `192.168.1.18/24`.
- Windows `sshd` service remains `Stopped` / `Manual`; active access depends on the foreground `sshd.exe` process.
