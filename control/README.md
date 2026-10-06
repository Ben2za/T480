# CTOS Control

First local control-space implementation for the host cockpit.

## Current Scope

- `tui.py`: terminal cockpit for immediate use in `kitty`, including fleet inventory, `ctos-core` state, and `ctos-kali` state, snapshot, disk, and health summary.
- `server.py`: local HTTP dashboard on `127.0.0.1:8765`.
- `static/`: browser-ready dashboard shell for the future visual cockpit.

The first iteration is intentionally stdlib-only. It does not install a browser, VM manager, frontend framework, or AI service.

## Commands

```bash
./scripts/ctos-control tui
./scripts/ctos-control serve
./scripts/ctos-control status
./scripts/ctos-control stop
./scripts/ctos-control url
```

Direct tower status helper:

```bash
./scripts/ctos-core status
./scripts/ctos-core status --json
./scripts/ctos-core ssh
./scripts/ctos-core plan-services
./scripts/ctos-core apply-layout
./scripts/ctos-core sync-repo --dry-run
./scripts/ctos-core sync-repo
./scripts/ctos-fleet status
./scripts/ctos-fleet status --json
```

## Boundaries

- VM information is read through `virsh --readonly` against `qemu:///system` and `qemu:///session`.
- `ctos-core` information is read through key-based SSH to `ctos@10.42.0.2`.
- `ctos-core` cockpit integration is status-only: it does not run sudo, mutate system services, or format/mount disks.
- `scripts/ctos-core apply-layout` and `sync-repo` mutate only user-writable paths under `/srv/ctos`.
- Fleet information is read from `fleet/nodes.json`; live checks are explicit pulls, not background telemetry.
- If libvirt access is denied, the dashboard reports that instead of hiding it.
- Mutating VM actions are limited to the localhost-only `/api/vm/action` endpoint.
- The only exposed domain is `ctos-kali`.
- Exposed actions are `start`, `shutdown`, `console`, and offline `checkpoint`.
- The terminal TUI is status-only and points VM actions back to the web dashboard.
- `shutdown` uses qemu-guest-agent mode and does not hard-stop as a fallback.
- `checkpoint` refuses to run unless `ctos-kali` is already shut off.
- Global feeds are placeholder/local telemetry only until a data-source and privacy policy are decided.

For a fuller read-only VM inventory, use:

```bash
../scripts/ctos-vm list
../scripts/ctos-vm status
```
