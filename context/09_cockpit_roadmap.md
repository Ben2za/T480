# Cockpit Roadmap

Date: 2026-05-27

## Direction

The host T480 is the control plane. It should stay clean, boring, and auditable.

Heavy or risky work belongs in isolated environments:

- Kali VM for authorized cyber/security workflows.
- Dev VM for isolated coding and workstation-portability work.
- AI workers activated by mode and resource budget.
- Game mode on the host unless a later hardware/VM decision justifies gaming in a VM.

## Host Workspaces

Waybar labels:

- `CTRL`: cockpit, host status, VM/mode controls.
- `DESK`: general personal desktop.
- `STATION`: general non-cyber work and repo/config/code work on the host.
- `VMS`: libvirt, snapshots, VM lifecycle.
- `AI`: local AI status and worker controls.
- `VAULT`: secrets tooling after a secrets decision.
- `COMMS`: browser/chat/mail once policy exists.
- `GAME`: host performance/game mode.

Cyber workspaces such as `RECON`, `EXPLOIT`, and `REVERSE` belong inside the Kali guest, not on the host.

## Control Surface Target

The `CTRL` workspace should become a real cockpit:

- System panels: CPU, RAM, disk, battery, thermal, uptime.
- Network panels: Wi-Fi, DNS, VPN/killswitch, firewall state.
- VM panels: Kali, Dev, Game/mode state, snapshots, storage, dirty/running/stopped state.
- AI panels: installed runtime, loaded model, workers, memory budget.
- Mode controls: `ctos-mode normal`, `ctos-mode kali`, `ctos-mode dev`, `ctos-mode ai`, `ctos-mode game`.
- Event console: VM start/stop, VPN off, low battery, AI worker loaded, snapshot actions.
- Globe/feeds: local telemetry first; external feeds require a source and privacy decision.

## Implementation Phases

1. Track live desktop config in Git.
2. Build a local control dashboard that is useful before any VM automation.
3. Inventory libvirt reality and define VM lifecycle model.
4. Create `ctos-vm` commands for list/status/start/stop/snapshot.
5. Create `ctos-mode` commands for host resource profiles.
6. Build Kali VM config and put cyber workspace labels inside the guest.
7. Build Dev VM config as an isolated CTOS-portable environment.
8. Research AI stack for T480 constraints and define worker memory budgets.
9. Decide game mode: host performance mode first; VM gaming only if justified.

## Current State

Done:

- Host labels moved away from cyber vocabulary.
- Screenshot workflow is silent and clipboard-capable.
- Live Hyprland/Waybar config is tracked in the repo.
- `scripts/ctos-install-desktop` can reinstall desktop config.
- `control/` contains a first Python stdlib TUI and local web dashboard.
- 2026-05-27: local web dashboard was expanded into a first cockpit view with system meters, modes, VMs, network, services, AI workers, events, and local telemetry globe.
- 2026-06-02: libvirt reality was inventoried in `context/10_libvirt_inventory.md`.
- 2026-06-02: `scripts/ctos-vm` provides read-only `list`, `status`, and `inspect` commands for `qemu:///system` and `qemu:///session`.
- 2026-06-02: VM lifecycle model was accepted in `context/11_vm_lifecycle_model.md`; CTOS-managed domains target `qemu:///system` with dedicated CTOS pools and NAT network definitions.
- 2026-06-03: CTOS live libvirt infrastructure was applied: `ctos-nat`, `ctos-images`, and `ctos-snapshots`.
- 2026-06-03: `ctos-kali` was defined as a shutoff install-phase domain with a 40 GiB qcow2 volume and Kali installer ISO attached.

Next:

- Add an explicit Kali install-start path, then install Kali manually/visibly.
- Add guarded `ctos-vm define/start/shutdown/snapshot` commands only after the mutating-command ADR.
- Keep it localhost-only until an explicit service/security decision exists.
- Do not install frontend/browser/runtime dependencies without a researched ADR.

## Constraints

- T480 has about 16 GiB RAM.
- Kali and Dev VMs cannot both receive large fixed allocations while AI workers are loaded.
- Minecraft/full performance should probably be a host game mode that stops VMs/AI first.
- Host must not become the offensive workstation; it orchestrates isolated guests.
- No silent fallback: unavailable libvirt/AI/firewall state must be displayed as blocked or unavailable.
