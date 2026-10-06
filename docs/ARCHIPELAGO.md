# CTOS Archipelago

The CTOS fleet model keeps EndeavourOS as the common base while separating machine roles.

## Roles

- `ctos-t480`: mobile admin, cockpit, daily coding/work machine.
- `ctos-core`: recovered desktop tower after reinstall; heavy workers, local caches, AI/runtime capacity, richer visual desktop.
- `ctos-zlitebook`: existing Ubuntu laptop reconnected as an SSH-managed worker candidate; not yet a CTOS EndeavourOS role target.
- `ctos-worker-*`: additional EndeavourOS machines that receive role updates and run selected workers.
- `ctos-lab`: VM/lab boundary for Kali and authorized security workflows.

## Bootstrap Shape

First version:

1. Install EndeavourOS with the official installer.
2. Copy or mount the CTOS USB kit.
3. Pull/apply the repo role for the machine.

The first concrete target is the recovered tower as `ctos-core`. Its wipe/install runbook is `docs/TOWER_CTOS_CORE_INSTALL.md`, and its first role bootstrap is:

```bash
bootstrap/ctos-apply-role ctos-core plan
sudo bootstrap/ctos-apply-role ctos-core apply
```

Later version:

- Use EndeavourOS installer customization files for a tighter one-USB flow after manifests and scripts are proven.

## Rule

Every node should be recoverable from the repo plus a small bootstrap kit. The tower can accelerate the fleet, but it should not become a hidden single point of failure.

## Current Core Link

`ctos-core` is now an EndeavourOS node reachable from the T480 over the Ethernet rescue link:

- SSH target: `ctos@10.42.0.2`
- T480 helper: `scripts/ctos-core status`
- Cockpit integration: status-only `ctos-core` card in the local control dashboard and terminal TUI.
- Service storage: Samsung SATA SSD mounted as `/srv/ctos` with Btrfs label `CTOS_SRV`.
- First service layout: `scripts/ctos-core apply-layout` creates repo, package, cache, model, worker, and state directories under `/srv/ctos` without enabling daemons.
- Repo transfer: `scripts/ctos-core sync-repo` copies a safe repo subset to `/srv/ctos/repo/t480`.
- Fleet inventory: `scripts/ctos-fleet status` aggregates T480 and ctos-core live status from `fleet/nodes.json`.
- Remote control V0: `scripts/ctos-remote status` and `scripts/ctos-remote plan` inventory tunnel-first desktop-control readiness without installing or exposing any service.

## Current ZLiteBook Link

The former bootstrap laptop is reachable from the T480 on the Wi-Fi LAN:

- SSH target: `ben@192.168.1.24`
- Hostname: `BXEB`
- OS: Ubuntu 24.04
- Observed service: nginx on TCP `8080` serving `Snake Surge`
- Fleet integration: status-only SSH read through `scripts/ctos-fleet`.

It is intentionally tracked as `worker-candidate`, not as a finished CTOS node.
Do not apply EndeavourOS role scripts or worker services to it until its role,
OS target, and data-retention boundary are explicitly decided.

## Planned Feature Tracks

- Remote control: controlled tower desktop/VM access from the T480, tunnel-first; details in `docs/REMOTE_CONTROL.md`.
- Fleet telemetry: later node heartbeats/constants so `ctos-core` has a global view.
- Storage expansion: future multi-SSD strategy for packages, models, workers, snapshots, and backups.

## Historical Windows Bridge

Before the tower was wiped, `scripts/ctos-tower` provided a temporary SSH wrapper for Windows inventory and preparation. It assumed the foreground Windows `sshd.exe` bridge was already open on the tower.

Previously verified commands:

- `scripts/ctos-tower test`
- `scripts/ctos-tower inventory`
