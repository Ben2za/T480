# T480 CTOS Operator Environment

Personal Arch/EndeavourOS workstation rebuild repository.

The goal is a full-in, independent operator environment that can be recreated on each machine: desktop, dev tooling, red-team lab boundaries, AI/Codex workflow, and future personal-server sync.

Secondary mission: `docs/ARCHIPELAGO.md` describes the EndeavourOS fleet model with the T480 as mobile admin, a future tower `core`, and additional worker nodes.

## Fast Start On T480

```bash
cd ~/T480
git status --short --branch
git pull --ff-only origin main
codex login status
codex
```

Start here:

- `AGENTS.md`: persistent Codex operating rules for this repo.
- `context/README.md`: project memory index.
- `docs/CODEX_ONBOARDING.md`: practical Codex onboarding.

## Control Space

First local cockpit:

```bash
./scripts/ctos-control tui
./scripts/ctos-control serve
./scripts/ctos-session boot
./scripts/ctos-session status
```

- `SUPER+C` opens the terminal cockpit in Hyprland.
- The local web shell runs at `http://127.0.0.1:8765`.
- Hyprland startup calls `scripts/ctos-session boot`: CTRL gets the terminal cockpit, DESK attempts the tunnel-only `ctos-core` X11 VNC desktop, and VMS gets a Kali quick-control terminal.
- Current implementation is stdlib-only and reports blocked VM/AI access explicitly.

Read-only VM inventory:

```bash
./scripts/ctos-vm list
./scripts/ctos-vm status
./scripts/ctos-vm inspect <domain>
```

Current libvirt reality is recorded in `context/10_libvirt_inventory.md`.

## CTOS AI

Install user command shims once:

```bash
cd ~/T480
./scripts/ctos-install-user-bin
source ~/.bashrc
```

Then the first Jarvis-like brief works from any terminal:

```bash
ctos-ai
ctos-ai brief
ctos-agenda add "example task" --priority 3 --estimate 30
ctos-ai plan-day
```

Operator-facing Jarvis bridge:

```bash
ctos-jarvis brief
ctos-jarvis smoke
ctos-jarvis text "agenda"
ctos-jarvis voice --seconds 4
ctos-jarvis voice --seconds 4 --save-agenda
ctos-jarvis review
ctos-jarvis confirm latest --yes
ctos-jarvis doctor
ctos-jarvis unlock-voice
ctos-jarvis unlock-voice --interactive
ctos-jarvis unlock-voice --start
ctos-jarvis unlock-voice --test
ctos-jarvis setup-voice --plan
```

`ctos-jarvis` is a facade over the safer CTOS tools. It does not give the model shell authority:
safe CTOS actions are routed first, agenda writes stay behind the proposal/confirmation loop, and
the mature Home Assistant/Wyoming backend remains gated until onboarding/token readiness is complete.
`ctos-jarvis smoke` is the quick non-destructive readiness check; use `--full` to include
`ctos-core` backend checks and `--with-model` to test the local model fallback.
`ctos-jarvis unlock-voice` is the mature voice-stack gate: it checks/starts the local
Home Assistant tunnel, summarizes the blocker, and points to the interactive hidden-prompt setup
when the Home Assistant token is still missing. After the token gate is ready, `--start` starts the
Speech-to-Phrase container and `--test` records one routed recognition sample.

Mutable CTOS actions go through the local approval queue:

```bash
ctos-ai actions
ctos-ai propose core-sync-repo
ctos-ai approvals
ctos-ai show 1
ctos-ai approve 1 --dry-run
ctos-ai approve 1
```

The queue is allowlist-only and stores state outside Git under `~/.local/share/ctos-ai/`.

## Fleet / USB Kit

Archipelago model:

```bash
less docs/ARCHIPELAGO.md
less context/17_archipelago_fleet_model.md
```

Stage a non-destructive CTOS bootstrap kit into a new or empty directory:

```bash
./scripts/ctos-build-usb-kit /path/to/empty/ctos-kit
```

First tower install/runbook:

```bash
less docs/TOWER_CTOS_CORE_INSTALL.md
bootstrap/ctos-apply-role ctos-core plan
```

VM lifecycle model:

- CTOS-managed VMs target `qemu:///system`.
- Planned repo definitions live under `libvirt/`.
- Current model is recorded in `context/11_vm_lifecycle_model.md`.
- Live CTOS network/pool state is recorded in `context/12_libvirt_infra_state.md`.

CTOS libvirt infra:

```bash
./scripts/ctos-libvirt-infra status
./scripts/ctos-libvirt-infra plan
./scripts/ctos-libvirt-infra apply
```

Kali install-phase domain:

```bash
./scripts/ctos-kali status
./scripts/ctos-kali plan
./scripts/ctos-kali prepare-media
./scripts/ctos-kali define
./scripts/ctos-kali start-install
```

Live Kali domain state is recorded in `context/13_kali_domain_state.md`.
First installer start state is recorded in `context/14_kali_install_start.md`.

Windows Apple recovery scaffold:

```bash
./scripts/ctos-apple-host status
./scripts/ctos-apple-recovery status
./scripts/ctos-apple-recovery plan
```

The current scaffold is deliberately blocked before Windows installation: no
eligible VM entitlement is recorded, and the locked iPhone must be physically
unplugged before IOMMU/reboot preparation. See `docs/APPLE_RECOVERY_VM.md` and
`context/24_windows_apple_recovery_vm_state.md`; do not attach the phone to a
VM or bypass a refused lifecycle command.

## Desktop Config

The current host cockpit desktop is tracked in:

- `hyprland/hyprland.conf`
- `waybar/config`
- `waybar/style.css`
- `scripts/ctos-install-desktop`
- `scripts/ctos-wallpaper`
- `scripts/ctos-session`
- `scripts/ctos-desk-remote`
- `scripts/ctos-vms-panel`

Install/update local config:

```bash
./scripts/ctos-install-desktop
hyprctl reload
pkill -x waybar && setsid -f waybar
```

## Current T480 State

- Repo path: `/home/operator/T480`
- Git remote: `git@github.com:Ben2za/T480.git`
- Codex CLI: installed and logged in with ChatGPT device auth.
- VS Code: official Microsoft binary installed.
- VS Code OpenAI extension: installed.
- GitHub SSH: T480 key validated for independent fetch/pull/push.

## Security Notes

- No secrets, tokens, private keys, logs, VM disks, loot, or private reports in Git.
- Temporary passwordless sudo used during bootstrap has been removed.
- Offensive tooling belongs in authorized lab/bug-bounty scope only.
