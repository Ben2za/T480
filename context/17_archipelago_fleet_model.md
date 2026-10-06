# CTOS Archipelago Fleet Model

Date: 2026-06-09

Scope: secondary mission for turning the recovered desktop tower and future machines into an EndeavourOS-based CTOS fleet, while keeping the T480 usable as the mobile admin/work machine.

## Mission Summary

The T480 remains the portable control plane and personal work machine. It should keep prioritizing function, stability, and clear recovery over visual polish.

The recovered tower should become `ctos-core` after hardware inventory, backup, and an explicit install decision. It is the central heavy node for workers, local model/runtime capacity, caches, and richer desktop work.

Future machines become independent CTOS nodes with roles. They should be able to receive repo updates and re-apply their local role without depending on the T480 being online.

## Roles

### `ctos-t480` / Godfather

- Mobile admin and cockpit.
- Source-of-truth operator console for repo changes, SSH administration, VM visibility, and fleet status.
- Usable for normal work, coding, and Codex.
- Does not run heavy always-on services by default.
- Keeps the T480 mission: function first, design second.

### `ctos-core` / Tower

- Target OS: EndeavourOS, not Windows long term.
- Heavy compute and visual desktop.
- Candidate services after research and explicit decisions:
  - local Git mirror or deployment cache;
  - package/cache helper for Arch/EndeavourOS packages;
  - local AI model/runtime cache and worker host;
  - job queue / worker scheduler;
  - richer desktop and visual tooling.
- Should not be wiped until Windows data and hardware state are inventoried.

### `ctos-worker-*`

- EndeavourOS nodes that can run selected workers.
- Receive CTOS repo updates and apply a role manifest.
- Can be laptops, small PCs, or future desktop nodes.
- Should remain independently bootable and recoverable.

### `ctos-lab`

- VM/lab boundary for Kali and authorized security work.
- Offensive tooling stays in lab VMs, not on host desktops.

## Install And Bootstrap Strategy

Phase 1 target:

- Use the official EndeavourOS installer USB.
- Use a second CTOS bootstrap USB directory, or a second partition on the same USB when practical.
- The CTOS kit carries this repo subset, role metadata, bootstrap docs, and later package manifests.
- After EndeavourOS install, run a repo-owned bootstrap/apply script for the machine role.

Phase 2 target:

- Use EndeavourOS installer customization files to move toward one USB:
  - `/home/liveuser/user_pkglist.txt`
  - `~/user-commands-before.bash`
  - `~/user_commands.bash`
- Keep this deferred until package manifests and post-install scripts are proven on the T480 or a disposable test machine.

Do not build a custom ISO yet. The smallest reliable next step is a CTOS kit directory that can be copied to USB without modifying installer internals.

## Update Flow

Initial update model:

1. T480 edits and validates repo changes.
2. Changes are pushed to the canonical Git remote.
3. `ctos-core` pulls and can mirror/cache those changes locally.
4. Worker machines pull or receive a USB kit copy.
5. Each machine applies only its declared role.

Later update model:

- `ctos-core` may host a LAN Git mirror and package/model caches.
- T480 remains able to administer and recover the fleet without being a permanent server.
- No secrets, VM disks, reports, logs, model weights, package caches, or private browser state belong in Git.

## Feature Tracks

### Remote Control

Goal: control the tower from the T480, either through a remote desktop path or a controlled tower-side VM/session.

Status: V0 started with `scripts/ctos-remote`.

Constraints:

- must not expose unauthenticated desktop access on the LAN;
- should prefer an SSH/tunnel-first model;
- must remain recoverable if the graphical session breaks;
- should not replace normal SSH admin for system work.

Current shape:

- SSH remains the root control path.
- `scripts/ctos-remote status` inventories local viewer readiness, tower server readiness, sessions, unit files, and RDP/VNC listeners.
- `scripts/ctos-remote plan` documents the tunnel-first lane.
- No remote desktop package, service, firewall rule, or long-running tunnel is installed/enabled by this V0.

### Fleet Inventory

Goal: maintain a small inventory library for every machine in the archipelago, then aggregate live health/status.

Status: V1 started with `fleet/nodes.json` and `scripts/ctos-fleet`.

Current shape:

- static node metadata for `ctos-t480`, `ctos-core`, and planned workers;
- live local status for T480;
- live SSH status for `ctos-core`;
- planned feature registry for remote control, telemetry/constants, and storage expansion.

### Fleet Telemetry / Constants

Goal: later, nodes report periodic constants/heartbeats so `ctos-core` always has a global view of the archipelago.

Status: planned.

First rule: telemetry starts as explicit local/status pulls. No daemon, background sender, or persistent listener until the security model is documented.

### Storage Expansion

Goal: prepare `ctos-core` for future large SSD additions when budget allows.

Status: planned.

Current base:

- NVMe remains OS and active desktop disk;
- SATA SSD is `/srv/ctos`;
- future SSDs should extend capacity for packages, models, worker data, snapshots, and backups only after a storage topology decision.

Open storage choices:

- simple separate mounts by role;
- Btrfs multi-device layout;
- merger layer for capacity aggregation;
- dedicated backup disk versus mixed live data;
- snapshot and restore policy.

## Desktop Policy

The T480 desktop must stay clean enough to work like a normal daily Linux desktop: file manager, browser, app install/update flow, editor, terminal, screenshots, and cockpit.

Visual polish can evolve incrementally. Any visual component proven useful on the tower can be promoted back to the T480 only if it improves work without making the host fragile.

## Immediate Next Steps

1. Keep `ctos-core` visible from the T480 cockpit and fleet helper.
2. Decide the first network-exposed service, if any.
3. Install/test the first remote-control server and viewer after choosing between KDE RDP and KDE/VNC.
4. Design telemetry/constant reporting from nodes back to `ctos-core`.
5. Research and decide the future multi-SSD storage topology.
6. Only after that, consider EndeavourOS installer customization files for a one-USB flow.

## Open Decisions

- Exact remote-control protocol/tunnel model.
- Exact telemetry/heartbeat data model and retention rules.
- Exact storage expansion topology for future large SSDs.
- Exact desktop baseline for new EndeavourOS nodes.
- Exact package manifests and AUR policy.
- Secrets model before any fleet SSH or service token distribution.
- Whether to use Ansible immediately or keep plain repo scripts until the first two nodes are stable.
