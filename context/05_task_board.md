# Task Board

Date: 2026-10-06

## Completed Repository Preservation Before T480 Repurposing

Scope 2026-10-06: the operator requested committing and pushing all outstanding
project work to the existing GitHub repository before discussing a new role for
the T480. Preserve the current implementation and historical notes as a
checkpoint; runtime secrets, caches, logs, recordings, and VM/media images stay
outside Git. This is repository preservation, not a full-machine backup.

- [x] Inspect repository instructions, local changes, ignored files, and origin.
- [x] Check candidate files for credentials and private/generated artifacts.
- [x] Run the existing tests and relevant static validation.
- [x] Fetch origin and reconcile any remote divergence without losing work.
- [x] Commit the reviewed project checkpoint and push to origin/main.
- [x] Verify the remote commit and the local worktree state after publication.

The T480's future role remains open; no reinstall or host conversion is part
of this checkpoint.

Verification 2026-10-06: origin/main and HEAD both resolve to `4bacad9` after
fetch, with no divergence. The reviewed candidate set contains 156 files
(141 previously untracked); only Python bytecode caches are ignored in the
working tree. Credential-pattern hits are synthetic negative-test fixtures;
no real credential or unexpected binary/runtime artifact was found by these
checks. The existing 126 unittest cases pass. Static validation passes for
37 Python files, 31 shell scripts, 10 JSON files, 2 JavaScript files, and 8 XML
files. PowerShell execution and live host/fleet behavior were not retested.
The full staged diff exposed one trailing-whitespace-only blank line in
`waybar/config`; it was removed without changing the configuration values.

Publication verified 2026-10-06: checkpoint
`65c2d1b59ebdd00d8e4fee8519fccc6100150916` was pushed to
`git@github.com:Ben2za/T480.git`, branch `main`. A subsequent `git ls-remote`
returned that exact commit. The checkpoint contains 148 added/modified files
and the local worktree was clean after publication. This completion note is
recorded in a separate documentation commit. Repurposing remains a discussion
to start with the operator; no new OS or machine role has been selected.

## Active Voice Console Missing-Response Incident

- [x] Correlate the operator report with the live loopback server log without
  exposing request text or transcripts.
- [x] Identify whether the EliteBook is running the current browser client.
- [x] Fix the static-cache and request-mode response defects.
- [x] Add narrow regression tests and rerun the focused suite.
- [x] Restart the loopback service, force a fresh EliteBook page, and verify the
  request path through the existing SSH tunnel.

Scope 2026-07-19: diagnose and repair missing visible Chat/Codex responses on
the already-authorized owned EliteBook/T480 LAN path. Do not enable the live
Codex cloud gate, retain raw audio/transcripts, expose a listener, or alter the
outside-home network boundary.

Evidence 2026-07-19: the restarted console log contains successful Chat and
Codex audio POSTs, but subsequent speech requests still target legacy
`/api/voice/say` instead of current `/api/voice/synthesize`. Static HTML/JS
responses have no explicit no-store policy, confirming that the EliteBook can
reuse an obsolete client. An apparent duplicate Codex response was ruled out:
it was the same source line printed twice by overlapping inspection ranges.

Result 2026-07-19: build `2026-07-19.3` sends `Cache-Control: no-store`,
`Pragma: no-cache`, and `Expires: 0` for static/API responses; HTML references
versioned assets and the client refuses a build mismatch. Every request now
captures its submission mode and disables mode changes while busy, preventing
a delayed Chat response from being parsed as a Codex preview or vice versa.
Codex previews scroll into view, request failures appear in the Answer panel,
and a successful-but-empty local Chat result becomes a visible server failure.
Legacy `/api/voice/say` now fails with HTTP 410 and cannot play Piper on the
T480 even from an already-open obsolete page.

The service restarted cleanly with the cloud run gate still false. Firefox on
`BXEB` fetched the versioned HTML/CSS/JS and then the matching status API. A
synthetic Chat through the EliteBook tunnel returned `OK` in about 11 seconds;
a local-only Codex preview returned in about 53 seconds with
`allowed_scope=["ai/voice_task_spec.py"]` and `runnable=false`; browser Piper
transport returned HTTP 200 `audio/wav` with 73260 bytes. Human confirmation
that the WAV is audible on the EliteBook remains pending. The expanded focused
suite passes 52 tests, plus Python/Bash/JavaScript syntax and diff checks. No
Codex cloud task, public listener, raw transcript retention, or outside-home
change occurred.

## Active EliteBook Voice-to-Codex Implementation

- [x] Re-verify T480 restart state and bidirectional key-only SSH with `BXEB`.
- [x] Start the loopback Voice Console on the T480 and create the `BXEB` local
  forward without widening either listener.
- [x] Open the forwarded Voice Console in the active EliteBook Firefox session
  for the operator's manual microphone smoke.
- [x] Record the Level A result and stop on any failed stage instead of masking
  it.
- [x] Implement and test the synthetic spec-only read-only Codex boundary.
- [x] Add the local transcript-to-spec preview without allowing implicit Codex
  execution or raw-transcript forwarding.
- [x] Add browser-delivered Piper audio only after the text result path passes.
- [x] Run narrow tests, record verification, and leave outside-home transport as
  its separate approval-gated slice.

Scope 2026-07-18: the operator explicitly authorized proceeding with the
staged implementation and then requested recovery after the T480 powered off.
Remote commands on the owned `BXEB` may re-establish the existing SSH tunnel
and open Firefox as in the earlier intake. Do not install Tailscale, change
router/firewall or power policy, expose public listeners, retain raw audio or
transcripts, enable workspace-write Codex, or add a silent local fallback.

Level A result 2026-07-18 after reboot: nested key-only SSH succeeded in both
directions (`ctos-node/operator` <-> `BXEB/ben`). The T480 console is healthy
on `127.0.0.1:8770` with audio retention disabled. A new `BXEB` SSH process
owns only its local `127.0.0.1:8770` forward, the status API passed through the
tunnel, Firefox opened the forwarded page, and the console logged a successful
HTTP 200 browser audio request in Chat mode. This proves the post-reboot
browser/microphone, SSH, ffmpeg, Vosk, and response path. It does not prove the
quality of five human Codex-mode samples or perceived Piper audio quality.

Implementation result 2026-07-18: the closed task/result schemas,
deterministic validator, spec-only `codex exec` runner, local Ollama structured
compiler, editable canonical preview, revalidation, digest-bound one-use token,
and browser-delivered Piper WAV path are implemented. The compiler now applies
a deterministic ceiling when the operator explicitly names a file, after a
live first pass showed that the small model could broaden scope. A live preview
and a valid no-store Piper WAV both passed through the `BXEB` tunnel. The
console manager also recovers from a stale PID file after interruption. Its
final restart and tunnel status passed. The focused suite passes 48 tests.

Live acceptance boundary 2026-07-18: the first actual Codex smoke was stopped
before execution because a read-only run can still disclose the reviewed spec
and permitted repository content to OpenAI. The Voice Console run gate is now
disabled by default and cannot be opened by its browser button alone. One
synthetic cloud invocation remains pending informed operator approval; this is
not a Codex failure because no task or network submission started. Human
EliteBook audibility and five French STT/spec samples also remain manual
acceptance checks. Tailscale/public access and T480 availability policy remain
separate and unchanged.

## Active EliteBook-to-T480 Voice-to-Codex Test Plan

- [x] Confirm current LAN identity and key-only SSH from `BXEB` back to the T480.
- [x] Inspect where browser capture, STT, Codex handoff, and Piper output run today.
- [x] Define the smallest existing-stack smoke test from the EliteBook.
- [x] Define the compliant spec-only `codex exec` POC and its verification gates.
- [x] Separate future outside-home access from the LAN voice POC and research its safe boundary.
- [x] Record concrete operator steps, blockers, and realistic elapsed-time ranges.

Scope 2026-07-18: planning and read-only verification only. Do not start the
Voice Console, retain audio, invoke a nested Codex task, install a VPN, expose
SSH/HTTP publicly, change firewall/router state, or alter T480 sleep/power
policy in this pass.

Result 2026-07-18: the existing LAN transport can be proved in 10-20 minutes
(30-45 minutes with diagnosis) through a `BXEB` loopback SSH forward. This
proves microphone, browser, ffmpeg, Vosk, and CTOS Brief only: current Codex
mode prints a prohibited raw handoff, and current Piper playback occurs on the
T480. A synthetic validated read-only Codex slice is 4-8 focused hours; the
full voice -> local compiler -> reviewed spec -> Codex path is 8-16 hours, and
browser-delivered Piper adds 2-4 hours. Detailed gates and commands are in
`context/26_elitebook_voice_codex_test_plan.md`. Outside-home access is a
separate 1.5-3-hour private-overlay slice after approval; public router
forwards and Funnel are rejected. No live service, Codex task, package, VPN,
power setting, public listener, or retained audio was created in this pass.

## Active ZLiteBook Voice/Phone Requirements Intake

- [x] Re-read the repository method, current voice/Jarvis state, and ZLiteBook reconnect context.
- [x] Verify the active Ubuntu graphical session and choose the smallest auditable text-entry bridge.
- [x] Open the text-entry window on the Ubuntu desktop and retrieve the operator-provided list.
- [x] Compare the list with the deployed CTOS/Jarvis components and identify only the necessary changes.
- [x] Record the intake result, remaining questions, and any researched technical decisions.

Scope 2026-07-18: use the newly re-established key-only SSH link to
`BXEB`/`ctos-zlitebook` only as a temporary operator-to-Codex text bridge.
Do not install packages, enable services, deploy phone software, or retain
secrets/sensitive phone data during intake.

Result 2026-07-18: an existing Zenity dialog in the active `BXEB`
GNOME/Wayland session returned the list directly over SSH stdout; no payload
file was created and the raw entry was not copied into the repo. The complete
sanitized comparison is in `context/25_voice_codex_orchestrator_intake.md`.
Most of the voice stack already exists. The critical missing component is a
validated, transcript-free task-spec boundary plus a direct supported
`codex exec` adapter. The operator confirmed that authenticated paid Codex may
be the primary work engine. ADR-0069 records Codex-first/no-silent-fallback
handling. No package, model, service, or Codex task was started.

## Active EliteBook/ZLiteBook Reconnect

- [x] Re-read repo context for the old EliteBook bootstrap trail.
- [x] Discover current reachable address/hostname without reading private keys.
- [x] Test SSH reachability and authentication from the T480.
- [x] Add the node to fleet metadata only after a stable identity is confirmed.
- [x] Record result, limitations, and next bootstrap command.

Context 2026-07-18: old notes only confirm that the T480 was reachable from
the EliteBook at `ssh operator@192.168.1.21` on 2026-05-24. They do not record
the EliteBook's own current IP or SSH username.

Discovery 2026-07-18: candidate is `bxeb.home` at `192.168.1.24`, MAC vendor
Intel, running Ubuntu OpenSSH `9.6p1` on TCP `22` and nginx `1.27.5` on TCP
`8080` serving `Snake Surge`. Initial SSH attempts with `operator`, `ben`, and
`ctos` failed before the correct user and authorized key state were confirmed.

Result 2026-07-18: the correct Ubuntu username is `ben`. The operator installed
the T480 public key with `ssh-copy-id -F /dev/null ben@192.168.1.24`; key-only
SSH then verified hostname `BXEB`, user `ben`, Ubuntu `24.04`, and kernel
`6.17.0-40-generic`. Added `ctos-zlitebook` as an active `worker-candidate` in
`fleet/nodes.json`, extended `scripts/ctos-fleet` with generic read-only SSH
status for non-core Linux nodes, and documented the link in
`docs/ARCHIPELAGO.md`. Live `scripts/ctos-fleet status --json` reports the node
online, with about 7.6 GiB RAM and root storage already 89% used.

## Active Windows Apple Recovery VM Implementation

- [x] Re-audit host, repository, libvirt, storage, boot, and package state immediately before mutation.
- [x] Bring the Arch host to one coherent package state and install the verified VM firmware/TPM prerequisites.
- [ ] Enable and verify Intel IOMMU, then qualify the USB-C xHCI controller without ACS override.
- [ ] Resolve the Windows VM entitlement, then download, checksum, and register only the matching official Microsoft media; do not use community VirtIO media.
- [x] Add fail-closed pre-install VM definitions, host/lifecycle helpers, tests, and an operator runbook to the repository.
- [x] Implement the authenticated ISO pool import, post-install evidence/re-attestation transition, atomic baseline, and disposable session lifecycle; keep every live path blocked until entitlement resolution.
- [ ] Install and update an eligible Windows edition with inbox drivers and the official Apple Devices application.
- [ ] Seal a clean `apple-ready` baseline and validate USB-C handoff with a non-sensitive test device.
- [ ] Record final verification, remaining limitations, and recovery instructions.

Scope 2026-07-17: implement the first goal from
`context/23_windows_apple_recovery_vm_plan.md`. This iteration ends at a clean,
reusable Apple-ready Windows VM and a non-sensitive USB validation. Do not
attach the iPhone to the VM, enter recovery/DFU, erase it, restore it, attempt
passcodes, or access its data. Any later phone restore remains a distinct,
explicit destructive-action approval window.

Licensing gate 2026-07-17: the operator confirmed that no Windows licence is
available. Host/repository work may continue, but consumer Windows media must
not be installed or sealed as a durable baseline. Microsoft's official
Windows 11 Enterprise Evaluation is a separate 90-day disposable option that
requires explicit approval because it requires a Microsoft account and shuts
down hourly after expiry.

Scaffold update 2026-07-17: install/maintenance XML now validates against
libvirt; the helper enforces the recorded entitlement state, Type-C partner
gate, exact device allowlist, active/inactive XML comparison, real
`virt-fw-vars` inspection, and atomic pre-install NVRAM/TPM preparation. It
deliberately refuses maintenance transition, baseline sealing, disposable
sessions, USB qualification success, and cleanup until those workflows have
real evidence. The final scaffold audit also closed unsafe secure-state
ownership/symlink handling, non-empty pre-install TPM acceptance, maintenance
profile start, recursive device-child drift including host logs/rendernodes/ROMs,
exact emulator/serial/console/video/PCR drift, and unreadable USB vendor
inventory. Combined Apple host/VM tests: 46 passed. No domain, VM disk,
managed secure state, media, PCI detach, or phone action was created.

Lifecycle completion slice 2026-07-18 (static implementation complete; live execution blocked): audit and implement the
previously hard-refused authenticated media import, post-install evidence and
maintenance transition, atomic baseline consistency set, disposable sessions,
recoverable cleanup, and non-sensitive USB qualification evidence. All new
mutation paths must remain unreachable while the entitlement is blocked or the
phone is a Type-C source/host partner; this slice must not create live state.

Lifecycle progress 2026-07-17: authenticated media import is now implemented
without authorizing its use. It checks visible root and the durable entitlement
before source access, accepts only the fixed canonical Microsoft filename/hash,
detects source mutation, publishes without replacement, writes a strict managed
attestation, refreshes the libvirt pool, and converges idempotently. Existing
incompatible targets are preserved. Recovery-helper tests now total 55 and
pass; combined host/VM tests total 74. The live entitlement remains
`blocked-no-eligible-vm-entitlement`, so no media was read or imported.

## Active Windows Apple Recovery VM Architecture Plan

- [x] Record the operator-confirmed iPhone XS model without device identifiers.
- [x] Re-inventory host/libvirt/storage/IOMMU constraints relevant to a reusable Windows VM.
- [x] Research current Windows media, VM hardware, VirtIO, libvirt USB, and Apple restore requirements from primary sources.
- [x] Select a reproducible VM lifecycle, driver, update, snapshot, networking, and USB handoff model.
- [x] Write a phase-by-phase implementation and validation runbook with explicit destructive-action gates.
- [x] Record decisions, sources, blockers, and the exact next goal scope.
- [x] Do not create/start a VM, download media, attach the phone, or enter recovery/DFU in this planning iteration.

Scope 2026-07-17: research and architecture only for a reusable official-Apple
Windows recovery workstation VM. Implementation is deferred until the user
starts the next iteration in goal mode.

Result 2026-07-17: complete implementation plan recorded in
`context/23_windows_apple_recovery_vm_plan.md`. Selected supported Windows 11
25H2 x64 on Q35/UEFI Secure Boot with Microsoft 2011+2023 transition keys,
private TPM 2.0, Windows inbox AHCI/e1000e drivers, official Apple Devices Store
product `9NP83LWLPZ9K`, CTOS NAT, 8 GiB RAM, 4 vCPU, and a 96 GiB sparse disk.
Preferred phone path is managed passthrough of JHL6240 xHCI `0000:3c:00.0`,
strictly conditional on a rebooted `intel_iommu=on` preflight proving isolation,
port mapping, host charging, detach, and reattach. ACS override is rejected.
The first future goal ends at a clean `apple-ready` baseline plus non-sensitive
USB validation; iPhone recovery/Restore is a separate destructive approval
window. No package, ISO, VM, boot configuration, or phone state was changed.

## Active Read-Only iPhone USB-C Identification

- [x] Preserve the no-pairing, no-write, no-passcode-attempt boundary.
- [x] Inventory the T480 USB-C controller, current topology, and host USB policy.
- [x] Inspect current/recent kernel USB events for Apple enumeration or cable faults.
- [x] Query only public pre-pairing device metadata if the iPhone enumerates.
- [x] Record verified model clues, blockers, and the smallest physical retest.

Scope 2026-07-17: identify the connected phone and USB path only. Do not pair,
trust, back up, restore, enter recovery/DFU, or change device/host USB policy.

Result 2026-07-17: both T480 xHCI controllers and the Thunderbolt/USB-C root
hubs are present and active, with the USB-C buses exposed as empty root hubs.
No Apple vendor ID `05ac`, connect/disconnect event, or USB child device was
observed. USBGuard is absent and `usbmuxd` is not installed as a service, but
neither can hide a device that never enumerated. Current Apple policy explains
that a locked iPhone does not communicate with a new wired accessory by
default. Exact model therefore cannot be read over this locked USB session.
Smallest non-mutating identification path: read only the `Axxxx` model number
inside the SIM-tray slot; iPhone X values are `A1865`, `A1901`, or `A1902`.
Do not expose or record the IMEI etched on the tray.

## Active Personal iPhone Passcode Recovery Assessment

- [x] Re-read repo context, security boundary, Kali state, and research rules.
- [x] Verify current Apple-supported passcode recovery, erase, backup, and Activation Lock behavior.
- [x] Assess the safest sequence that maximizes the chance of preserving family photos.
- [x] Record sources, constraints, unresolved facts, and final recommendation.
- [x] Do not install or run passcode-bypass, brute-force, or forensic tooling.

Scope 2026-07-17: advice and read-only assessment for an owner-authorized family
iPhone currently in a 15-minute Security Lockout delay. No data extraction,
device mutation, erase, or software installation is authorized in this step.

Result 2026-07-17: stop passcode attempts. The only supported non-erasing
recovery identified is iOS 17+ Passcode Reset with the previous passcode within
72 hours of a passcode change. Otherwise Apple requires erasing the device and
restoring from iCloud Photos, iCloud Backup, or an existing computer backup.
Before erasing, verify the linked Apple Account/Activation Lock credentials and
archive visible iCloud photos. A new computer cannot be trusted while the phone
is locked because trust requires the device passcode. Read-only USB inventory
found no Apple USB device, so model/iOS could not be verified. No bypass,
forensic, or brute-force tool was installed or run.

## Active Tower Internet Throughput Diagnosis

- [x] Re-read repo context and existing tower egress helper.
- [x] Compare T480 WAN health with `ctos-core` egress health.
- [x] Check T480-to-tower Ethernet link speed and route/NAT state.
- [x] Identify whether the slow path is LAN, NAT/firewall, DNS, Wi-Fi WAN, or remote desktop traffic.
- [x] Apply the smallest durable fix if the fault is confirmed.
- [x] Record result and verification.

Result 2026-07-13: T480 WAN is healthy, T480-to-tower Ethernet is
`1000/full`, and tower-to-T480 ping is healthy. The tower cannot ping `1.1.1.1`
or resolve DNS, so the fault is T480 tower egress/NAT after reboot. Permanent
fix applied with `scripts/ctos-install-tower-egress`: `/etc/nftables.conf`
contains CTOS tower forward/NAT rules and
`/etc/sysctl.d/90-ctos-ip-forward.conf` keeps IPv4 forwarding enabled.
Post-fix tower checks passed: gateway ping 0% loss, `1.1.1.1` ping 0% loss
at about 13 ms, DNS resolved `endeavouros.com`, and a 10 MB HTTP download from
Cloudflare reached about 24 MB/s.

## Active DESK Remote Boot Healing

- [x] Re-read repo context and current DESK remote scripts.
- [x] Stop treating a stale local SSH listener as a healthy DESK tunnel.
- [x] Make the DESK guard heal faster after T480/tower boot or resume.
- [x] Verify syntax and live guard status.
- [x] Record the remote-access reliability decision.

Result 2026-07-12: `scripts/ctos-desk-remote` and `scripts/ctos-desk-guard`
now require a real VNC `RFB` handshake on `127.0.0.1:5902`; stale local SSH
listeners are killed and rebuilt. The guard default interval is now 5 seconds.
Live status after relaunch reported `local_tunnel: listening 127.0.0.1:5902
handshake=ok`.

## Active Audit: Repository and Host Orientation

- [x] Re-read repo context and local working agreements.
- [x] Inventory repository structure and existing planning documents.
- [x] Inventory host filesystem layout without reading secrets, browser state, VM disks, logs, or generated sensitive artifacts.
- [x] Identify likely intervention points for future bootstrap, security, VM, AI, and dotfile tasks.
- [x] Record verification commands and unresolved assumptions.

Audit summary recorded in `context/08_host_audit.md`.

## Active Desktop Fix: Screenshot And Background

- [x] Verify existing screenshot tools and Hyprland wallpaper config.
- [x] Research/document screenshot workflow choice.
- [x] Add screenshot keybinds.
- [x] Apply repo background image through Hyprland startup.
- [x] Reload or provide exact manual reload command if sandbox blocks it.

Live config updated at `~/.config/hypr/hyprland.conf`; Hyprland reload and `swaybg` process verified on 2026-05-26.

## Desktop Fix: Hyprland Config Error

- [x] Confirm `dwindle:pseudotile` is rejected by current Hyprland.
- [x] Remove obsolete `pseudotile = yes` from `~/.config/hypr/hyprland.conf`.
- [x] Reload Hyprland and verify `hyprctl configerrors` returns no errors.

## Active Desktop Refactor: Host Workspace Model

- [x] Move cyber-specific workspace names out of the host.
- [x] Rename host workspace labels around cockpit/control, normal work, VM control, AI, comms, and game mode.
- [x] Align Waybar labels and styling with the new host workspace model.
- [x] Reload Hyprland/Waybar and verify no config errors.
- [x] Record rationale in the decision log.

Implementation note: Hyprland keeps numeric workspace IDs for stable native switching; Waybar carries the semantic labels `CTRL`, `DESK`, `STATION`, `VMS`, `AI`, `VAULT`, `COMMS`, `GAME`.

## Active Control Space: First Dashboard

- [x] Move current VS Code window to `DESK`.
- [x] Create a repo-owned local control dashboard.
- [x] Surface first-pass host, VM, AI, and network status without privileged changes.
- [x] Add a launcher script and Hyprland keybind for the control dashboard.
- [x] Launch it into `CTRL` and verify the service responds locally.

Implementation note: first pass lives in `control/` with launcher `scripts/ctos-control`; `SUPER+C` opens the terminal cockpit. Web shell is available on `127.0.0.1:8765` when started.

## Active Desktop Fix: AZERTY Workspaces And Screenshot Clipboard

- [x] Add French AZERTY top-row workspace binds for `SUPER+&/é/"'/(-è_ç`.
- [x] Install/verify `wl-clipboard`.
- [x] Add repo-owned screenshot wrapper for file + clipboard capture.
- [x] Repoint Hyprland screenshot binds to the wrapper.
- [x] Reload Hyprland and verify config errors are clear.

Screenshot workflow is now silent: files are saved under `~/Pictures/Screenshots` and PNG content is copied with `wl-copy` without a desktop notification.

## Active Desktop Reproducibility: Track Cockpit Config

- [x] Import current Hyprland config into `hyprland/hyprland.conf`.
- [x] Import current Waybar config into `waybar/config`.
- [x] Import current Waybar style into `waybar/style.css`.
- [x] Add `scripts/ctos-install-desktop` with backup-on-change behavior.
- [x] Document the repo-owned desktop config path and verification.

## Active Cockpit Roadmap And Dashboard

- [x] Save cockpit/VM/AI/game-mode roadmap in `context/09_cockpit_roadmap.md`.
- [x] Improve the local web dashboard into the first real `CTRL` cockpit.
- [x] Keep dashboard localhost-only and dependency-light.
- [x] Verify dashboard backend and static assets.

Dashboard now exposes host, system meters, modes, VMs, network, services, AI workers, events, and local telemetry globe through `control/static/` and `/api/status`.

## Active Libvirt Inventory And Read-Only VM CLI

- [x] Inventory libvirt system and session connections without reading VM disk contents.
- [x] Record VM/network/storage reality in context.
- [x] Add read-only `scripts/ctos-vm` commands: `list`, `status`, `inspect`.
- [x] Keep start/stop/snapshot actions out of scope for this first CLI.
- [x] Verify script output and dashboard compatibility.

Implementation note: `scripts/ctos-vm` now checks `qemu:///system` and `qemu:///session` with `virsh --readonly`. Inventory is recorded in `context/10_libvirt_inventory.md`; the current state is no defined domains, active pools, Kali ISO present, and `kali.qcow2` still only a qcow2 allocation stub.

## Active VM Lifecycle Model

- [x] Research current libvirt/Arch guidance for system/session, storage pools, networking, and snapshots.
- [x] Document CTOS VM lifecycle model and boundaries.
- [x] Add repo-owned `libvirt/` planning structure without VM disks or generated state.
- [x] Record the architecture decision and source registry entry.
- [x] Verify docs/scripts remain consistent.

Implementation note: CTOS-managed domains target `qemu:///system`; repo definitions now include `ctos-nat`, `ctos-images`, `ctos-snapshots`, and planned VM profile metadata. No live libvirt definitions were changed in this step.

## Active Libvirt Infra Apply Command

- [x] Add an idempotent repo command for CTOS libvirt network/pool infra.
- [x] Include `status`, `plan`, and `apply` modes.
- [x] Refuse to overwrite conflicting live libvirt resources.
- [x] Apply only `ctos-nat`, `ctos-images`, and `ctos-snapshots`; do not define domains.
- [x] Verify dry-run/status and live apply.
- [x] Record decision, sources, and verification.

Implementation note: `scripts/ctos-libvirt-infra apply` defined, started, and autostarted only CTOS infrastructure on 2026-06-03. Idempotence verified by a second apply returning no changes. The dashboard now exposes `vms.infra` so CTRL can show CTOS network/pool readiness.

## Active Kali Domain Definition

- [x] Research/verify current Kali/libvirt requirements and local virt-install capabilities.
- [x] Add repo-owned install-phase domain XML for `ctos-kali`.
- [x] Add idempotent `status`, `plan`, and `define` command for `ctos-kali`.
- [x] Create only the libvirt volume and shutoff domain; do not start/install Kali.
- [x] Verify domain XML, script behavior, live domain state, and cockpit status.
- [x] Record decision, sources, and live state.

Implementation note: `ctos-kali` now exists under `qemu:///system` as a shutoff install-phase domain. Volume `ctos-images/ctos-kali.qcow2` exists; Kali is not installed yet.

## Active Kali Install Start

- [x] Add explicit `scripts/ctos-kali start-install`.
- [x] Ensure it blocks unless the domain, volume, ISO, and CTOS infra are compatible.
- [x] Start the VM only if it is shut off; do not reinstall/redefine implicitly.
- [x] Open the graphical installer console through Hyprland/virt-manager.
- [x] Verify running state, viewer launch, and cockpit visibility.
- [x] Record decision, sources, and live state.

Implementation note: initial start failed because QEMU could not traverse `/home/operator` to read the ISO. Added `ctos-iso`, imported the Kali ISO with `scripts/ctos-kali prepare-media`, redefined `ctos-kali`, then started it. The VM is running and the console window is visible on workspace 2.

## Active Kali Installer DHCP Recovery

- [x] Inspect live `ctos-nat` network state after installer DHCP failure.
- [x] Identify whether the failure is libvirt network, guest NIC, or installer timing.
- [x] Apply the smallest safe recovery.
- [x] Verify installer can continue with networking or record an explicit no-network path.

Live check: `ctos-nat` is active/autostarted, `virbr-ctos` is up at `192.168.130.1/24`, `vnet2` is attached to the bridge, and libvirt `dnsmasq` for `ctos-nat` is running. DHCP retry still failed in the installer, so the guest was configured manually with `192.168.130.50/24`, gateway `192.168.130.1`, DNS `192.168.130.1`. Installation continued.

## Active Kali Post-Install Boot

- [x] Inspect current domain state after installer completion prompt.
- [x] Stop or wait for the installer VM if needed.
- [x] Convert `ctos-kali` from install boot to installed-system boot.
- [x] Start the installed guest and open its console.
- [x] Verify running state and record live outcome.

Implementation note: the installer VM was `paused (user)` with no active libvirt job. Added `libvirt/domains/ctos-kali.xml` and `scripts/ctos-kali finalize-install`, then ran `scripts/ctos-kali finalize-install --force-stop --start`. `ctos-kali` is running from disk `vda` only; the installer ISO is no longer attached.

Update 2026-06-04: user reached the installed Kali Xfce desktop after login. Host-to-guest ping to `192.168.130.50` succeeded with 0% packet loss. Next safe step is a guest-side network sanity check, clean shutdown, then baseline snapshot.

## Active Kali Guest Network Egress Fix

- [x] Verify host-side `ctos-nat` forwarding/NAT state.
- [x] Verify whether the installed guest has route/DNS configured after manual installer networking.
- [x] Apply the smallest safe fix.
- [x] Re-test guest IP egress and DNS.

Host-visible state: `ctos-nat` is active, NAT mode is declared, `net.ipv4.ip_forward=1`, host route to `192.168.130.0/24` exists on `virbr-ctos`, and guest interface is attached to `ctos-nat`. The remaining fault was host firewall/NAT egress: a standalone `/etc/nftables.conf` `inet filter forward` chain had policy `drop` without CTOS VM forward exceptions. Runtime and persistent fixes are now applied. After reboot/restart, Kali can ping `1.1.1.1` and resolve `deb.debian.org`.

## Active Kali Guest Agent Access

- [x] Confirm qemu-guest-agent is reachable in `ctos-kali`.
- [x] Add repo helper for controlled guest commands.
- [x] Use guest-agent access to inspect Kali network and voice/accessibility state.

Implementation note: `scripts/ctos-kali-agent` uses qemu-guest-agent `guest-exec`; it does not require SSH. Used it to disable Kali `orca`, user `speech-dispatcher.service`, and user `speech-dispatcher.socket`. Orca autostart was hidden and the GNOME accessibility screen-reader flag was set false for user `ctos`.

## Active Host Firewall Report

- [x] Confirm guest egress still fails through both `ctos-nat` and a temporary live NIC on libvirt `default`.
- [x] Add root-only firewall report helper.
- [x] Have operator run the report with sudo and inspect output.
- [x] Identify the standalone nftables `inet filter forward` policy drop as the blocker.
- [x] Apply runtime CTOS forward allow rules.
- [x] Re-test Kali egress.
- [x] Persist CTOS VM egress rules in `/etc/nftables.conf`.

Report result: firewalld/libvirt allow and NAT rules are present, but `/etc/nftables.conf` creates `table inet filter` with `chain forward` policy `drop` and no allow rules. Added `scripts/ctos-firewall-fix-vm-egress` as a root-only runtime test helper.

Runtime fix result: `sudo scripts/ctos-firewall-fix-vm-egress` restored Kali egress. Guest-agent tests succeeded for gateway, `1.1.1.1`, and `deb.debian.org`.

Persistent fix result: `sudo scripts/ctos-install-host-firewall` installed the equivalent rules in `/etc/nftables.conf`. Guest-agent tests still succeed for `1.1.1.1` and `deb.debian.org`.

## Active Kali Baseline Snapshot

- [x] Confirm installed Kali guest has external IP egress and DNS.
- [x] Confirm Kali voice/accessibility autostart remains disabled.
- [x] Add a repo-owned shutoff disk snapshot command.
- [x] Shut down `ctos-kali` cleanly.
- [x] Create the post-install baseline snapshot.
- [x] Verify the active disk chain and record the restore point.

Snapshot result: `ctos-kali-post-install-20260604` exists. The immutable baseline disk remains `/var/lib/libvirt/ctos/images/ctos-kali.qcow2`; the active running disk is `/var/lib/libvirt/ctos/snapshots/ctos-kali-post-install-20260604.overlay.qcow2`.

Post-battery-cut recovery: `ctos-kali` was verified after reboot, relaunched, and confirmed running from the overlay. Guest internet and DNS still work.

## Active Kali Greeter Voice Disable

- [x] Identify that `orca` was launched by the LightDM greeter, not the `ctos` user session.
- [x] Disable screen-reader GSettings for `lightdm` and `ctos`.
- [x] Add exact-name XDG autostart overrides for `lightdm` and `ctos`.
- [x] Force LightDM greeter a11y reader state off.
- [x] Add a reversible `dpkg-divert` wrapper for `/usr/bin/orca`.
- [x] Restart LightDM and verify there are no active voice/speech processes.

Result: no active `orca`, `speech-dispatcher`, `sd_espeak-ng`, or `sd_dummy` processes remain. `/usr/bin/orca` is diverted to `/usr/bin/orca.distrib`; the replacement `/usr/bin/orca` exits immediately.

## Active Kali Voice-Fixed Snapshot

- [x] Receive user confirmation that Kali is clean after login.
- [x] Add a repo-owned checkpoint snapshot command for an existing overlay chain.
- [x] Shut down `ctos-kali` cleanly.
- [x] Create `ctos-kali-voice-fixed-20260605`.
- [x] Verify the snapshot tree, active disk chain, and guest restart state.

Result: `ctos-kali` is running from `/var/lib/libvirt/ctos/snapshots/ctos-kali-voice-fixed-20260605.overlay.qcow2`. Snapshot tree is `ctos-kali-post-install-20260604 -> ctos-kali-voice-fixed-20260605`. Guest internet, DNS, and no-active-voice-process checks all pass.

## Active Cockpit Kali Controls

- [x] Add detailed `ctos-kali` status to the local cockpit API.
- [x] Add localhost-only VM action endpoint with strict domain/action allowlist.
- [x] Add Kali control buttons and health indicators to the dashboard.
- [x] Sync the terminal TUI with the same Kali state and control boundary.
- [x] Verify status rendering and allowed actions without opening unsafe scope.
- [x] Record the cockpit control boundary and verification.

Result: `/api/status` now includes detailed `ctos-kali` state, active disk/snapshot, snapshot tree, and cached health checks. `/api/vm/action` accepts only `ctos-kali` and fixed actions `start`, `shutdown`, `console`, `checkpoint`. The terminal TUI now shows `KALI CONTROL` with state, snapshot chain, disk role, health summary, and the dashboard action path. Test server verification confirmed status, shutdown no-op, domain allowlist rejection, and TUI rendering.

## Active Archipelago Secondary Mission

- [x] Capture the new fleet/tower/T480 intent without changing the live host.
- [x] Document the EndeavourOS-first archipelago model.
- [x] Add initial fleet role/inventory scaffolding.
- [x] Add a non-destructive USB kit staging helper.
- [x] Record the decision, sources, and open questions.
- [x] Inventory the recovered tower hardware and Windows data risk.
- [x] Stage a temporary USB SSH key/foreground-sshd bridge for tower access.
- [x] Confirm the temporary foreground `sshd` on the tower is reachable from T480 on TCP/22.
- [x] Fix Windows public-key authorization for the temporary T480 SSH bridge.
- [x] Add and verify repo helper `scripts/ctos-tower` for direct temporary SSH operations.
- [x] Decide tower install path: wipe Windows and install EndeavourOS as `ctos-core`.
- [x] Create first role package manifests.
- [x] Create first idempotent post-install bootstrap apply script.
- [x] Write the `ctos-core` wipe/install runbook.
- [x] Add guarded SATA initialization helper for `/srv/ctos`.
- [x] Build/verify a USB kit directory for the tower install.
- [x] Copy the verified kit to the physical USB after the stale `/tmp/ctos-usb` mount is replugged/remounted cleanly.

Result: the repo now treats the T480 as `godfather`, the recovered tower as pending `ctos-core`, and future machines as EndeavourOS worker nodes. Tower diagnostics show Windows 10 Home on a Ryzen 5 2400G / GTX 1650 / ASUS B550 system, with Windows on a 1 TB NVMe and an apparently empty 500 GB SATA SSD available as the safest first EndeavourOS target. OpenSSH service startup fails, but foreground `sshd` can listen; a temporary USB bridge was staged.

SSH bridge validation: TCP/22 is reachable at `192.168.1.18`; public-key authentication now works for local account `desktop-lalfaj9\admin`.

Payload update: USB folder `ctos_tower_ssh_link` now writes the T480 key to both `C:\ProgramData\ssh\administrators_authorized_keys` and the current admin user's `.ssh\authorized_keys`, hardens ACLs, and starts debug foreground `sshd` with logs under `ctos_tower_ssh_link\logs`.

Direct helper result: `scripts/ctos-tower test` and `scripts/ctos-tower inventory` work against `Admin@192.168.1.18` while foreground `sshd.exe` is open on the tower.

Install path update 2026-06-12: user explicitly wants Windows removed and EndeavourOS installed on the tower today. First install target is a simple, recoverable `ctos-core` V1: EndeavourOS on the NVMe, CTOS role bootstrap after first boot, and SATA initialization through a separate guarded helper.

Preparation result 2026-06-12: added manifests, `bootstrap/ctos-apply-role`, `bootstrap/ctos-init-core-storage`, and `docs/TOWER_CTOS_CORE_INSTALL.md`. Verified script syntax, role plan rendering, package/group availability, and USB-kit staging into `/tmp/ctos-core-kit-clean3-2`. Physical USB copy initially failed because `/dev/sdb` disappeared while `/tmp/ctos-usb` remained mounted, causing I/O errors. After replug, copied `ctos-core-kit` to `/tmp/ctos-usb/ctos-core-kit`, verified required files, and ran `sync`; kit size is about 796 KiB on a 3.8 GiB FAT USB. Unmount requires operator sudo password.

## Active Jarvis: Mature Open-Source Substrate

- [x] Stop treating one-word voice misses as the main development path.
- [x] Keep CTOS as the action, approval, and audit boundary.
- [x] Record the mature local/open-source stack selection.
- [x] Add `ctos-jarvis mature-plan` so the adoption path is visible from the operator CLI.
- [x] Add a read-only `ctos-jarvis mature-check` preflight for the mature stack.
- [x] Add default sample inventory/regression commands for the reusable voice-sample loop.
- [x] Keep Open Interpreter/01, OpenVoiceOS, GLM-family models, and AirLLM-style offload as sandbox/reference tracks for now.
- [ ] Run a fresh human push-to-talk `ctos-jarvis run` session and save failed/important samples.
- [ ] Promote the Home Assistant/Wyoming deterministic rail only after the token/onboarding gate is clean.

Current result: `ctos-jarvis mature-plan` prints the selected path: Home Assistant/Wyoming, Wyoming Whisper/faster-whisper, Speech-to-Phrase, Piper, and Ollama on `ctos-core`, all behind CTOS proposals and typed approvals. `ctos-jarvis mature-check` gives a read-only readiness/next-action report before live voice work. `ctos-jarvis samples` and `ctos-jarvis regression` make the reusable sample loop default to `~/.local/state/ctos/jarvis-samples/manifest.jsonl`, so missed phrases such as `agenda` can be captured once and replayed without copying long paths.

Verification 2026-07-07: `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-voice-v2`, `python3 -m json.tool ai/jarvis_stack.json`, `ctos-jarvis mature-plan --commands`, `ctos-jarvis samples`, `ctos-jarvis samples --json`, `ctos-jarvis regression --plan`, `ctos-jarvis regression --backend open-stt --target-tunnel --plan`, a temporary transcript-only regression manifest, `ctos-jarvis smoke`, and targeted `git diff --check` passed.

## Active Remote Control V0

- [x] Inventory current T480 client and `ctos-core` server readiness.
- [x] Confirm SSH is the only active remote-control primitive today.
- [x] Research current official-repo remote-control candidates.
- [x] Add a non-mutating remote-control helper.
- [x] Document the tunnel-first boundary and next install/test lane.
- [x] Add install/tunnel/client/service command generation for KRDP/FreeRDP.
- [x] Operator installed T480 viewer and tower KRDP package with sudo.
- [x] Apply localhost-only KRDP user-service profile on `ctos-core`.
- [x] Generate KRDP TLS certificate and enable PAM login for user `ctos`.
- [x] Verify KRDP listens only on `127.0.0.1:3389`.
- [x] TCP-test an SSH tunnel from T480 `127.0.0.1:3390` to tower `127.0.0.1:3389`.
- [x] Reach KRDP authentication from FreeRDP through the SSH tunnel.
- [x] Diagnose first blank-window attempt as a FreeRDP VAAPI/libavcodec client rendering issue.
- [x] Diagnose first `xfreerdp3` software-only attempt as missing the KRDP-required RDP graphics pipeline.
- [x] Diagnose RDPGFX/no-AVC attempt as rejected because KRDP requires H.264/YUV420.
- [x] Test RDPGFX/AVC `xfreerdp3`; KRDP authenticated and selected caps but still ended with a blank window/client cancellation.
- [x] Prepare VNC fallback commands with Remmina + `libvncserver` on T480 and `krfb` on `ctos-core`.
- [x] Install VNC fallback packages: Remmina VNC support on T480 and `krfb` on `ctos-core`.
- [x] Launch KRFB in the active tower KDE session and detect its default listener.
- [x] Protect KRFB with runtime firewalld rejects on tower port `5900` before client use.
- [x] Verify direct LAN access to `10.42.0.2:5900` is refused.
- [x] Open and TCP-test the SSH VNC tunnel `127.0.0.1:5901 -> ctos-core:127.0.0.1:5900`.
- [x] Detect Remmina keyring blocker and switch the VNC test client command to TigerVNC `vncviewer`.
- [x] Diagnose TigerVNC/KRFB static-frame/no-input behavior and reject KRFB as the V1 backend.
- [x] Add command generation for TigerVNC attached-screen fallbacks: `w0vncserver` on Wayland and `x0vncserver` on Plasma X11.
- [x] Move VS Code to workspace `STATION` so workspace `DESK` can stay dedicated to local desktop/remote-control testing.
- [x] Install `tigervnc` on `ctos-core` for the next attached-screen VNC test.
- [x] Test `w0vncserver` on the current Wayland session and reject it for V1.
- [x] Switch the tower session to Plasma X11 and launch `x0vncserver`.
- [ ] Validate `x0vncserver` refresh and mouse/keyboard input from the T480 viewer.
- [ ] Complete a visually updating, interactive remote-control test through an SSH tunnel.

Result: `scripts/ctos-remote` now provides `status`, `plan`, `install-commands`, `krdp-localhost`, `tunnel-command`, `client-command`, `server-command`, `service-command`, and `ssh`. `krdp-localhost --start` configured a user systemd override so KRDP runs as `/usr/bin/krdpserver --address 127.0.0.1 --plasma`, generated a local TLS cert, enabled `SystemUserEnabled=true`, kept `Autostart=false`, and verified only `127.0.0.1:3389` is listening on `ctos-core`. A temporary SSH tunnel to T480 `127.0.0.1:3390` was TCP-tested and closed. The first FreeRDP visual attempt authenticated but produced a blank window while logging VAAPI/libavcodec hardware-decoder failures. The first `xfreerdp3` software-only attempt was rejected by KRDP with `Client does not support graphics pipeline which is required`; the RDPGFX/no-AVC attempt was rejected with `Client does not support H.264 in YUV420 mode!`; the RDPGFX/AVC attempt selected caps but still stayed blank until the client was cancelled. KRDP remains installed and localhost-only, but is not visually validated.

On 2026-06-16, KRFB was observed listening on `0.0.0.0:5900` and `[::]:5900`; the user added runtime firewalld reject rules for public TCP `5900`, direct T480 access to `10.42.0.2:5900` returned `Connection refused`, and the SSH tunnel on `127.0.0.1:5901` passed a TCP test. Remmina then blocked on a desktop keyring unlock prompt, so `scripts/ctos-remote client-command --protocol vnc` switched to TigerVNC. TigerVNC authenticated and displayed the KRFB desktop, but the frame did not refresh and keyboard/mouse input did not work even after setting `[Security] allowDesktopControl=true` in `~/.config/krfbrc`, restarting KRFB, and disabling viewer remote resize. KRFB is rejected as the V1 backend. The current next backend is TigerVNC attached-screen sharing: try `w0vncserver` through localhost SSH tunnel while still on Wayland; if that fails, switch the tower session to Plasma X11 and use `x0vncserver`.

Runtime note 2026-06-16: VS Code is now on workspace `STATION`, leaving `DESK` for the local desktop-control surface. SSH check confirmed `ctos-core` is reachable but does not yet have `tigervnc`/`w0vncserver`/`x0vncserver` installed. Remote `sudo -n` requires a password, so the package install needs one explicit user-run command before Codex can launch the next test.

Package install note 2026-06-16: first remote `sudo pacman -S --needed tigervnc` failed before commit because several mirrors returned 404 for `tigervnc-1.16.2-3`. Non-sudo SSH inspection showed `/var/lib/pacman/sync/extra.db` timestamp `2026-06-15 00:39:21`; the user then ran `sudo pacman -Syyu --needed tigervnc`, which installed `tigervnc 1.16.2-4` on `ctos-core`.

Wayland attached-screen note 2026-06-16: `w0vncserver` was launched as transient user unit `ctos-w0vnc.service` with `-localhost -rfbport 5902 -SecurityTypes None -AlwaysShared`. It listened only on `127.0.0.1:5902` and `[::1]:5902`, and a T480 SSH tunnel plus TigerVNC client connected. The server logged accepted client/security negotiation but later `Framebuffer updates: 0`; the T480 `vncviewer` process stayed alive without a Hyprland window. The tunnel, viewer, and transient service were stopped. Treat `w0vncserver` on the current Wayland session as rejected for V1; next test is Plasma X11 plus `x0vncserver`.

X11 attached-screen note 2026-06-16: after the tower was switched to Plasma X11, SSH inspection found `kwin_x11`, `DISPLAY=:0`, and `XAUTHORITY=/tmp/xauth_wHykbD`. `x0vncserver` was launched as transient user unit `ctos-x0vnc.service` with `-display :0 -localhost -rfbport 5902 -SecurityTypes None -AlwaysShared -AcceptKeyEvents -AcceptPointerEvents -AcceptSetDesktopSize=0`. It listened only on `127.0.0.1:5902` and `[::1]:5902`, detected XTest 2.2 for input, and accepted a tunnelled TigerVNC client. Hyprland now shows `ctos@ctos-core - TigerVNC` on workspace `DESK` and VS Code remains on `STATION`. Human validation of refresh and pointer/keyboard input is still pending.

Network recovery update 2026-06-12: after offline install, tower Wi-Fi can scan but NetworkManager reports missing `802-11-wireless-security.key-mgmt`. Added `bootstrap/roles/ctos-core/network-usb/ctos-core-netfix` and copied it to `/tmp/ctos-usb/ctos-core-netfix/ctos-core-netfix`. It can create a diagnostic report, recreate Wi-Fi profiles with explicit key management, and attempt iPhone USB tethering without writing Wi-Fi secrets to logs.

Ethernet recovery update 2026-06-14: T480 Ethernet `enp0s31f6` detects carrier to the tower and was changed to NetworkManager shared mode on profile `Wired connection 1`. T480 now owns `10.42.0.1/24` on Ethernet while Wi-Fi remains on `192.168.1.21/24` via `Livebox-8F18`. No tower ARP/IP was visible immediately after activation, so the tower side likely needs its wired profile reconnected or configured to DHCP/static `10.42.0.2/24`.

USB command pack update 2026-06-14: added `bootstrap/roles/ctos-core/ethernet-rescue/ctos-ethernet-rescue` and copied it to `/tmp/ctos-usb/ctos-ethernet-rescue/`. The script supports `diag`, `dhcp`, `static`, and `auto`; it writes reports under `outputs/` and targets the T480 shared Ethernet rescue network (`10.42.0.1/24`).

Tower Ethernet feedback 2026-06-14: latest USB report `ethernet-20260614-234920` shows DHCP failed on the tower, static fallback succeeded with `enp6s0 = 10.42.0.2/24`, and ping to T480 `10.42.0.1` has 0% packet loss. Ping to `1.1.1.1` still has 100% packet loss and DNS fails, so the remaining blocker is T480 Internet egress/firewall/NAT. Added `scripts/ctos-firewall-fix-tower-egress` to apply runtime firewalld/nft forwarding and masquerade rules for `10.42.0.0/24 -> wlan0`.

Direct T480-to-tower check 2026-06-14: after the egress fix, T480 can ping tower `10.42.0.2` with 0% packet loss. TCP/22 on the tower returns connection refused, so SSH is not yet available; tower needs `openssh` installed and `sshd.service` enabled/started.

Tower SSH bridge complete 2026-06-14: user installed the T480 SSH key with `ssh-copy-id -F /dev/null ctos@10.42.0.2`. T480 can now SSH key-only to `ctos@10.42.0.2`. Verified tower hostname `ctos-core`, EndeavourOS, kernel `6.18.4-arch1-1`, ASUS ROG STRIX B550-F GAMING BIOS `1401`, Ethernet `enp6s0=10.42.0.2/24`, and Internet/DNS through T480 with 0% loss to `1.1.1.1` and `endeavouros.com`.

## Active Tower Bootstrap: ctos-core Role

- [x] Revalidate tower reachability after sleep/resume.
- [x] Copy the current CTOS repo/kit to `/home/ctos/T480` on the tower.
- [x] Make the bootstrap conservative about existing display-manager configuration.
- [x] Diagnose first apply attempt as stopped before pacman transaction completion.
- [x] Replace pacman group names with explicit package names in the desktop manifest.
- [x] Run `bootstrap/ctos-apply-role ctos-core apply` on the tower with operator-confirmed sudo.
- [x] Verify role marker, services, repo copy, and CTOS service directories.
- [x] Remove the temporary bootstrap sudo rule from the tower.
- [x] Reboot the tower once so it boots the newly installed kernel.
- [ ] Decide and apply the SATA `/srv/ctos` initialization only after confirming disk identity.

Bootstrap result 2026-06-15: after refreshing `archlinux-keyring` and `endeavouros-keyring`, the role apply completed. Verified `/etc/ctos-role`, active `NetworkManager`, `sshd`, and `avahi-daemon`, preserved SDDM as the active display manager, created `/opt/ctos/repo` and `/srv/ctos/{cache,models,workers,snapshots,packages}`, installed `qemu-full`, `libvirt`, `podman`, `podman-compose`, `xfce4-session`, `lightdm`, and `crun`, and confirmed DNS through the T480 link. Temporary passwordless sudo now fails with `sudo: a password is required`. Reboot remains required because the running kernel is `6.18.4-arch1-1` while package `linux 7.0.12.arch1-1` is installed.

Post-reboot validation 2026-06-15: `ctos-core` is reachable over SSH at `10.42.0.2`, running kernel `7.0.12-arch1-1`, with `NetworkManager`, `sshd`, and `avahi-daemon` active. The T480 gateway and DNS both work, SDDM remains the display manager, and passwordless sudo remains closed.

## Active ctos-core Post-Welcome Stabilization

- [x] Audit the tower after EndeavourOS Welcome tasks.
- [x] Confirm display/session state without changing the display manager.
- [x] Identify the NVMe OS disk and SATA service disk by stable `/dev/disk/by-id` names.
- [x] Decide whether to initialize the SATA SSD as `/srv/ctos`.
- [x] Record the verified state and next operator action.

Post-Welcome audit 2026-06-15: `ctos-core` remains healthy after Welcome tasks. Kernel `7.0.12-arch1-1`, SDDM active, `NetworkManager`/`sshd`/`avahi-daemon` active, no failed systemd units, no pacman lock, T480 gateway and DNS OK. The OS is on NVMe `nvme-WDC_PC_SN720_SED_SDAQNTW-1T00_193915800317`; the unused service candidate is SATA `ata-Samsung_SSD_850_EVO_500GB_S3R3NF1JB01054J` -> `/dev/sda`, 465.8 GiB, unmounted and with no filesystem shown by `lsblk`. `bootstrap/ctos-init-core-storage plan` targets that SATA disk for Btrfs label `CTOS_SRV`.

SATA `/srv/ctos` result 2026-06-15: initialized `ata-Samsung_SSD_850_EVO_500GB_S3R3NF1JB01054J` as `/dev/sda1` Btrfs label `CTOS_SRV`, UUID `d7db0dbc-63ea-4add-a609-5bde6783bd5f`, mounted at `/srv/ctos` with `noatime,compress=zstd:3`. Permissions repaired to `root:ctos` with setgid on `/srv/ctos` and expected subdirectories. User `ctos` write test succeeded.

## Active ctos-core Control Integration

- [x] Add a T480-side `ctos-core` helper for status, SSH, and storage checks.
- [x] Expose `ctos-core` state in the local cockpit status snapshot.
- [x] Render `ctos-core` in the terminal and web cockpit.
- [x] Verify helper and cockpit output over the Ethernet rescue link.
- [x] Record the control boundary and verification.

Control result 2026-06-15: added `scripts/ctos-core` with `status`, `status --json`, `ssh`, and `ping`. The helper uses key-based SSH to `ctos@10.42.0.2` and does not run sudo or mutate the tower. `control/status.py` now includes cached `core` status, the TUI renders `CTOS CORE`, and the web dashboard has a status-only `Core Node` panel. Verified `core.available=true`, host `ctos-core`, kernel `7.0.12-arch1-1`, `/srv/ctos=/dev/sda1`, `srv.writable=true`, T480/DNS checks OK, and passwordless sudo closed.

## Active ctos-core Services V1

- [x] Define a non-daemon service/storage layout under `/srv/ctos`.
- [x] Add T480-controlled commands to plan/apply the layout without sudo.
- [x] Add T480-to-core repo subset sync without rsync.
- [x] Verify layout completeness, marker, and repo copy on `ctos-core`.
- [x] Surface layout completeness in the helper and cockpit.
- [x] Document the boundary and next real-service step.

Services V1 result 2026-06-15: `scripts/ctos-core` now supports `plan-services`, `apply-layout`, and `sync-repo`. The layout creates `/srv/ctos/repo/t480`, `/srv/ctos/packages/{pacman/pkg,incoming}`, `/srv/ctos/cache/{git,python,node}`, `/srv/ctos/models/{ollama,huggingface}`, `/srv/ctos/workers/{queue,active,done,failed}`, and `/srv/ctos/state` without sudo, package installs, daemons, or open ports. The repo subset is synced to `/srv/ctos/repo/t480` via tar over SSH with explicit exclusions for `.git`, Codex state, VM disks, ISOs, images, and logs. Verified `layout.complete=true`, marker `/srv/ctos/state/layout-v1.json`, repo copy size about 804 KiB, and dashboard API reports layout complete.

## Active Fleet Inventory V1

- [x] Record planned feature tracks: remote control, fleet inventory, telemetry/constants, and storage expansion.
- [x] Add a static fleet inventory library.
- [x] Add a `ctos-fleet` helper for list, features, and live status.
- [x] Aggregate live status for T480 and `ctos-core`.
- [x] Expose fleet status in the cockpit API, TUI, and web dashboard.
- [x] Verify JSON, helper output, and dashboard API.

Fleet result 2026-06-15: added `fleet/nodes.json` and `scripts/ctos-fleet`. Inventory currently declares `ctos-t480`, `ctos-core`, and planned `ctos-worker-01`, plus feature tracks `remote-control`, `fleet-inventory`, `fleet-telemetry`, and `storage-expansion`. Live status pulls are explicit and status-only: local read for T480 and SSH read through `scripts/ctos-core` for `ctos-core`. Verified `ctos-t480` and `ctos-core` online, worker planned, and dashboard API includes the `fleet` block.

## Active Desktop Boot Cockpit V1

- [x] Inspect current Hyprland/desktop launcher scripts and wallpaper path.
- [x] Add a repo-owned startup orchestrator for CTRL/DESK/VMS windows.
- [x] Add a VMS quick-control window with Kali launch/console commands available but no automatic VM start.
- [x] Restore the repo background image from `Assets/BackGround/4.webp`.
- [x] Apply the repo desktop config to the live user config and reload/verify.
- [x] Record the startup boundary and verification.
- [ ] Validate the full startup sequence after a real logout/login or reboot.

Result 2026-06-16: added `scripts/ctos-wallpaper`, `scripts/ctos-session`, `scripts/ctos-desk-remote`, and `scripts/ctos-vms-panel`. Hyprland now runs `ctos-wallpaper`, Waybar, Mako, and `ctos-session boot` at startup. The repo wallpaper `Assets/BackGround/4.webp` is active through `swaybg`. Live window state after manual boot test: `CTOS_CONTROL` on `CTRL`, `ctos@ctos-core - TigerVNC` on `DESK`, `CTOS_VMS` on `VMS`, and VS Code remains on `STATION`. `ctos-vms-panel` gives explicit Kali actions without automatically starting the VM. Hyprland `windowrulev2` was replaced with current `windowrule = match:...` syntax after deprecation errors; `hyprctl configerrors` now returns no errors. Full reboot validation remains pending.

Workspace update 2026-06-16: the visible host strip is now `CTRL`, `DESK`, `STATION`, `VMS`, `AI`, `VAULT`, `COMMS`, `GAME`. `CODE` was removed, former `WORK` became `STATION`, and `VMS` moved left of `AI`. DESK uses a workspace-specific no-gap/no-border rule so the remote desktop frame fills the usable screen area under Waybar.

DESK refinement 2026-06-16:

- [x] Inspect TigerVNC and tower display geometry.
- [x] Remove avoidable vertical scrollbars from the DESK remote view.
- [x] Prefer intuitive viewport movement over visible scroll controls if TigerVNC supports it.
- [x] Apply and verify the DESK profile live.

DESK refinement note 2026-06-16: TigerVNC documents edge scrolling by bumping the mouse against the screen edge in full-screen mode. The tower currently exposes two X11 outputs side by side, originally `3840x1200`. `scripts/ctos-desk-remote` now applies a panorama layout at `3840x1080` when two outputs are connected, restarts `x0vncserver` after layout changes, and opens TigerVNC with `-FullScreen -FullScreenMode=Current -FullScreenSystemKeys=0 -RemoteResize=0 -Shared`.

Live verification 2026-06-16: `ctos-core` X11 now reports `Screen 0 ... current 3840 x 1080`; Hyprland reports the TigerVNC client on workspace `DESK` at `0,0` with size `1920x1080` and fullscreen state enabled. This intentionally hides Waybar while DESK is focused because TigerVNC edge scrolling is a full-screen behavior.

DESK drag-across refinement 2026-06-16:

- [x] Confirm whether TigerVNC exposes a setting for drag-aware edge panning.
- [x] Confirm TigerVNC upstream edge scrolling is drag-aware, but has no exposed speed/threshold option.
- [x] Reject Remmina scaled fallback for V1 because it reopens the desktop keyring prompt and exits before a clean unattended DESK session.
- [x] Reject the full global/scaled DESK view on UX grounds after user test; it makes the desktop feel worse, not better.
- [x] Tune the TigerVNC DESK launch for responsive pointer events while keeping tunnel-only fullscreen panorama.
- [ ] Human-validate drag/select/resize across the tower monitor boundary from the T480.

Drag-across note 2026-06-16: TigerVNC source includes edge scrolling for pointer drag events, so the intended model is: hold the drag/selection/resize, touch the local left/right edge, and let the fullscreen viewport pan over the `3840x1080` remote desktop. The client does not expose an option to tune edge-scroll speed/threshold. Do not pursue full global/scaled DESK view as the next fallback; the user explicitly rejected the feel of that mode.

## Active ctos-core Wi-Fi Uplink Test

- [x] Probe the tower over the Ethernet rescue SSH link.
- [x] Confirm the external USB Wi-Fi adapter, NetworkManager profile, and current failure mode.
- [ ] Try the smallest stable NetworkManager profile correction without dropping Ethernet rescue.
- [ ] Test Wi-Fi IP, internet reachability, and DNS from `ctos-core`.
- [ ] Decide whether this dongle is good enough for temporary outside access or should be set aside.

Initial finding 2026-06-17: `ctos-core` sees the external adapter as `wlan0` using `rtw89_8852bu`. The saved `Livebox-8F18` profile exists with `wifi-sec.key-mgmt=wpa-psk` and an available secret, but activation currently fails in wpa_supplicant with association/scan timeouts rather than the older missing `key-mgmt` error.

Blocker 2026-06-17: after the initial Wi-Fi diagnostic, the tower still answers ICMP on `10.42.0.2` and TCP/22 accepts connections, but OpenSSH times out during banner exchange before authentication. No Wi-Fi profile mutation was confirmed after this point. Resume by restarting `sshd` or rebooting `ctos-core`, then re-run the profile-stability attempt over the Ethernet rescue link.

Update 2026-06-17: Wi-Fi stabilization was explicitly deferred. A foreground emergency `sshd` on `ctos-core:2222` works, and `scripts/ctos-desk-remote` now accepts `CTOS_CORE_SSH_PORT` so the DESK stream can be restored through that temporary SSH path. Verified DESK/TigerVNC restored via `CTOS_CORE_SSH_PORT=2222`; Hyprland reports `ctos@ctos-core - TigerVNC` on workspace `DESK`. Normal TCP/22 still accepts connections but times out during SSH banner exchange and needs a later service diagnosis.

## Active Restart-Safe Cockpit Contract

- [x] Verify why `ctos-kali` is reported as unavailable in the VMS panel.
- [x] Make DESK prefer normal SSH/22 and fall back to the documented temporary SSH/2222 path while the tower service is being repaired.
- [x] Add a repo-owned ctos-core boot contract for SSH, restricted rescue SSH, optional X11 autologin, and tunnel-only VNC.
- [x] Sync the boot contract to `ctos-core`.
- [x] Apply and verify the live T480 startup path.
- [x] Record the restart contract and remaining tower-side requirement.
- [x] Run the tower-side boot contract with sudo on `ctos-core`.
- [ ] Validate the full startup sequence after a real two-machine reboot.
- [x] Add a local DESK guard that reopens the remote desktop when the tower X11 session is reachable.

Restart-safe update 2026-06-17: VMS was using invalid `virsh` argument order; `scripts/ctos-vms-panel` now passes `--readonly` to `virsh` correctly and reports detailed libvirt errors. Outside the sandbox, `virsh -c qemu:///system --readonly domstate ctos-kali` reports `shut off`, so the domain exists. `scripts/ctos-desk-remote` now tries SSH ports `22 2222` by default, waits up to 240 seconds for the tower during boot, and successfully restored DESK through normal SSH/22. The tower-side script `bootstrap/roles/ctos-core/boot/ctos-core-boot-contract` is synced to `/srv/ctos/repo/t480` on `ctos-core`; it still needs a local sudo run to make rescue SSH persistent across tower reboot. Autologin into Plasma X11 is explicit via `--enable-autologin`.

Post-tower-reboot check 2026-06-17: `ctos-core` came back at `10.42.0.2`; SSH `22` and rescue SSH `2222` both accept key authentication, and `ctos-sshd-rescue.service` is active. SDDM autologin succeeded, but into Plasma Wayland (`startplasma-wayland`) instead of Plasma X11, so `kwin_x11` was absent and DESK/x0vnc cannot auto-attach yet. Updated `ctos-core-boot-contract` to neutralize the older `/etc/sddm.conf` `Session=plasma` line before writing the CTOS `plasmax11.desktop` autologin drop-in; synced this fix to `/srv/ctos/repo/t480`.

Follow-up check 2026-06-17: after relaunching the T480 cockpit, Hyprland shows `CTOS_CONTROL`, `CTOS_DESK`, and `CTOS_VMS` on their expected workspaces, and `ctos-control` is running on `127.0.0.1:8765`. Local libvirt sees `ctos-kali` as `shut off`. The tower still needs the synced boot contract applied with local sudo because `sudo -n` over SSH requires a password; until then DESK cannot auto-attach after tower reboot because the current tower session remains Plasma Wayland.

Tower reboot validation 2026-06-17: after a full tower power-off/power-on, `ctos-core` autologged directly into Plasma X11 (`startplasma-x11`, `kwin_x11`). `/etc/sddm.conf` now comments the old `Session=plasma` line and the CTOS drop-in selects `plasmax11.desktop`. `scripts/ctos-desk-remote` restored the DESK stream through SSH/22, set the tower X11 layout to `3840x1080`, started `x0vncserver` on `127.0.0.1:5902` only, opened the local SSH tunnel, and launched TigerVNC fullscreen on workspace `DESK`. `ctos-kali` remains visible locally as `shut off`.

DESK guard update 2026-06-17: `scripts/ctos-session boot` now starts `scripts/ctos-desk-guard` in the Hyprland session. The guard checks SSH `22/2222`, remote `kwin_x11`, remote localhost-only `x0vncserver`, the local SSH tunnel, and the local TigerVNC process every 20 seconds. If the tower desktop is reachable and the viewer was closed, it relaunches `scripts/ctos-desk-remote` in non-interactive mode and reopens TigerVNC on `DESK`. Live check after the user closed DESK: the guard healed `viewer=0 tunnel=1 remote_vnc=1`, reopened TigerVNC, and `ctos-desk-guard status` reported all five checks healthy.

## Active Tower Workstation Bootstrap

- [x] Inspect `ctos-core` for existing VS Code/Codex prerequisites.
- [x] Install official VS Code binary on `ctos-core`.
- [x] Install Codex CLI on `ctos-core`.
- [x] Install the OpenAI VS Code extension on `ctos-core`.
- [x] Verify `code`, `codex`, and extension availability from the tower session.
- [x] Record the tower workstation install decision.

Initial finding 2026-06-17: `ctos-core` already has `nodejs 26.2.0-1`, `npm 11.16.0-1`, `git`, `base-devel`, and `yay`. `code` and `codex` are not installed, and no OpenAI/Codex VS Code extension is present yet.

Result 2026-06-17: added `scripts/ctos-core-install-workstation` for a sudo-free user install on `ctos-core`. Installed official VS Code stable tarball under `/home/ctos/.local/opt/vscode`, linked `code` and `codex` under `/home/ctos/.local/bin`, installed Codex CLI `0.140.0` via npm user prefix, and installed VS Code extension `openai.chatgpt`. `bash -lc` on `ctos-core` now finds both `code` and `codex`; `code --version` reports `1.125.0`.

## Active CTOS AI V0

- [x] Scan current open-source AI/operator projects for usable patterns.
- [x] Keep CTOS as the architecture center rather than adopting a generic Jarvis stack wholesale.
- [x] Document the V0 assistant model, permission tiers, storage boundary, and first implementation slice.
- [x] Record the architecture decision and source registry entries.
- [x] Implement deterministic `ctos-agenda` and `ctos-ai` V0 scripts.
- [x] Expose read-only AI/agenda readiness in `CTRL`.
- [x] Add a daily/operator brief command as the first Jarvis-like entrypoint.
- [x] Expose common CTOS commands through user-local `~/.local/bin` shims.
- [x] Scan GLM-5.2 and AirLLM for runtime implications.
- [x] Add a proper approval surface before any Tier 2 mutable tool is exposed to a model.
- [x] Add provider/runtime profiles before selecting a first model backend.
- [x] Add a no-network-by-default dry-run adapter before activating a first runtime.
- [ ] Decide model/runtime integration after dry-run probes, secrets policy, and storage policy are stable.

Design result 2026-06-17: added `context/20_ctos_ai_v0_model.md`. V0 will start as a deterministic, tool-governed local assistant with an agenda and CTOS tool contract, not an unrestricted shell or always-on voice agent. Open-source projects are treated as inspiration and possible future dependencies: OpenHands for agent/workstation patterns, Open Interpreter for conversational local operation, LangGraph for durable workflows, MCP for future tool exposure, and OpenAI computer-use/Agents concepts for later bounded visual/action loops.

Implementation result 2026-06-17: added executable scripts `scripts/ctos-agenda` and `scripts/ctos-ai`. `ctos-agenda` uses Python stdlib SQLite with default state outside Git at `~/.local/share/ctos-ai/agenda.sqlite3`; verified with a temporary DB in `/tmp`. `ctos-ai` currently supports `capabilities`, `status`, `search-context`, `agenda`, `plan-day`, `open-desk`, and `open-vms`. No model runtime, daemon, root action, or network-exposed service was added.

CTRL integration result 2026-06-17: `control/status.py` now exposes read-only CTOS AI readiness: model runtime deferred, `ctos-ai`/`ctos-agenda` tool availability, agenda DB path/existence/writability, task counts, and permission tier hints. The terminal cockpit renders this as `CTOS AI`, and the web dashboard `AI Workers` panel now shows tool contract, agenda, model runtime, Ollama, and planned workers.

Live result 2026-06-18: `scripts/ctos-control serve` is running on `127.0.0.1:8765`. The real user agenda DB was initialized at `~/.local/share/ctos-ai/agenda.sqlite3`; `/api/status` reports `db_exists=true`, `state_root_writable=true`, both CTOS AI tools available, and model runtime intentionally deferred.

Brief result 2026-06-18: `scripts/ctos-ai brief` is available as the first deterministic Jarvis-like entrypoint. Live verification outside the sandbox reported host `ctos-node`, core `ctos-core` with `/srv/ctos` free space, Kali `shut off` on snapshot `ctos-kali-voice-fixed-20260605`, empty real agenda, and next recommendation to add one concrete agenda task.

User command result 2026-06-18: added `scripts/ctos-install-user-bin`, linked common CTOS commands into `~/.local/bin`, and appended a guarded PATH block to `~/.bashrc`. Verified from `~` in a fresh interactive Bash shell that `command -v ctos-ai` returns `/home/operator/.local/bin/ctos-ai` and `ctos-ai brief` runs without `cd ~/T480`.

CLI polish result 2026-06-19: `ctos-ai` with no subcommand now defaults to the operator brief, while `ctos-ai -h` still shows the command help. The brief recommendation text now points to the user-local `ctos-ai plan-day` command instead of the repo-relative script path. Live verification outside the sandbox reported `ctos-core` available, Kali `shut off`, agenda item `#1`, and `ctos-ai plan-day` produced a 09:00-09:30 block.

Runtime scan result 2026-06-19: GLM-5.2 is kept as a future external/frontier model candidate, not a local runtime target for current hardware. AirLLM is kept as experimental offload inspiration, not the V1 assistant runtime. Next implementation step remains the Tier 2 approval surface, followed by provider/runtime profiles.

Approval surface work 2026-06-19:

- [x] Define a local approval queue stored outside Git.
- [x] Add an allowlist for first CTOS Tier 2 actions.
- [x] Add propose/list/show/approve/reject commands.
- [x] Verify that no arbitrary command can be queued or executed through the approval path.

Approval result 2026-06-19: `ctos-ai` now exposes `actions`, `propose`, `approvals`, `show`, `approve`, and `reject`. The queue defaults to `~/.local/share/ctos-ai/approvals.sqlite3`, stores target/risk/rollback metadata, and executes only static allowlisted CTOS actions. Verification used a temporary `/tmp` DB and no live mutable action was executed.

CTRL approval visibility work 2026-06-19:

- [x] Expose approval DB counts and pending records in the read-only control status snapshot.
- [x] Render pending approvals in the terminal `CTRL` cockpit.
- [x] Render pending approvals in the web dashboard AI panel and event feed.
- [x] Verify with a temporary approval DB and compile checks.

CTRL approval result 2026-06-19: `control/status.py` now reads `~/.local/share/ctos-ai/approvals.sqlite3` or `CTOS_AI_APPROVAL_DB` in SQLite read-only mode and exposes counts plus the latest pending records under `ai.approvals`. The terminal cockpit displays pending/failed/total approval counts and up to three pending action IDs. The web dashboard AI panel and event feed now surface pending approvals without adding an approve/execute button. Verification used a temporary `/tmp` approval DB with two pending records; no live mutable action was executed. The live localhost dashboard was restarted and confirmed to expose `ai.approvals`; the live `CTOS_CONTROL` TUI window was relaunched with the updated renderer.

Provider/runtime profile work 2026-06-19:

- [x] Research current official/primary sources for candidate runtime interfaces.
- [x] Add repo-owned provider/runtime profiles without secrets or installs.
- [x] Add `ctos-ai` commands to list/show/recommend runtime profiles.
- [x] Expose profile summary in `CTRL`.
- [x] Record the runtime abstraction decision and verification.

Provider/runtime profile result 2026-06-19: added inert profiles under `ai/runtime_profiles.json` for OpenAI Responses API, Ollama on `ctos-core`, llama.cpp server, GLM-5.2 external/provider, and AirLLM offload experiments. `ctos-ai runtimes`, `ctos-ai runtime <id>`, and `ctos-ai runtime-recommend` render the model-backend registry without installing or activating anything. `control/status.py`, the terminal cockpit, and the web dashboard expose profile count and active profile; `active_profile` remains `none`. The live localhost dashboard was restarted and `/api/status` confirmed `ai.runtime_profiles.count=5`.

Runtime dry-run adapter work 2026-06-19:

- [x] Add a no-network-by-default runtime check command.
- [x] Validate profile schema, endpoint shape, and secret presence without printing secret values.
- [x] Add optional owned-node target probing for `ctos-core`.
- [x] Expose the adapter contract in `CTRL` status.
- [x] Verify commands and document the decision.

Runtime dry-run adapter result 2026-06-19: `ctos-ai runtime-check <id>` now validates runtime profile metadata, endpoint shape, and secret environment variable presence by name only. It does not contact external endpoints or models by default. `--target-probe` is available for owned `ctos-core` checks; live verification confirmed SSH reachability, `/srv/ctos` writable, and `/srv/ctos/models/ollama` ready for the Ollama candidate. OpenAI remains blocked by missing `OPENAI_API_KEY` and the unresolved secrets/privacy decision. `control/status.py`, the terminal cockpit, and the web dashboard expose the adapter contract. The localhost dashboard was restarted and `/api/status` confirmed `network_default=false`, `model_contact_default=false`, and `target_probe_optional=true`.

Ollama core benchmark preparation work 2026-06-20:

- [x] Research current package/API/model sources for a tiny local benchmark.
- [x] Add a repo-owned benchmark plan with localhost-only constraints.
- [x] Add a T480-side benchmark helper for plan/preflight/status/pull/bench steps.
- [x] Keep install/model-download/benchmark execution explicit, not automatic.
- [x] Verify the helper locally and against `ctos-core` read-only.
- [x] Record the package/service/cache decision.

Ollama benchmark preparation result 2026-06-20: added `ai/benchmarks/ollama_core_local_v0.json` and executable `scripts/ctos-ollama-bench`, exposed as `~/.local/bin/ctos-ollama-bench`. The plan uses Arch package `ollama`, localhost bind `127.0.0.1:11434`, model cache `/srv/ctos/models/ollama`, and first tiny Qwen2.5-Coder smoke/benchmark models. Local checks passed. Live read-only preflight on `ctos-core` found Ollama not installed, no listener, API offline, model cache ready/writable, 3.12 GiB RAM available, GTX 1650 + AMD Raven/Vega detected, and sudo password required. No package was installed and no model was downloaded.

Ollama install handoff 2026-06-21: live read-only preflight still finds Ollama absent on `ctos-core`, API offline, `/srv/ctos/models/ollama` writable, 2.8 GiB RAM available, and sudo password required. Added `ctos-ollama-bench install-interactive --yes` so the operator can run a single visible T480 command, type the tower sudo password once, and then let Codex continue with `preflight`, `status`, `pull`, and `bench`.

Ollama smoke result 2026-06-21: operator ran `ctos-ollama-bench install-interactive --yes`; `ctos-core` now has `ollama 0.30.8-1`, `ollama.service` active/enabled, localhost API `127.0.0.1:11434`, and model cache under `/srv/ctos/models/ollama`. Pulled `qwen2.5-coder:0.5b` and benchmarked it successfully. Result JSON lives on `ctos-core` at `/srv/ctos/state/ai/benchmarks/ollama-qwen2.5-coder-0.5b-20260621-020230.json`; the two non-trivial prompts generated at about 35 tokens/s after load. `ai/runtime_profiles.json` now marks `ollama-core-local` as `dry_run_ready`, but `active_profile` remains unset until a bounded command or stronger benchmark is chosen.

Bounded ask result 2026-06-21: added `ctos-ai ask-local` as the first model-backed command. It sends only the explicit prompt to `qwen2.5-coder:0.5b` on `ctos-core` through SSH/Ollama, does not read files/context/memory automatically, and exposes no CTOS tools to the model. Live proof returned `CTOS_LOCAL_OK` with about 44.86 tokens/s for the tiny response. `ollama-core-local` is now `ready` / `bounded_call_verified`, while `active_profile` remains unset until the V1 surface is decided.

Ollama 1.5B benchmark work 2026-06-21:

- [x] Re-check `ctos-core` Ollama service and cache state.
- [x] Pull `qwen2.5-coder:1.5b` through the localhost-only Ollama API.
- [x] Run the same synthetic benchmark prompts against the 1.5B model.
- [x] Compare measured speed/behavior with the 0.5B smoke result.
- [x] Keep `active_profile` unset until the V1 interaction surface is decided.

Ollama 1.5B result 2026-06-22: `qwen2.5-coder:1.5b` is now cached on `ctos-core` and benchmarked. Result JSON lives at `/srv/ctos/state/ai/benchmarks/ollama-qwen2.5-coder-1.5b-20260622-021732.json`. It completed all prompts, but the two non-trivial prompts generated at about 16.5 and 16.2 tokens/s, roughly half the 0.5B speed. `ctos-ai ask-local --model qwen2.5-coder:1.5b` also works and returned `CTOS_15B_OK`. Keep 0.5B as the fast default for now; use 1.5B explicitly for deliberate checks.

## Active Cockpit TUI Scrollback Fix

- [x] Identify why repeated `CTOS CONTROL // HOST COCKPIT` frames stayed visible.
- [x] Switch the terminal cockpit to the terminal alternate screen.
- [x] Restore cursor and normal screen on Ctrl+C, SIGHUP, or SIGTERM.
- [x] Fit each rendered frame to the current terminal height.
- [x] Sanitize embedded newlines so one status row cannot create extra terminal rows.
- [x] Switch wide terminal rendering to a two-column cockpit layout.
- [x] Relaunch the live cockpit window after verification.

Implementation note 2026-06-18: `control/tui.py` now behaves like a full-screen terminal app instead of printing each refresh into normal terminal history.
Live result 2026-06-18: `python /home/operator/T480/control/tui.py` is running in the real Hyprland session after relaunch. Height tests for 12/24/40-line frames now render exactly 12/24/40 terminal lines, so the frame should not push its header out of view.
Layout update 2026-06-18: wide terminals now render as two columns: local host/core/fleet on the left, virtualization/Kali/AI/services on the right. Narrow terminals keep the single-column fallback.

## Active CTOS AI Loop/API/Voice V1

- [x] Capture the durable loop methodology instead of relying on injected prompt stacks.
- [x] Add a default CTOS identity contract for local model calls.
- [x] Add a localhost-only Ollama tunnel helper.
- [x] Add a small local HTTP API for fast `health` and `ask` calls.
- [x] Add a managed local API server and `/chat` endpoint.
- [x] Add an in-memory local chat loop.
- [x] Add a bounded voice wrapper for typed prompts with spoken replies.
- [x] Verify live identity, tunnel, API, and voice wrapper.
- [x] Decide whether speech-to-text should use Whisper.cpp, Vosk, browser/WebSpeech, or a different backend.
- [x] Add a Vosk-based push-to-talk recording/transcription path.
- [x] Install or verify the local Vosk package and French small model outside the repo.
- [x] Verify `ctos-voice listen-once` with a local STT sample and recorder smoke test.

Implementation note 2026-06-23: V1 deliberately keeps voice input blocked unless a verified STT backend exists. `ctos-voice` can speak model responses and run tiny read-only intents, but it does not launch arbitrary processes or execute model-suggested commands.
Verification note 2026-06-23: live checks passed for `ctos-ai ask-local` identity, detached tunnel status, `ctos-ai-api health`, `ctos-ai-api ask`, `ctos-ai-api serve` with `GET /health`, `ctos-ai-api-server start/status`, `ctos-ai-chat`, `ctos-voice probe`, `ctos-voice ask --no-speak`, `ctos-voice chat --no-speak`, and `ctos-voice command --no-speak brief`. `ctos-voice listen-once` correctly reports that no STT backend is verified yet.
STT decision 2026-06-23: choose Vosk small French as the first push-to-talk backend because it is offline, packaged on Arch, and lighter than Whisper for short commands on T480-class hardware. Always-on wake-word remains out of scope.
STT implementation note 2026-06-23: `ctos-voice` now has `setup-vosk`, `record-once`, `transcribe-file`, `listen-once`, and `voice-command`. The French Vosk model was downloaded outside Git to `~/.local/share/ctos-ai/stt/vosk-model-small-fr-0.22` with `ctos-voice setup-vosk --model-only --yes`; `voice_probe` reports `model_ready=true`. Because system package install required sudo, `ctos-voice setup-vosk --venv --yes` installed PyPI `vosk 0.3.45` in the local venv `~/.local/share/ctos-ai/venvs/vosk`; `voice_probe` now reports `voice_input_ready=true`.
API recovery note 2026-06-23: `ctos-ai-api-server start` restored the local API at `127.0.0.1:8767`. `ctos-ai-api health --json` sees Ollama `0.30.8` and both Qwen2.5-Coder models; `ctos-ai-api ask` returned `CTOS_API_LIVE_OK` through the fast path.
Voice verification note 2026-06-23: generated a 16 kHz mono WAV with `espeak-ng`/`ffmpeg`; `ctos-voice transcribe-file` returned text, and `ctos-voice listen-once --from-wav ... --no-speak` completed the STT-to-CTOS answer loop. `ctos-voice record-once --seconds 1` produced a valid microphone WAV via PipeWire. `ctos-voice voice-command --from-wav ... --no-speak` mapped the recognized phrase `santé` to the read-only `ctos-ai brief` path and, outside the sandbox, reported live `ctos-core` and Kali state.
Identity guard note 2026-06-23: added a deterministic response guard so `ctos-ai ask-local` and the fast API replace GPT/OpenAI/cloud identity hallucinations with the CTOS Local identity fallback. The original prompt `tu fonctionnes?` now returns `Je fonctionne bien.` through both `ctos-ai-api ask` and `ctos-ai ask-local` on `qwen2.5-coder:1.5b`.
Final smoke 2026-06-23: `ctos-ai-api ask "tu fonctionnes?" --model qwen2.5-coder:1.5b` returned `Je fonctionne bien.` with API `ok=true`; `ctos-voice listen-once --from-wav /tmp/ctos-vosk-synth.wav --no-speak` completed the STT-to-model discussion path; `ctos-voice voice-command --from-wav /tmp/ctos-vosk-status.wav --no-speak` mapped transcript `santé` to the read-only `ctos-ai brief` and reached live `ctos-core`.

## Active CTOS Voice Commands V1

- [x] Record the current network stance: `ctos-core` remains Internet-dependent on the T480 bastion link.
- [x] Extend real push-to-talk voice commands with only Tier 0/Tier 1 safe intents.
- [x] Add a small terminal PTT launcher for visible microphone use.
- [x] Add a Hyprland keybind/window rule for the voice launcher.
- [x] Verify typed intent routing and the existing Vosk input readiness.

Voice command update 2026-07-07: `ctos-core` stays behind the T480 bastion for Internet egress. Real voice remains push-to-talk only. Added `scripts/ctos-voice-ptt` and `SUPER+SHIFT+V`, routed `CTOS_VOICE` to workspace `AI`, and expanded safe voice intents to `sante/statut/brief`, `agenda/journee`, `ouvre desk/bureau`, `ouvre vms/machines/kali`, `approbations/validations`, `capacites`, and `aide`. No voice command can directly start/stop VMs, install packages, change firewall rules, or run arbitrary shell.

Verification 2026-07-07: `python3 -m py_compile scripts/ctos-voice scripts/ctos-ai ai/local_api.py`, `bash -n scripts/ctos-voice-ptt`, `ctos-voice probe --json`, typed command tests for `aide`, `agenda`, `capacites`, and `approbations` with a temporary approval DB, live `scripts/ctos-install-desktop`, `hyprctl reload`, `hyprctl configerrors`, and live config comparison all passed. `ctos-voice command --no-speak "ouvre vms"` returns `rc=2` inside the sandbox because `hyprctl dispatch exec` cannot access the real session there; the live Hyprland config contains the installed keybind and window rule.

## Active Desktop Audio Control V1

- [x] Add a repo-owned audio helper for status, volume up/down, mute, set, and mixer.
- [x] Add permanent Waybar volume visibility with scroll/click controls.
- [x] Add Hyprland hardware-key volume binds.
- [x] Improve CTOS voice TTS intelligibility.
- [x] Apply live desktop config and verify audio status against PipeWire.

Audio result 2026-07-07: added `scripts/ctos-audio` using existing PipeWire/WirePlumber `wpctl` and existing `pavucontrol`; no new package was installed. Waybar now shows `VOL n%`; scrolling the module changes volume, left click opens `pavucontrol`, and right click toggles mute. Hyprland binds `XF86AudioRaiseVolume`, `XF86AudioLowerVolume`, `XF86AudioMute`, shifted 10% volume steps, and `SUPER+SHIFT+A` for the mixer. `ctos-voice` now uses slower/louder French `espeak-ng` defaults for clearer spoken feedback. Live volume was raised from `40%` to `70%`.

Verification 2026-07-07: `bash -n scripts/ctos-audio scripts/ctos-voice-ptt scripts/ctos-install-desktop`, `python3 -m py_compile scripts/ctos-voice scripts/ctos-ai ai/local_api.py`, `python3 -m json.tool waybar/config`, `scripts/ctos-audio status`, `scripts/ctos-audio waybar`, live `scripts/ctos-install-desktop`, `hyprctl reload`, Waybar restart, `hyprctl configerrors`, `pgrep -a waybar`, and `command -v ctos-audio ctos-voice-ptt` passed.

Follow-up verification 2026-07-07: after the user reported low/incomprehensible voice feedback, live session audio still worked. `scripts/ctos-audio status` reported `VOL 87%` with session PipeWire access; the sandbox-only failure was `Operation not permitted` against DBus/PipeWire, not a host audio failure. Waybar JSON reported `VOL 87%`, `hyprctl configerrors` was clean, and `waybar` was running.

Update 2026-07-07: added non-multimedia fallback audio binds so volume remains accessible even if hardware/Fn media keys are awkward: `SUPER+PageUp` raises volume by 10%, `SUPER+PageDown` lowers it by 10%, and `SUPER+BackSpace` toggles mute. The existing `SUPER+SHIFT+A` mixer bind and Waybar scroll/click controls remain. CTOS voice defaults were made slower and louder (`espeak-ng` speed `130`, amplitude `200`) to improve intelligibility.

Live verification 2026-07-07: `scripts/ctos-install-desktop` backed up and installed the Hyprland config, `hyprctl reload` returned `ok`, `hyprctl configerrors` was empty, live Hyprland config matches the repo, Waybar is running, `scripts/ctos-audio status` reports `VOL 87%`, and `scripts/ctos-audio waybar` reports the active `VOL 87%` module.

Microphone helper update 2026-07-07: extended `scripts/ctos-audio` with `mic-status`, `mic-up`, `mic-down`, `mic-mute`, and `mic-set`. These use the default PipeWire source through `wpctl`, cap input gain at 100%, and are intended for the open-STT capture cleanup where live T480 recordings reached the backend but produced empty transcripts. No package or service was added.

Microphone helper verification 2026-07-07: `bash -n scripts/ctos-audio`, `scripts/ctos-audio --help`, live `scripts/ctos-audio status`, and live `scripts/ctos-audio mic-status` passed. The live session reported `VOL 87%` and `MIC 30%`.

Microphone diagnostic update 2026-07-07: added `ctos-voice-v2 mic-check`, which records or inspects one WAV and reports duration, RMS level, peak level, clipping percentage, zero percentage, and a concrete gain recommendation. `ctos-voice-v2 stp-transcribe` now includes the same `audio_analysis` payload before/alongside Wyoming recognition, so the next open-STT test can distinguish a backend/model miss from bad capture.

Permanent audio access update 2026-07-07: after the user still had no practical way to adjust T480 sound, extended `scripts/ctos-audio` with `report` and `panel`. `SUPER+A` and Waybar left click now open the live CTOS audio panel; Waybar middle click and `SUPER+SHIFT+A` still open `pavucontrol`. Added microphone binds `SUPER+SHIFT+PageUp/PageDown` and `SUPER+SHIFT+BackSpace`, and the CTRL cockpit now displays `VOL` and `MIC` state. No package, service, or always-on microphone listener was added.

Permanent audio access verification 2026-07-07: `bash -n scripts/ctos-audio scripts/ctos-install-desktop`, `python3 -m py_compile control/status.py control/tui.py scripts/ctos-jarvis scripts/ctos-voice-v2`, and `python3 -m json.tool waybar/config` passed. Live install created Hyprland/Waybar backups, `hyprctl reload` returned `ok`, Waybar restarted as pid `3536154`, `hyprctl configerrors` was empty, live configs match the repo, `ctos-audio report` showed `VOL 87%` and `MIC 20%`, and `ctos-audio waybar` returned active `VOL 87%`.

## Active Desktop Check: ctos-core Wi-Fi And Keyboard RGB

- [x] Re-read relevant desktop/tower context.
- [x] Check local T480 network state and the T480-to-ctos-core link.
- [x] Check `ctos-core` NetworkManager, Wi-Fi devices, rfkill, routes, and recent logs.
- [x] Check keyboard/RGB visibility through USB devices, LED interfaces, and any RGB services.
- [x] Record likely cause and smallest next action.

Diagnostic result 2026-07-07: T480 Wi-Fi is healthy on `wlan0` / `Livebox-8F18`, Ethernet sharing profile `Wired connection 1` is active on `enp0s31f6 = 10.42.0.1/24`, and `ctos-core` is reachable at `10.42.0.2`. `ctos-core` has no current Wi-Fi hardware from the kernel/NetworkManager point of view: `nmcli radio all` reports `WIFI-HW missing`, `nmcli device status` only shows `enp6s0` and `lo`, `rfkill` is empty, and `lsusb` shows only ASUS AURA, Genesys hub, and Logitech G213 keyboard. The saved `Livebox-8F18` profile still exists and has `wpa-psk`, so the issue is not the previous missing `key-mgmt` field. `ctos-core` can ping `10.42.0.1` but not `1.1.1.1`, so the T480-to-tower path is up while Internet egress/NAT through the T480 needs the existing root helper reapplied or inspected with sudo. Keyboard RGB is not CTOS-managed: no OpenRGB/ckb service is installed, and the Logitech G213 exposes only normal HID keyboard LEDs through `/sys/class/leds`; the observed RGB state is probably firmware/device default after reboot.

Egress recovery 2026-07-07: operator reran `sudo scripts/ctos-firewall-fix-tower-egress` on the T480. Follow-up remote checks from `ctos-core` passed: `ping 10.42.0.1`, `ping 1.1.1.1`, and `getent hosts endeavouros.com`. `ctos-core` still reports `WIFI-HW missing`, and `lsusb` still does not show a Wi-Fi adapter, so current Internet access is through the T480 Ethernet-sharing path only.

## Active Voice Quality: Piper TTS Trial

- [x] Confirm current TTS output is limited to `espeak-ng`/`espeak`.
- [x] Add a reversible Piper TTS setup/test path outside the repo.
- [x] Add an explicit TTS engine selector for A/B testing.
- [x] Expose TTS status in the localhost Voice Console.
- [x] Verify syntax, probe output, and print-only install commands.
- [x] Run a live Piper voice test before changing the default voice.

Result 2026-07-10: `ctos-voice` now has `tts-probe`, `setup-piper`, `tts-test`, and `say --engine`. Piper was installed into `~/.local/share/ctos-ai/venvs/piper`; the French `fr_FR-siwis-medium` model/config live under `~/.local/share/ctos-ai/tts/piper/fr_FR-siwis-medium`. Live `tts-test --engine piper` passed. The Voice Console and `ctos-voice-ptt` automatically export `CTOS_VOICE_ENGINE=piper` only when Piper readiness is verified. The running Voice Console reports `tts.default_engine=piper`, and `/api/voice/say` returned `ok=true` with Piper.

## Active CTOS Voice Backend V2 Spike

- [x] Re-read the current CTOS AI/voice V1 context.
- [x] Re-check current open-source voice-stack direction before making a service/package decision.
- [x] Add a repo-owned Voice Backend V2 runbook and backend registry.
- [x] Add a helper command for plan/status/install-command handoff.
- [x] Verify the helper and record the architecture decision.

Working direction 2026-07-07: do not keep expanding the fragile Vosk phrase matcher as the main path. Keep CTOS push-to-talk and permission tiers, but evaluate a mature local voice backend around Home Assistant Assist/Wyoming with Speech-to-Phrase for fixed commands and Piper/Whisper-class components for clearer voice I/O.

Result 2026-07-07: added `ai/voice_backends.json`, `ai/voice_intents_fr.json`, `docs/VOICE_BACKEND_V2.md`, `context/21_ctos_voice_backend_v2.md`, and `scripts/ctos-voice-v2`. The helper exposes `plan`, `status`, `backends`, `intents`, and `next-commands`; it is linked as `/home/operator/.local/bin/ctos-voice-v2`. Verification passed for JSON parsing, Python compile, helper rendering, V1 voice probe, user-bin install, and `ctos-ai capabilities`.

## Active CTOS Voice Intent Adapter V0

- [x] Add deterministic intent matching against `ai/voice_intents_fr.json`.
- [x] Add phrase export output for backend handoff/regression.
- [x] Verify sample phrases and document the next backend adapter step.

Result 2026-07-07: `ctos-voice-v2` now includes `match <text>` and `export-phrases --format plain|jsonl|tsv|yaml`. `ctos-voice-v2 match agenda` resolves to `ctos_agenda -> ctos-ai plan-day`; `ctos-voice-v2 match "ouvre vms"` resolves to `ctos_open_vms -> ctos-ai open-vms`; JSONL phrase export works for backend handoff. The next implementation slice should convert this catalog into a real Speech-to-Phrase/Assist adapter or local regression test harness using recorded samples.

## Active CTOS Voice Intent Runtime Wiring

- [x] Extract the deterministic French intent matcher into a shared repo module.
- [x] Make `ctos-voice-v2` consume the shared matcher instead of duplicating logic.
- [x] Make the real `ctos-voice command`/`voice-command` path consume `ai/voice_intents_fr.json` first.
- [x] Keep the previous hard-coded V1 matcher as a compatibility fallback.
- [x] Verify typed commands for `agenda`, `brief`, `capacites`, and phrase export.

Result 2026-07-07: added `ai/voice_intents.py` and routed both `ctos-voice-v2` and the live `ctos-voice command` path through `ai/voice_intents_fr.json`. The old V1 phrase matcher remains as fallback. Added agenda variants `l agenda`, `a jenda`, and `ajenda` so likely Vosk drift still maps to `ctos-ai plan-day`.

Verification 2026-07-07: `python3 -m py_compile ai/voice_intents.py scripts/ctos-voice-v2 scripts/ctos-voice scripts/ctos-ai`, JSON validation for voice backends/intents, `ctos-voice-v2 match agenda`, `ctos-voice-v2 match "a jenda"`, `ctos-voice-v2 match ajenda`, `ctos-voice command --no-speak agenda`, `ctos-voice command --no-speak "a jenda"`, `ctos-voice command --no-speak ajenda`, `ctos-voice command --no-speak brief`, `ctos-voice command --no-speak capacites`, `ctos-voice command --no-speak approbations`, phrase export, and `ctos-voice-v2 status` all passed. The `brief` check could not reach `ctos-core` from the sandboxed shell, but the command path and local summary completed.

## Active CTOS Voice Regression Harness V0

- [x] Add a `ctos-voice-v2 sample-plan` command for temporary real-voice samples.
- [x] Add a `ctos-voice-v2 regression` command for WAV/transcript -> intent checks.
- [x] Support JSON/JSONL manifests and filename-based WAV directory scans.
- [x] Document the no-Git recording policy and operator workflow.
- [x] Verify with deterministic transcript fixtures and existing voice readiness checks.

Result 2026-07-07: `ctos-voice-v2 sample-plan --dir /tmp/ctos-voice-samples --write-manifest` prints the six safe recording commands and writes a temporary JSONL manifest outside Git. `ctos-voice-v2 regression` can test either WAV files named `intent_id__label.wav` from a directory or JSON/JSONL manifest rows with `file` or `transcript`. Results include transcript source, expected intent, actual intent, matched phrase, score, and pass/fail status.

Verification 2026-07-07: `python3 -m py_compile ai/voice_intents.py scripts/ctos-voice-v2 scripts/ctos-voice scripts/ctos-ai`, JSON validation for voice intents/backends, `ctos-voice-v2 sample-plan --dir /tmp/ctos-voice-samples-test --write-manifest`, `ctos-voice-v2 regression --manifest /tmp/ctos-voice-regression.jsonl`, `ctos-voice-v2 regression --manifest /tmp/ctos-voice-regression.jsonl --json`, `ctos-voice-v2 next-commands`, `ctos-voice-v2 status`, and targeted `git diff --check` passed.

## Active CTOS Voice Backend Export Adapter V0

- [x] Verify current upstream custom-sentence handoff format.
- [x] Export the CTOS intent catalog as Home Assistant/Speech-to-Phrase custom sentences.
- [x] Export a CTOS sidecar intent map so recognition stays separate from action authority.
- [x] Document operator commands and backend boundary.
- [x] Verify generated artifacts without installing daemons.

Result 2026-07-07: `ctos-voice-v2` now exports the CTOS French intent catalog as Home Assistant-compatible custom sentences and writes a complete inert backend handoff bundle with `ctos-voice-v2 export-backend --backend home-assistant --dir /tmp/ctos-voice-backend`. The same bundle shape is usable for the Speech-to-Phrase path because it consumes custom-sentence directories. A generated `ctos_intent_map.json` keeps backend recognition labels separate from CTOS commands, tiers, and approvals.

Verification 2026-07-07: `python3 -m py_compile ai/voice_intents.py scripts/ctos-voice-v2 scripts/ctos-voice scripts/ctos-ai`, JSON validation for voice intents/backends and generated map, `ctos-voice-v2 export-phrases --format ha-sentences`, `ctos-voice-v2 export-phrases --format ha-map`, `ctos-voice-v2 export-backend --backend home-assistant --dir /tmp/ctos-voice-backend-test`, `ctos-voice-v2 export-backend --backend speech-to-phrase --dir /tmp/ctos-voice-backend-stp-test`, `ctos-voice-v2 next-commands`, `ctos-voice-v2 status`, and targeted `git diff --check` passed.

## Active CTOS Voice Backend Bundle Validation V0

- [x] Add a bundle validator for generated custom sentences and CTOS sidecar map.
- [x] Add explicit backend test command handoff without installing/running services.
- [x] Document validation and handoff workflow.
- [x] Verify generated bundles and command output.

Result 2026-07-07: `ctos-voice-v2 validate-backend --dir <bundle>` now checks the exported `custom_sentences/fr/ctos.yaml`, sidecar `ctos_intent_map.json`, intent set, phrase lists, CTOS intent IDs, commands, tiers, and Tier 0/1 safety. `ctos-voice-v2 backend-commands --backend speech-to-phrase|home-assistant --dir <bundle>` prints the next non-mutating handoff commands without installing packages, starting daemons, or exposing ports.

Verification 2026-07-07: `python3 -m py_compile ai/voice_intents.py scripts/ctos-voice-v2 scripts/ctos-voice scripts/ctos-ai`, `ctos-voice-v2 export-backend --backend home-assistant --dir /tmp/ctos-voice-backend-vtest`, `ctos-voice-v2 validate-backend --dir /tmp/ctos-voice-backend-test`, `ctos-voice-v2 validate-backend --dir /tmp/ctos-voice-backend-test --json`, `ctos-voice-v2 validate-backend --dir /tmp/ctos-voice-backend-vtest`, `ctos-voice-v2 backend-commands --backend speech-to-phrase --dir /tmp/ctos-voice-backend-test`, `ctos-voice-v2 backend-commands --backend home-assistant --dir /tmp/ctos-voice-backend-vtest`, `ctos-voice-v2 next-commands`, generated map JSON validation, and targeted `git diff --check` passed.

## Active CTOS Voice Speech-to-Phrase Preflight V0

- [x] Add a backend preflight that separates bundle readiness, local tool readiness, and actual Speech-to-Phrase runtime readiness.
- [x] Render explicit non-mutating install/test commands for Speech-to-Phrase without creating a service.
- [x] Document that a full recognition test requires a temporary Home Assistant/Wyoming context and a token file, not an inline shell secret.
- [x] Verify helper output, backend validation, and docs.

Working constraint 2026-07-07: Speech-to-Phrase is the right mature fixed-phrase direction, but upstream is not a simple offline WAV-to-intent binary. CTOS should prepare the bundle and preflight first, then choose a temporary Home Assistant test context before any persistent daemon.

Result 2026-07-07: `ctos-voice-v2 backend-preflight --backend speech-to-phrase --dir <bundle>` now reports bundle validity, local helper tools, Python module import readiness, Home Assistant websocket/token-file readiness, and optional `ctos-core` probe output. The generated CTOS custom-sentence bundle validates cleanly; current blocker is expected and explicit: `speech_to_phrase` is not installed/importable and no temporary Home Assistant context/token file has been chosen yet.

Verification 2026-07-07: `python3 -m py_compile ai/voice_intents.py scripts/ctos-voice-v2 scripts/ctos-voice scripts/ctos-ai`, `ctos-voice-v2 export-backend --backend speech-to-phrase --dir /tmp/ctos-voice-backend-preflight-test`, `ctos-voice-v2 validate-backend --dir /tmp/ctos-voice-backend-preflight-test`, `ctos-voice-v2 backend-preflight --backend speech-to-phrase --dir /tmp/ctos-voice-backend-preflight-test`, `ctos-voice-v2 backend-preflight --backend speech-to-phrase --dir /tmp/ctos-voice-backend-preflight-test --json`, `ctos-voice-v2 backend-commands --backend speech-to-phrase --dir /tmp/ctos-voice-backend-preflight-test`, `ctos-voice-v2 next-commands`, and targeted `git diff --check` passed.

## Active CTOS Speech-to-Phrase Smoke Test V0

- [x] Reconfirm local CTOS bundle/preflight state.
- [x] Re-check current Speech-to-Phrase package/runtime direction.
- [x] Document the transient venv smoke-test decision.
- [x] Run a `/tmp` venv import/help smoke test with no daemon.
- [x] Record results and next blocker.

Working constraint 2026-07-07: the smoke test may install Python packages into a disposable `/tmp` venv only. No package-manager install, no user-local persistent venv, no systemd service, no open port, and no Home Assistant token in shell history.

Result 2026-07-07: PyPI lookup/install for `speech-to-phrase` and `speech_to_phrase` found no installable distribution in the current environment, but installing the official GitHub repo into `/tmp/ctos-speech-to-phrase-smoke-venv` succeeded at commit `b4ecef9519e84fefd5dc35c0384c50efa13a0bad`. Runtime imports passed: `speech_to_phrase 1.4.3`, `wyoming 1.5.4`. The observed invocation is `python -m speech_to_phrase --help`; there is no dedicated console script. `ctos-voice-v2 backend-preflight --runtime-python /tmp/ctos-speech-to-phrase-smoke-venv/bin/python` now reports `backend_runtime_ready True` while correctly keeping `full_recognition_ready False` until a Home Assistant websocket/token-file context exists.

Verification 2026-07-07: `/tmp/ctos-speech-to-phrase-smoke-venv/bin/python -m speech_to_phrase --help`, `/tmp/ctos-speech-to-phrase-smoke-venv/bin/python -m speech_to_phrase --version`, Python import/version check, module/package inspection, `python3 -m py_compile ai/voice_intents.py scripts/ctos-voice-v2 scripts/ctos-voice scripts/ctos-ai`, `ctos-voice-v2 backend-preflight --backend speech-to-phrase --dir /tmp/ctos-voice-backend-preflight-test --runtime-python /tmp/ctos-speech-to-phrase-smoke-venv/bin/python`, JSON preflight output, and backend command rendering passed. Future generated install commands now include `PIP_NO_CACHE_DIR=1`; the first escalated install did leave a pip wheel cache entry, which was documented instead of silently deleting user cache.

## Active CTOS Speech-to-Phrase Backend Tiers V0

- [x] Inspect the installed Speech-to-Phrase source for a no-Home-Assistant training path.
- [x] Confirm CTOS generated custom sentences parse through upstream `hassil`.
- [x] Add preflight reporting for offline training readiness.
- [x] Keep the heavy model/tools training command rendered but commented until cache/storage is decided.
- [x] Document the remaining blockers.

Result 2026-07-07: `speech_to_phrase.train` exists and can train directly from the CTOS generated YAML, so Home Assistant is not required for the next offline-training tier. The generated CTOS YAML parses with `hassil` and contains the six expected intent labels. The current missing pieces are explicit and expected: a `fr_FR-rhasspy` model cache and speech-tool cache with Kaldi/OpenFST/OpenGRM/Phonetisaurus, plus a later Home Assistant websocket/token-file context for a full live recognizer.

Verification 2026-07-07: `python3 -m py_compile ai/voice_intents.py scripts/ctos-voice-v2 scripts/ctos-voice scripts/ctos-ai`, `ctos-voice-v2 export-backend --backend speech-to-phrase --dir /tmp/ctos-voice-backend-preflight-test`, `ctos-voice-v2 backend-commands --backend speech-to-phrase --dir /tmp/ctos-voice-backend-preflight-test`, `ctos-voice-v2 backend-preflight --backend speech-to-phrase --dir /tmp/ctos-voice-backend-preflight-test --runtime-python /tmp/ctos-speech-to-phrase-smoke-venv/bin/python`, JSON preflight output, and targeted `git diff --check` passed.

## Active CTOS Speech-to-Phrase Cache Placement V0

- [x] Add a read-only cache inspection command.
- [x] Check the expected local model/tool cache paths.
- [x] Probe `ctos-core` cache paths over SSH.
- [x] Record the `ctos-core` `/srv/ctos` placement decision.
- [x] Document the next controlled bootstrap step.

Result 2026-07-07: added `ctos-voice-v2 stp-cache`. It reports the selected `fr_FR-rhasspy` model, model download URL, recommended owner, `/srv/ctos` cache directories, missing model/tool artifacts, JSON output, and optional `ctos-core` SSH probe. The preferred cache owner is `ctos-core`, not the T480 host. The live `ctos-core` probe succeeded and confirmed the model/tool cache is not present yet.

Verification 2026-07-07: `python3 -m py_compile scripts/ctos-voice-v2`, `ctos-voice-v2 stp-cache --runtime-python /tmp/ctos-speech-to-phrase-smoke-venv/bin/python`, `ctos-voice-v2 stp-cache --runtime-python /tmp/ctos-speech-to-phrase-smoke-venv/bin/python --json`, and `ctos-voice-v2 stp-cache --runtime-python /tmp/ctos-speech-to-phrase-smoke-venv/bin/python --target-probe` passed as expected. The cache command exits non-zero while cache artifacts are missing; that is the intended automation signal.

## Active CTOS Speech-to-Phrase Container Path V0

- [x] Add an official container-first plan command.
- [x] Verify `ctos-core` has a container runtime candidate.
- [x] Regenerate and validate the CTOS Speech-to-Phrase backend bundle.
- [x] Copy the validated bundle to `ctos-core` under `/srv/ctos`.
- [x] Verify local/remote bundle checksums.
- [x] Document the container-first decision.
- [x] Pull/inspect `docker.io/rhasspy/wyoming-speech-to-phrase --help` on `ctos-core`.
- [x] Create the first writable Speech-to-Phrase cache directories on `ctos-core`.
- [x] Choose a temporary Home Assistant/Wyoming test context and token-file path.
- [ ] Run one localhost-only manual recognition loop.

Result 2026-07-07: added `ctos-voice-v2 stp-container-plan` and `ctos-voice-v2 stp-container-inspect`, updated `ai/voice_backends.json`, and copied the validated Speech-to-Phrase custom-sentence bundle to `ctos-core:/srv/ctos/voice/backend/speech-to-phrase`. `ctos-core` has `/usr/bin/podman`. The fully qualified image `docker.io/rhasspy/wyoming-speech-to-phrase` was pulled and inspected; help output passed and the image digest is `sha256:9ef75f4a4f21484ebbe7e0c0f81a53bb7670e6b57430c7d8fa632239ba318289`. Image inspection showed `ENTRYPOINT=["bash","/run.sh"]`, and `/run.sh` uses image-internal `/usr/src/tools`; CTOS must not mount or override `/tools` for the first live test. The generated live command now mounts the Home Assistant token file read-only at `/run/secrets/ctos-ha-token` instead of passing the token as a host shell argument. Verification after this hardening: `ctos-voice-v2 stp-container-plan --target-probe` still reaches `ctos-core`, finds `/usr/bin/podman`, and confirms `backend_dir`, `custom_sentences`, `train_dir`, and `models_dir`.

Verification 2026-07-07: `python3 -m py_compile scripts/ctos-voice-v2`, `python3 -m json.tool ai/voice_backends.json`, `ctos-voice-v2 stp-container-plan`, `ctos-voice-v2 stp-container-plan --json`, `ctos-voice-v2 stp-container-plan --target-probe`, `ctos-voice-v2 export-backend --backend speech-to-phrase --dir /tmp/ctos-voice-backend`, `ctos-voice-v2 validate-backend --dir /tmp/ctos-voice-backend`, tar-over-SSH bundle copy, matching local/remote `sha256sum` checks, `ctos-voice-v2 stp-container-inspect`, remote image entrypoint inspection, and remote cache directory creation passed. The container image was pulled and run only with `--help`; no persistent service was created.

## Active CTOS Temporary Home Assistant Context V0

- [x] Document the smallest temporary Home Assistant/Wyoming context.
- [x] Add a helper that prints the temporary Home Assistant container/tunnel/token plan.
- [x] Prepare/probe the `ctos-core` config directory without starting a persistent service.
- [x] Verify local script syntax, JSON output, and non-persistent target checks.
- [x] Add controlled temporary lifecycle commands.
- [x] Start the temporary Home Assistant context on `ctos-core`.
- [ ] Complete local onboarding through the T480 SSH tunnel.
- [ ] Create the temporary Home Assistant token file outside Git/history.
- [ ] Run one localhost-only Speech-to-Phrase recognition loop.

Working constraint 2026-07-07: use Home Assistant only as a temporary local websocket/token context for the first Speech-to-Phrase loop. Do not create a permanent daemon, expose the API on LAN, mount privileged host devices, or store the token in Git/history.

Result 2026-07-07: added `ctos-voice-v2 hass-context-plan`. It renders the temporary `ghcr.io/home-assistant/home-assistant:stable` container plan on `ctos-core`, config under `/srv/ctos/voice/home-assistant-test/config`, localhost bind `127.0.0.1:8123`, SSH tunnel from the T480, token-file handling at `/run/user/$UID/ctos-ha-token`, and the follow-up Speech-to-Phrase plan command.

Verification 2026-07-07: `python3 -m py_compile ai/voice_intents.py scripts/ctos-voice-v2 scripts/ctos-voice scripts/ctos-ai`, `python3 -m json.tool ai/voice_backends.json`, `python3 -m json.tool ai/voice_intents_fr.json`, `ctos-voice-v2 hass-context-plan`, `ctos-voice-v2 hass-context-plan --json`, `ctos-voice-v2 next-commands`, targeted `git diff --check`, and `ctos-voice-v2 hass-context-plan --target-prepare --target-probe` passed. The `ctos-core` probe found `/usr/bin/podman`, free port `8123`, prepared `/srv/ctos/voice/home-assistant-test/config` as `ctos:ctos drwxrwsr-x`, and reported the Home Assistant image as not yet pulled.

Update 2026-07-07: added `ctos-voice-v2 hass-context status|start|logs|stop`. `ctos-voice-v2 hass-context start` pulled `ghcr.io/home-assistant/home-assistant:stable` and started `ctos-ha-test` on `ctos-core` with `--rm`, config `/srv/ctos/voice/home-assistant-test/config`, and localhost-only bind `127.0.0.1:8123:8123`. `ctos-voice-v2 hass-context status --json` verified image present, container running, port busy, and HTTP `302`. Image id is `ceb81d836a0b125a4ec14a754231a5dd1cc5f2feb2594107320c3cea345dd9d1`; digest is `sha256:21e0d1bae299819d8cf4ef8aa197593205a5fae51c69031c13bfd1eac8c56204`. `ctos-voice-v2 hass-context logs --logs-tail 20` shows a rootless DHCP watcher permission warning, not blocking for this websocket/token-only test.

Update 2026-07-07: added `ctos-voice-v2 hass-context token-status|readiness|tunnel-command|token-command`. `readiness` combines remote Home Assistant status with safe token/API checks and prints the Speech-to-Phrase plan command only once the token file reports ready. `token-status` and `readiness` now exit non-zero until the token is valid, making them usable as gates rather than only diagnostics. Live check: `ctos-ha-test` is running, image is present, localhost port `8123` is busy, HTTP is `302`, and `/run/user/1000/ctos-ha-token` is currently missing. No token content is printed. Verification: `python3 -m py_compile scripts/ctos-voice-v2`, `ctos-voice-v2 hass-context token-command`, `ctos-voice-v2 next-commands`, and expected-fail live SSH checks for `ctos-voice-v2 hass-context readiness` and `ctos-voice-v2 hass-context token-status` passed.

Update 2026-07-07: added `ctos-voice-v2 stp-container status|start|stop|logs` as the temporary Speech-to-Phrase runtime manager. `status` reads remote runtime/image/path/container/port state. `start` checks the Home Assistant token/API gate first and refuses before launching if `hass-context readiness` is not green. Live verification: `ctos-voice-v2 stp-container status` found image and paths ready, container missing, port `10300` free, and token missing; `ctos-voice-v2 stp-container start` expected-failed with `state=missing_token` and `blocked_before_container_start`; a follow-up status confirmed the container was still missing and port `10300` still free. `ctos-voice-v2 stp-container logs` and `stop` also handle the absent-container state cleanly with `missing`.

Update 2026-07-07: verified the temporary Home Assistant context is still running on `ctos-core`: `ctos-ha-test` is running, image present, localhost port `8123` busy, and HTTP returns `302`. `hass-context readiness` still fails correctly because `/run/user/1000/ctos-ha-token` is missing. Added `ctos-voice-v2 hass-context token-save` so the operator can paste the long-lived Home Assistant token through a hidden T480 prompt; the helper sends it over SSH stdin, strips newlines, writes the token file on `ctos-core`, and sets mode `600` without printing the token or putting it in shell history. Verification: `python3 -m py_compile scripts/ctos-voice-v2`, `ctos-voice-v2 next-commands`, `ctos-voice-v2 hass-context --help`, and empty-token refusal with `ctos-voice-v2 hass-context token-save --token-stdin` passed.

Follow-up 2026-07-07: local tunnel `127.0.0.1:8123 -> ctos-core:127.0.0.1:8123` is already running (`ssh -fN ...`) and local `curl http://127.0.0.1:8123/` returns `302`. `xdg-open http://127.0.0.1:8123/` failed because no classic browser executable was available on the T480; this is now tracked as open question 33.

Update 2026-07-07: added `ctos-voice-v2 hass-context onboard-api` as the browserless first-onboarding/token helper for the temporary Home Assistant instance. The server-side schemas were verified directly inside the running `ctos-ha-test` container before implementation. The helper prompts for the Home Assistant display name, username, and password; posts to the local tunneled onboarding API; exchanges the returned auth code; creates a long-lived token through the local Home Assistant websocket; and stores only that token through the existing `/run/user/$UID/ctos-ha-token` path on `ctos-core`. It does not print password, auth code, access token, refresh token, or long-lived token. The helper has not been run yet because it requires the operator's temporary Home Assistant password input.

Verification 2026-07-07: `python3 -m py_compile scripts/ctos-voice-v2 scripts/ctos-voice scripts/ctos-ai`, `ctos-voice-v2 hass-context --help`, `ctos-voice-v2 next-commands`, and targeted `git diff --check` passed. A mismatch test with `ctos-voice-v2 hass-context onboard-api --ha-name Test --ha-username test --json` refused before onboarding with `password confirmation mismatch; onboarding not attempted`.

Final check 2026-07-07: reran `python3 -m py_compile scripts/ctos-voice-v2 scripts/ctos-voice scripts/ctos-ai`, targeted `git diff --check`, and `ctos-voice-v2 next-commands`; all passed. The next live step is the real `hass-context onboard-api` run because it requires the operator to enter a temporary Home Assistant password through a hidden prompt.

Update 2026-07-07: added `scripts/ctos-voice-setup` and linked it into the user-bin manifest. It is a guided interactive setup wrapper for the temporary live voice stack: local/core status, Home Assistant status/start, readiness, browserless onboarding if the token is missing, readiness recheck, Speech-to-Phrase start, and open-STT path probe. It supports `--plan` for non-mutating audit output and `--help` without touching SSH or containers.

Verification 2026-07-07: `bash -n scripts/ctos-voice-setup scripts/ctos-install-user-bin scripts/ctos-voice-v2 scripts/ctos-voice`, `python3 -m py_compile scripts/ctos-voice-v2 scripts/ctos-voice scripts/ctos-ai`, `ctos-voice-setup --help`, `ctos-voice-setup --plan` from both the repo and `~/.local/bin`, `ctos-voice-v2 next-commands`, and targeted `git diff --check` passed. The live gate remains intentionally blocked at `state=missing_token`: `ctos-ha-test` is running on `ctos-core`, Speech-to-Phrase image/paths are present, the `ctos-speech-to-phrase` container is absent, and port `10300` is free.

Live handoff 2026-07-07: launched `kitty --class CTOS_VOICE --title CTOS_VOICE ctos-voice-setup` through Hyprland. `hyprctl clients` confirms a mapped `CTOS_VOICE` window on workspace `5 (AI)`, ready for the operator to enter the temporary Home Assistant onboarding password locally.

Update 2026-07-07: added `ctos-voice-v2 doctor` and wired it into `ctos-voice-setup --plan`. The doctor is a read-only live stack summary: local voice catalog/tools, `ctos-core` SSH, temporary Home Assistant container, token gate, Speech-to-Phrase container, and open-STT directory readiness. Live check reported `state=missing_token`: SSH is OK, `ctos-ha-test` is running, Speech-to-Phrase image and paths are present, open-STT dirs are ready, and the next concrete action is `ctos-voice-v2 hass-context onboard-api`.

## Active CTOS Jarvis Voice Stack Pivot V0

- [x] Reassess the "missed agenda" symptom as an architecture issue, not only a phrase-list issue.
- [x] Compare the current CTOS direction with mature local open-source voice stacks.
- [x] Record the hybrid-stack decision in the decision log.
- [x] Add a non-destructive open-ended STT plan/preflight command.
- [ ] Complete the temporary Home Assistant onboarding/token blocker.
- [ ] Run one localhost-only Speech-to-Phrase loop for deterministic commands.
- [x] Add a local open-ended STT plan/preflight for natural requests.
- [x] Route typed and spoken requests into the same CTOS intent/action planner.
- [x] Add the first permissioned natural-language agenda proposal/commit loop.
- [x] Add a push-to-talk natural transcript route that proposes agenda actions without mutation.
- [x] Add a saved pending-proposal loop so voice can stage agenda changes before confirmation.
- [x] Add a read-only voice review command for pending agenda proposals.
- [x] Add a Speech-to-Phrase/Wyoming one-shot test command with temporary SSH tunneling.
- [x] Add a local Wyoming mock self-test for transport and CTOS route verification.
- [x] Add an idempotent T480-to-Home-Assistant tunnel helper before onboarding.
- [x] Add a bounded assistant fallback for typed/push-to-talk transcripts while HA onboarding remains token-gated.
- [x] Add a single `ctos-jarvis` operator facade over the safe voice/agenda/backend commands.
- [x] Add a quick non-destructive `ctos-jarvis smoke` readiness check.
- [x] Add an operator-safe `ctos-jarvis unlock-voice` gate for the mature HA/Speech-to-Phrase rail.
- [x] Select `wyoming-faster-whisper` as the first open-ended STT smoke candidate.
- [x] Add `ctos-voice-v2 open-stt-candidates` as the auditable candidate/smoke-plan surface.
- [x] Run the containerized Wyoming Whisper help/runtime probe on `ctos-core`.
- [x] Add `ctos-voice-v2 open-stt status|start|logs|stop` for reproducible temporary smoke tests.
- [x] Add `ctos-jarvis calibrate` as the readable live open-STT/audio/route report.
- [x] Harden transcript guarding against unreadable and symbol-noise STT output.
- [x] Add a guided reusable voice-corpus collection command instead of one-word tuning.
- [x] Add read-only audio preflight before guided corpus collection.
- [x] Add a read-only corpus readiness gate before sample regression.
- [x] Add a read-only Jarvis corpus triage verdict.
- [x] Add a one-command corpus evaluation gate before local/open-STT regression.
- [x] Add `ctos-jarvis improve` as the safe corpus improvement loop.
- [x] Add `ctos-jarvis collect-next` for one-phrase corpus capture.
- [x] Add a compact `ctos-jarvis status` command for current state and next action.
- [x] Reconfirm the mature open-source/local stack path after the `agenda` miss.
- [ ] Fix the T480 microphone capture/gain path for open-STT.
- [ ] Run one localhost-only open-STT push-to-talk transcript through CTOS routing.

Result 2026-07-07: accepted ADR-0056. CTOS should not build a whole voice platform from scratch and should not keep tuning exact Vosk/Speech-to-Phrase phrases as the only path. The working target is a hybrid local stack: Home Assistant Assist/Wyoming as the voice bus, Speech-to-Phrase as the deterministic command rail, a Whisper-compatible local STT rail for natural language, local TTS, and CTOS as the action/approval boundary. OpenVoiceOS and Open Interpreter/01 remain research inspirations or sandbox candidates only, not the authority layer. AirLLM/GLM-family work is deferred to the model-runtime layer.

Update 2026-07-07: added `ctos-voice-v2 open-stt-plan`. It renders the future open-ended STT rail without installing packages, downloading models, starting services, or enabling an always-on microphone. The default placement is `ctos-core` under `/srv/ctos/models/open-stt`, `/srv/ctos/cache/open-stt`, and `/srv/ctos/voice/backend/open-stt`, with future localhost-only Wyoming port `10301`. The command can probe `ctos-core` paths with `--target-probe` and can create only those planned directories with `--target-prepare`. It records that open STT returns transcript text only; CTOS still owns intent/action approval.

Verification 2026-07-07: `ctos-voice-v2 open-stt-plan` and `ctos-voice-v2 open-stt-plan --json` passed locally. `ctos-voice-v2 open-stt-plan --target-probe` initially reported the three planned `ctos-core` paths missing. `ctos-voice-v2 open-stt-plan --target-prepare --target-probe` then created and verified `/srv/ctos/models/open-stt`, `/srv/ctos/cache/open-stt`, and `/srv/ctos/voice/backend/open-stt`.

Open-STT runtime result 2026-07-07: direct upstream `wyoming-faster-whisper` venv setup on `ctos-core` failed during the `pysilero-vad` build under Python 3.14, so the first runnable path moved to the official `docker.io/rhasspy/wyoming-whisper` container. Container `--help` passed, a temporary localhost-only `ctos-open-stt-smoke` container started on port `10301`, and a synthetic French WAV reached CTOS through the Wyoming client/route path. Transcript quality was not yet acceptable and live T480 microphone recordings returned empty transcripts despite reaching the backend, so the next blocker is audio capture/gain cleanup before persistent service work or model tuning.

Cleanup 2026-07-07: confirmed `ctos-open-stt-smoke` was still running on `ctos-core` after the temporary test window and stopped it. No open-STT daemon or persistent service is running.

Live open-STT follow-up 2026-07-07: microphone gain was reduced after clipping diagnostics and the live capture now reports usable levels (`state=ok`, no clipping). A temporary `docker.io/rhasspy/wyoming-whisper` container was retested with `base-int8`, then `small-int8`. The backend processed audio and the CTOS Wyoming route worked, but raw live capture still returned empty transcripts; software-normalized capture produced a known Whisper silence/noise hallucination (`Sous-titres réalisés...`). The conclusion is to keep the mature open-STT pivot and avoid spending time on phrase-by-phrase command tuning. `ctos-voice-v2 stp-transcribe` now blocks empty transcripts, bad audio states, and known hallucinations before CTOS routing, with `--no-transcript-guard` as a debug-only bypass. It also has `--preprocess auto`, an energy-based voice activity/trim/normalization step that refuses low-activity samples before contacting Whisper. Verification with a generated silence WAV confirmed that silence is blocked before STT, while an older short active sample is prepared into a normalized STT WAV but still returns no transcript. The temporary container was stopped after the test.

Planner result 2026-07-07: added `ai/action_planner.py` and `ctos-ai route-text`. Typed text and the live `ctos-voice command` catalog path now use the same CTOS action planner. The planner executes nothing by default; `--execute-safe` is limited to Tier 0/Tier 1 commands owned by `ctos-ai`. Unmatched natural-language requests are classified as transcript text for the future open-ended Jarvis parser instead of being guessed into shell or VM actions.

Planner verification 2026-07-07: `python3 -m py_compile ai/action_planner.py ai/voice_intents.py scripts/ctos-ai scripts/ctos-voice scripts/ctos-voice-v2`, `python3 -m json.tool ai/voice_intents_fr.json`, `ctos-ai route-text agenda --json`, `ctos-ai route-text --source voice --execute-safe agenda`, `ctos-ai route-text "ajoute un rendez-vous demain" --json`, `ctos-ai route-text --execute-safe "ajoute un rendez-vous demain" --json` expected-refusal with rc `2`, `ctos-voice command --no-speak agenda`, `ctos-ai capabilities --json`, and targeted `git diff --check` passed.

Agenda parser result 2026-07-07: added `ai/agenda_parser.py` and `ctos-ai agenda-propose`. Natural French agenda requests now produce a reviewed proposal with title, due date, priority, estimate, and the exact `ctos-agenda add ...` command. The command writes nothing by default and refuses `--commit` unless `--yes` is also present. `ctos-ai route-text` now attaches an `agenda_proposal` for agenda-like unmatched text, including scheduled add requests that do not explicitly say "agenda".

Agenda parser verification 2026-07-07: `python3 -m py_compile ai/agenda_parser.py ai/action_planner.py ai/voice_intents.py scripts/ctos-ai scripts/ctos-voice scripts/ctos-voice-v2 scripts/ctos-agenda`, `python3 -m json.tool ai/voice_intents_fr.json`, `ctos-ai route-text "ajoute acheter du lait demain 30 min priorité 4" --json`, `ctos-ai agenda-propose "ajoute acheter du lait demain 30 min priorité 4" --json`, `CTOS_AI_DB=/tmp/ctos-agenda-propose-final.sqlite3 ctos-ai agenda-propose "ajoute acheter du lait demain 30 min priorité 4" --commit --yes --json`, temp DB list verification, expected refusal for `--commit` without `--yes`, `ctos-ai capabilities --json`, and targeted `git diff --check` passed.

Voice route result 2026-07-07: added `ctos-voice route` for typed transcript debugging and `ctos-voice route-once` for one push-to-talk Vosk transcript. This is the first microphone-facing natural-language Jarvis path: it can show an agenda proposal from speech text, but it still refuses mutable agenda writes unless the operator uses the separate reviewed `ctos-ai agenda-propose ... --commit --yes` flow.

Voice route verification 2026-07-07: `python3 -m py_compile scripts/ctos-voice ai/action_planner.py ai/agenda_parser.py scripts/ctos-ai`, `ctos-voice route "ajoute acheter du lait demain 30 min priorité 4" --no-speak`, `ctos-voice route "ajoute acheter du lait demain 30 min priorité 4" --execute-safe --no-speak --json` expected-refusal with rc `2`, and `ctos-voice route agenda --execute-safe --no-speak` passed.

Saved agenda proposal result 2026-07-07: `ctos-ai agenda-propose ... --save --source voice` now stores a pending local proposal in the CTOS approval DB, separate from the real agenda DB. `ctos-ai agenda-proposals`, `ctos-ai agenda-show latest`, `ctos-ai agenda-confirm latest --yes`, and `ctos-ai agenda-reject latest` provide the review surface. `ctos-voice route ... --save-agenda` and `ctos-voice route-once ... --save-agenda` can stage recognized agenda requests from typed or push-to-talk transcripts, while `--save-agenda --execute-safe` is refused as an ambiguous mixed mode.

Saved agenda proposal verification 2026-07-07: temporary `/tmp` DBs verified save/list/refuse-without-`--yes`/confirm/write/reject paths. `python3 -m py_compile scripts/ctos-ai scripts/ctos-voice ai/action_planner.py ai/agenda_parser.py scripts/ctos-agenda`, `ctos-voice route "ajoute acheter du pain demain" --save-agenda --no-speak`, `ctos-voice route "ajoute acheter du pain demain" --save-agenda --execute-safe --no-speak` expected-refusal with rc `2`, and targeted `git diff --check` passed.

Agenda review voice result 2026-07-07: added `ctos-ai agenda-review` and the safe voice intent `ctos_agenda_review` for phrases such as `propositions agenda`, `validation agenda`, and `agenda en attente`. This path lists pending agenda proposals and prints exact typed `agenda-confirm` / `agenda-reject` commands. It is read-only and does not approve anything by voice.

Agenda review voice verification 2026-07-07: `ctos-voice-v2 match "propositions agenda"` matched `ctos_agenda_review` over the generic agenda intent. With temporary `/tmp` DBs, `ctos-ai agenda-review`, `ctos-ai agenda-review --json`, and `ctos-voice command --no-speak "propositions agenda"` displayed the pending proposal without committing it. Final `py_compile`, JSON validation, and targeted `git diff --check` passed.

Read-only review fix 2026-07-07: `ctos-ai agenda-review --json` now uses a read-only SQLite connection for proposal listing and returns an empty list when the approval DB or `agenda_proposals` table is absent. This avoids trying to initialize/write the DB from read-only contexts. Verified real read-only review, temporary save/confirm, `py_compile`, JSON validation, and targeted `git diff --check`.

Speech-to-Phrase test bridge 2026-07-07: added `ctos-voice-v2 stp-transcribe`. It records or accepts a mono WAV, optionally opens a temporary SSH tunnel from the T480 to `ctos-core:127.0.0.1:10300`, sends the audio to the Wyoming/Speech-to-Phrase endpoint, and routes any transcript back through the CTOS planner. `--route` is plan-only; `--execute-safe` stays limited to CTOS-owned Tier 0/1 actions. Verification passed for syntax/help/next-command wiring and a controlled no-service socket failure. Live `ctos-voice-v2 doctor` still reports `missing_token`: Home Assistant is running, STP image and paths are ready, but the HA token must be created before `stp-container start` and the real recognition loop can run.

Wyoming self-test result 2026-07-07: added `ctos-voice-v2 wyoming-selftest`. It starts a localhost-only mock Wyoming server, sends a temporary WAV through the same event client used by `stp-transcribe`, returns a fixed transcript such as `agenda`, and routes the text through CTOS. This is deliberately not a speech-recognition quality test; it isolates protocol plumbing and CTOS routing while Home Assistant token onboarding remains blocked.

Wyoming self-test verification 2026-07-07: `ctos-voice-v2 wyoming-selftest --no-speak --json` passed outside the sandbox with mock events `describe`, `transcribe`, `audio-start`, `audio-chunk`, `audio-stop`; the returned transcript `agenda` routed to `ctos_agenda -> ctos-ai plan-day`.

Home Assistant tunnel hardening 2026-07-07: added `ctos-voice-v2 hass-context tunnel-status|tunnel-start|onboarding-status` and wired `ctos-voice-setup` to run `tunnel-start` before `onboard-api`. This removes a fragile manual step after reboot/sleep: browserless onboarding now first ensures `127.0.0.1:8123/api/onboarding` on the T480 reaches the temporary Home Assistant context on `ctos-core`; `onboarding-status` exposes the first-run step booleans without creating users or tokens.

Home Assistant tunnel verification 2026-07-07: `ctos-voice-v2 hass-context onboarding-status --json` reached the tunneled local API and reported `user=false core_config=false analytics=false integration=false`. `ctos-voice-v2 doctor --json` and the human doctor output now include the same onboarding state and still correctly report `state=missing_token`, with `next_action=ctos-voice-v2 hass-context onboard-api`. Static verification passed for `py_compile`, `bash -n`, CLI help, `ctos-voice-setup --plan`, `ctos-voice-v2 next-commands`, and targeted `git diff --check`.

Bounded assistant result 2026-07-07: added `ctos-voice assistant` for typed transcript tests and `ctos-voice assistant-once` for one push-to-talk recording. The mode first tries the CTOS safe action planner, can stage an agenda proposal with `--save-agenda`, and otherwise asks the local Ollama model through a restricted CTOS prompt. The model fallback is conversational only and cannot execute shell, VM, package, firewall, or approval actions.

Bounded assistant verification 2026-07-07: `ctos-voice assistant agenda --no-speak --json` executed the safe day-plan path, temporary `/tmp` DBs verified `ctos-voice assistant "ajoute acheter du pain demain 30 min priorité 4" --save-agenda --no-speak --json`, and the repaired Ollama tunnel answered `ctos-voice assistant "explique en une phrase ce que tu peux faire" --no-speak --json`. Static verification passed for `py_compile`, `ctos-voice --help`, `ctos-voice-v2 next-commands`, `ctos-ai capabilities`, and targeted `git diff --check`.

Operator facade result 2026-07-07: added `scripts/ctos-jarvis` as the daily entrypoint for the current Jarvis bridge. It wraps `brief`, `doctor`, `next`, typed `text`, push-to-talk `voice`, read-only agenda `review`, typed `confirm/reject`, and `setup-voice`. The facade does not add new authority; it only calls existing CTOS commands that preserve the same safe-action, agenda-proposal, and Home Assistant token gates.

Operator facade verification 2026-07-07: `python3 -m py_compile scripts/ctos-jarvis`, `bash -n scripts/ctos-install-user-bin`, `ctos-jarvis --help`, `ctos-jarvis next`, `ctos-jarvis text agenda --json`, and temporary `/tmp` DB agenda proposal tests passed. `scripts/ctos-install-user-bin --dry-run` now includes `ctos-jarvis`, and targeted `git diff --check` passed.

Jarvis smoke result 2026-07-07: added `ctos-jarvis smoke` as a quick readiness check for the usable bridge. Default mode is local and non-destructive: it runs the voice backend doctor in local-only mode, probes the voice setup, tests the safe `agenda` route, stages a natural agenda proposal in temporary `/tmp` DBs, and reviews that proposal. `--full` includes `ctos-core` backend checks; `--with-model` includes the local Ollama fallback.

Jarvis smoke verification 2026-07-07: `python3 -m py_compile scripts/ctos-jarvis`, `ctos-jarvis --help`, `ctos-jarvis next`, `ctos-jarvis smoke`, `ctos-jarvis smoke --json`, `ctos-jarvis smoke --with-model --json`, and targeted `git diff --check` passed.

Jarvis mature voice gate result 2026-07-07: added `ctos-jarvis unlock-voice`. Default mode is safe and non-secret: it ensures the local Home Assistant tunnel, runs the live voice doctor, reports the exact state/blockers, and points to `ctos-jarvis unlock-voice --interactive` when the Home Assistant onboarding/token gate is still missing. `--interactive` delegates to `ctos-voice-setup`; `--start` starts Speech-to-Phrase only after the token gate is ready; `--test` starts Speech-to-Phrase if needed, then records and routes one sample only after the stack is ready.

Jarvis mature voice gate verification 2026-07-07: `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-voice scripts/ctos-ai scripts/ctos-voice-v2`, `ctos-jarvis --help`, `ctos-jarvis next`, and `ctos-jarvis unlock-voice --plan` passed. Live `ctos-jarvis unlock-voice` reached `ctos-core`, confirmed the Home Assistant tunnel, parsed the doctor output, and expected-failed with `state=missing_token`. `ctos-jarvis unlock-voice --json` produced valid JSON with `ready=false`, one token blocker, and next action `ctos-voice-v2 hass-context onboard-api`. `ctos-jarvis unlock-voice --test` also expected-failed at `missing_token` before attempting a Speech-to-Phrase start. `ctos-jarvis smoke` and targeted `git diff --check` passed.

Jarvis pivot update 2026-07-07: after the operator reported that real voice mostly works but missed `agenda`, CTOS will not make phrase-by-phrase tuning the main path. `ctos-jarvis next` now points first to the open-ended STT plan so a mature Whisper-class local backend can handle natural French requests, while Speech-to-Phrase remains the strict fixed-command rail.

Open-STT manager update 2026-07-07: added `ctos-voice-v2 open-stt status|start|logs|stop` so the selected `docker.io/rhasspy/wyoming-whisper` candidate can be started and stopped on `ctos-core` without raw SSH/podman snippets. The command remains temporary and localhost-only: no systemd unit, no always-on microphone, port `127.0.0.1:10301`, model data under `/srv/ctos/models/open-stt`, and CTOS still routes transcripts through `stp-transcribe --preprocess auto --route`. Live verification reached `ctos-core`, found image/paths ready, started `ctos-open-stt-smoke`, confirmed logs include `Ready`, then stopped it and verified the container was missing again and port `10301` was free.

Open-STT Jarvis facade update 2026-07-07: added `ctos-jarvis listen` as the daily push-to-talk command for the open-ended Whisper/Wyoming rail. It starts the temporary backend if needed, records one phrase, opens the localhost SSH tunnel, routes the transcript through CTOS, and stops the backend if this command started it. `--save-agenda` now reaches the same pending-proposal queue as typed agenda requests, while `--execute-safe` remains limited to CTOS-owned Tier 0/1 actions. Verification covered CLI syntax/help/plan, Wyoming mock routing, read-only remote status, and the `--no-start` guard refusing before microphone capture when the backend is absent.

Jarvis stack selection update 2026-07-07: selected the hybrid mature-stack path instead of phrase-by-phrase tuning. Added `ai/jarvis_stack.json`, `context/22_jarvis_stack_selection.md`, `docs/JARVIS_STACK.md`, and `ctos-jarvis stack`. The next practical loop is the open-STT calibration/proposal POC: `ctos-jarvis calibrate`, then `ctos-jarvis calibrate --save-agenda` only if the transcript/proposal is readable, then `ctos-jarvis review`, then typed confirmation if correct.

Open-STT readiness update 2026-07-07: `ctos-voice-v2 open-stt start` now waits for the container logs to report `Ready` before returning success. This fixed the first synthetic `ctos-jarvis listen --from-wav` failure where the port was open but Wyoming returned `Broken pipe`. A second synthetic French WAV reached the backend and returned a transcript, then CTOS safely refused agenda staging because the synthetic transcript was too degraded to parse as an agenda request. Final status check confirmed `ctos-open-stt-smoke` missing and port `10301` free.

Calibration update 2026-07-07: added `ctos-jarvis calibrate` as the preferred live loop for the Jarvis pivot. It runs one open-STT sample through the existing CTOS boundary and prints mic level, preprocessed STT WAV level, transcript, transcript guard, route, and proposal state. It keeps debug WAVs by default and saves nothing to the agenda unless `--save-agenda` is explicit. The transcript guard now blocks unreadable normalized text, repeated non-speech symbols, and high symbol-noise output before CTOS routing. Synthetic TTS still proves transport only: the latest synthetic sample reached the backend and returned speech-like but degraded text with no agenda proposal. The next useful proof is a real human push-to-talk sample.

Calibration diagnostics update 2026-07-07: `ctos-jarvis calibrate` now handles the flat CTOS route payload returned by `ctos-voice route --json`. The readable report shows route reason, best candidate, agenda-save attempt state, and refusal reason. Synthetic `--save-agenda --stop` reached `ctos-core`, returned a degraded transcript, and safely refused agenda staging with `reason=no recognized agenda proposal`; no agenda proposal was written. `ctos-voice-v2 open-stt status --json` confirmed the temporary container was missing and port `10301` was free after the test.

Session loop result 2026-07-07: added `ctos-jarvis session` with aliases `practice` and `drill`. It runs several readable `calibrate` attempts, prompts before each recording, keeps open-STT running between rounds, and stops it at the end unless `--keep-backend` is explicit. `--save-agenda` can stage recognized agenda proposals, but the loop still cannot approve agenda writes or create new action authority.

Session review update 2026-07-07: `ctos-jarvis session --save-agenda` now runs the read-only pending agenda review at the end by default. Operators can suppress it with `--no-review` or request it without saving via `--review`. This preserves typed confirmation as the only agenda write path.

Session review verification 2026-07-07: `ctos-jarvis session --help` exposes `--review` and `--no-review`. `ctos-jarvis session --rounds 1 --no-prompt --no-start --seconds 0.1 --stop-on-failure --clean --save-agenda` expected-failed with `backend_not_running`, printed `CTOS agenda review` with `pending 0`, and kept the next write step outside the session. `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-voice-v2` and targeted `git diff --check` passed.

Session preflight result 2026-07-07: `ctos-jarvis session` now runs a read-only preflight before recording: `ctos-audio mic-status`, `ctos-voice-v2 open-stt status --json`, and `ctos-jarvis review --json`. Warnings are non-blocking by default. `--strict-preflight` stops before recording when any check warns. This is meant to catch bad audio/backend state earlier without starting services or changing agenda state.

Jarvis run command result 2026-07-07: added `ctos-jarvis run` as the daily operator command above the lower-level calibration/session tools. It runs the safe open-STT session loop, stages agenda proposals by default, prints the read-only review, and keeps typed `ctos-jarvis confirm latest --yes` as the only agenda write path. It adds no package, service, persistent daemon, or direct model/voice authority. `ctos-jarvis run --plan` exposes the exact lower-level command.

Jarvis run command verification 2026-07-07: `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-voice-v2`, `python3 -m json.tool ai/jarvis_stack.json`, `ctos-jarvis run --help`, `ctos-jarvis run --plan`, `ctos-jarvis run --no-save-agenda --plan`, `ctos-jarvis run --execute-safe --plan`, `ctos-voice-v2 next-commands`, and `ctos-jarvis next` passed. `ctos-jarvis run --rounds 1 --no-prompt --no-start --seconds 0.1 --stop-on-failure --clean` expected-failed with `backend_not_running`, printed preflight warnings plus read-only agenda review, and did not record through open-STT because `--no-start` stopped before backend use. Live `ctos-voice-v2 open-stt status --json` over SSH confirmed the temporary container is missing and port `10301` is free.

Jarvis mature-stack acceleration 2026-07-07: confirmed the product path is not phrase-by-phrase tuning. Keep Home Assistant/Wyoming-compatible local components as replaceable voice/model infrastructure, keep `ctos-jarvis` as the operator facade, and keep CTOS as the action/approval boundary.

Jarvis sample command result 2026-07-07: added an operator-facing way to capture or register reusable voice samples outside the repo. `ctos-jarvis sample "..."` records or imports a labeled WAV, appends a JSONL manifest row, prints replay commands for `ctos-jarvis calibrate --from-wav`, and keeps audio artifacts under local state rather than Git.

Jarvis sample regression compatibility result 2026-07-07: Jarvis sample manifests now carry `expected_text`, and `ctos-voice-v2 regression` scores samples without `intent_id` against expected transcript text. Fixed-command samples still use `intent_id` as the stricter authority.

Jarvis corpus collection result 2026-07-07: added `ctos-jarvis collect` with presets `core`, `commands`, and `agenda`. The default `core` preset records `agenda`, `brief`, `ouvre desk`, `ouvre vms`, and one natural agenda request into the same local sample manifest, adds fixed `intent_id` values for known CTOS commands, and prints the sample inventory plus regression commands. `ctos-jarvis mature-check` now points to `ctos-jarvis collect` when no reusable voice samples exist.

Jarvis corpus collection verification 2026-07-07: `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-voice-v2`, `ctos-jarvis collect --help`, `ctos-jarvis collect --plan`, `ctos-jarvis mature-check --json`, `ctos-voice-v2 next-commands`, `python3 -m json.tool ai/jarvis_stack.json`, and targeted `git diff --check` passed. The check was static/non-recording; live sample capture still requires the operator microphone.

Jarvis collect preflight update 2026-07-08: `ctos-jarvis collect` now runs a
read-only local audio preflight before guided recording: output status and
microphone status through `ctos-audio`. It warns by default, can stop before
recording with `--strict-preflight`, and can be skipped with `--no-preflight`
for capture-path debugging. This adds no package, daemon, backend start,
always-on microphone, or action authority.

Jarvis collect preflight verification 2026-07-08: `python3 -m py_compile
scripts/ctos-jarvis scripts/ctos-voice-v2`, `python3 -m json.tool
ai/jarvis_stack.json`, `ctos-jarvis collect --help`, `ctos-jarvis collect
--plan`, `ctos-jarvis collect --plan --no-preflight`, and targeted
`git diff --check` passed. No live microphone recording was run during this
verification.

Jarvis corpus readiness result 2026-07-07: added `ctos-jarvis corpus` with aliases `corpus-check` and `sample-check`. It reads the reusable sample manifest, checks preset coverage, sample count, referenced WAV existence, and audio-state warnings, then reports the next command. `ctos-jarvis mature-check` now points to `ctos-jarvis corpus` once at least one sample exists, and remains pointed at `ctos-jarvis collect` when the corpus is empty.

Jarvis corpus readiness verification 2026-07-07: `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-voice-v2` passed. `ctos-jarvis corpus --json` expected-failed with state `empty` because the real operator sample manifest is not captured yet. Temporary manifests verified the `ready` state with `ctos-jarvis corpus --manifest /tmp/ctos-jarvis-corpus-test-ready.jsonl --json` and the `incomplete` state with `ctos-jarvis corpus --manifest /tmp/ctos-jarvis-corpus-test-incomplete.jsonl --allow-incomplete`. `ctos-jarvis collect --plan`, `ctos-jarvis mature-plan --commands`, `ctos-voice-v2 next-commands`, `python3 -m json.tool ai/jarvis_stack.json`, and targeted `git diff --check` passed.

Jarvis corpus triage result 2026-07-08: added `ctos-jarvis triage` with aliases
`decide` and `verdict`. It runs the existing read-only corpus and sample checks,
then returns one operator verdict: `capture_corpus`, `complete_corpus`,
`repair_sample_files`, `repair_manifest`, `recapture_weak_audio`,
`benchmark_backends`, or `inspect_state`. It does not record audio, transcribe,
start open-STT, touch Home Assistant, or mutate agenda state. `ctos-jarvis
next`, `ctos-jarvis mature-check`, and the Jarvis docs now point the operator
toward triage after samples exist.

Jarvis corpus triage verification 2026-07-08: `python3 -m py_compile
scripts/ctos-jarvis scripts/ctos-voice-v2`, `python3 -m json.tool
ai/jarvis_stack.json`, `ctos-jarvis triage --help`, `ctos-jarvis
mature-plan --commands`, `ctos-voice-v2 next-commands`, and targeted
`git diff --check` passed. `ctos-jarvis triage --json` on the real empty
manifest expected-failed with `capture_corpus`; a temporary complete manifest
under `/tmp` produced `benchmark_backends`; a temporary manifest with one
`audio_state=clipped` sample expected-failed with `recapture_weak_audio`. The
temporary manifests used placeholder WAV files and did not test recognition
quality.

Jarvis corpus evaluation result 2026-07-08: added `ctos-jarvis evaluate` with aliases `eval` and `test-corpus`. It runs the corpus readiness gate first, refuses to launch regression on an empty or broken sample manifest, and can compare the local fallback and open-STT/Wyoming rails with `--backend both` once the corpus is ready.

Jarvis corpus evaluation verification 2026-07-08: `python3 -m py_compile scripts/ctos-jarvis scripts/ctos-voice-v2`, `python3 -m json.tool ai/jarvis_stack.json`, `ctos-jarvis evaluate --plan`, `ctos-jarvis evaluate --backend both --plan`, `ctos-jarvis collect --plan`, `ctos-jarvis mature-plan --commands`, and `ctos-voice-v2 next-commands` passed. `ctos-jarvis evaluate --json` expected-failed with state `empty` on the real missing sample manifest and ran no regression.

Jarvis improve loop result 2026-07-08: added `ctos-jarvis improve` with aliases
`cycle` and `advance`. It runs corpus triage first, then chooses one next safe
step: strict guided collection for empty/incomplete/weak corpus, backend
evaluation for ready corpus, or sample/manifest inspection for repair states.
Without `--run` it only prints the selected command. With `--run` it delegates
to the existing guarded command and adds no package, service, daemon, model
runtime, always-on microphone, or new action authority.

Jarvis improve loop verification 2026-07-08: `python3 -m py_compile
scripts/ctos-jarvis scripts/ctos-voice-v2`, `python3 -m json.tool
ai/jarvis_stack.json`, `ctos-jarvis improve --help`, `ctos-jarvis improve`,
`ctos-jarvis improve --json`, `ctos-jarvis improve --json --run`
expected-refused interactive audio capture on the real empty corpus without
`--yes`, temporary ready/weak manifests selected evaluate/collect respectively,
`ctos-jarvis mature-plan --commands`, `ctos-voice-v2 next-commands`, and
targeted `git diff --check` passed.

Jarvis one-phrase capture result 2026-07-08: added `ctos-jarvis collect-next`
with aliases `sample-next` and `next-sample`. It inspects the reusable corpus
manifest, chooses the first missing preset phrase or first weak-audio sample,
then prints one exact `ctos-jarvis sample ...` command. It is plan-only by
default and records audio only with `--run`. When the corpus is already ready,
it points to `ctos-jarvis evaluate --backend both`.

Jarvis one-phrase capture verification 2026-07-08: `python3 -m py_compile
scripts/ctos-jarvis scripts/ctos-voice-v2`, `python3 -m json.tool
ai/jarvis_stack.json`, `ctos-jarvis collect-next --help`,
`ctos-jarvis collect-next`, `ctos-jarvis collect-next --json`,
`ctos-jarvis collect-next --json --run` expected-refused interactive capture
without `--yes`, ready/weak temporary manifests, `ctos-jarvis next`,
`ctos-voice-v2 next-commands`, and targeted `git diff --check` passed.

Jarvis status result 2026-07-08: added `ctos-jarvis status` with aliases `now`
and `mission`. It runs read-only `mature-check`, `improve`, `collect-next`,
and agenda `review`, then prints a compact state and one next operator action.
On the real empty corpus it points to `ctos-jarvis collect-next --run`; on a
temporary ready corpus it points to backend evaluation and `ctos-jarvis run`.

Jarvis status verification 2026-07-08: `python3 -m py_compile
scripts/ctos-jarvis scripts/ctos-voice-v2`, `python3 -m json.tool
ai/jarvis_stack.json`, `ctos-jarvis status`, `ctos-jarvis status --json`,
`ctos-jarvis now`, temporary ready/weak manifests, `ctos-jarvis --help`,
`ctos-jarvis next`, `ctos-voice-v2 next-commands`, and targeted
`git diff --check` passed.

Jarvis audio diagnostic result 2026-07-08: added `ctos-audio doctor [--json]`
and wired it into `ctos-jarvis mature-check` plus collection preflight. The
diagnostic is read-only and distinguishes real output/microphone failure from a
restricted execution context such as Codex sandbox access to DBus/PipeWire.

Jarvis audio diagnostic verification 2026-07-08: `bash -n scripts/ctos-audio`,
`python3 -m py_compile scripts/ctos-jarvis scripts/ctos-voice-v2`,
`ctos-jarvis mature-check --json`, `ctos-jarvis status`, `ctos-jarvis status
--json`, `ctos-audio --help`, and `ctos-jarvis collect-next` passed. In the
restricted Codex context, `ctos-audio doctor [--json]` intentionally returned
`rc=1` with `pipewire_context_denied`; in the live desktop context, doctor
returned `rc=0` with `VOL 77%` and `MIC 20%`.

Jarvis bootstrap loop result 2026-07-08: added `ctos-jarvis bootstrap` with
alias `onboard`. It reads `ctos-jarvis status`, selects the first next action,
and shows it by default. With `--run`, it executes exactly that existing command
and then rechecks status. It adds no model runtime, package, service, daemon,
always-on microphone, or new action authority.

Jarvis bootstrap loop verification 2026-07-08: `python3 -m py_compile
scripts/ctos-jarvis scripts/ctos-voice-v2`, `ctos-jarvis bootstrap`,
`ctos-jarvis bootstrap --json`, `ctos-jarvis bootstrap --json --run`
expected-refused interactive audio without `--yes`, and `ctos-jarvis --help`
passed. On the real empty corpus, bootstrap selects `ctos-jarvis collect-next
--run` and target phrase `agenda`.

Jarvis facade smoke 2026-07-07: `ctos-jarvis` is linked through `~/.local/bin`, `.bashrc` already exposes that path, and `ctos-jarvis smoke` passed the local non-destructive checks: voice backend doctor, voice probe, safe action route, temporary agenda proposal staging, and temporary agenda review.

Jarvis mature-stack refresh 2026-07-08: rechecked the open-source/local
adoption path after the live command test missed `agenda`. The conclusion
remains: do not tune isolated words as the main strategy. Use the captured
corpus and `ctos-jarvis evaluate` to measure recognition, keep Home
Assistant/Wyoming-compatible components as the mature voice substrate, keep
Ollama on `ctos-core` as the bounded model runtime, and keep CTOS as the only
action/approval boundary. No new package/service was selected in this refresh.

## Active Phase: Knowledge Bootstrap

- [x] Read `CTOS_HANDOVER.md`.
- [x] Confirm repo state and available files.
- [x] Research Codex instruction mechanism.
- [x] Create repository `AGENTS.md`.
- [x] Create `context/` knowledge structure.
- [x] Verify created files and Git status.
- [ ] Brainstorm open questions with user.

## Next Phase: Workstation Bootstrap Planning

- [ ] Decide exact base target: pure Arch vs EndeavourOS minimal.
- [x] Decide fleet model: full-in independent machines.
- [ ] Decide repo architecture: dotfiles, scripts, package manifests, docs, assets, VM definitions.
- [x] Research and decide VS Code/Codex install path.
- [x] Install VS Code/Codex on T480 via SSH.
- [x] Push initial repo bootstrap to GitHub and pull it on T480.
- [x] Add T480's own SSH public key to GitHub for independent Git access.
- [x] Log into Codex on T480.
- [x] Remove temporary passwordless sudo rule from T480.
- [x] Add repo onboarding for quick Codex handoff.
- [ ] Research and decide secrets management.
- [ ] Research and decide firewall/DNS/killswitch design.
- [x] Research and decide VM lifecycle model.
- [ ] Research and decide local AI/RAG stack for T480 constraints.
- [ ] Design bug bounty workflow boundaries and AI-assisted knowledge loop.
- [ ] Design future personal-server sync model.

## Later Implementation Phases

- [ ] Build package manifests.
- [ ] Build idempotent bootstrap scripts.
- [ ] Add Hyprland/Waybar CTOS configuration.
- [ ] Add host security baseline.
- [ ] Add libvirt VM automation.
- [ ] Add AI knowledge base setup.
- [ ] Add verification scripts.
- [ ] Add recovery/rebuild runbook.
Jarvis safe action fix result 2026-07-08: `ctos-ai open-vms` now keeps the
same Tier 1 VMS launcher but surfaces Hyprland/launcher failures instead of
returning a silent `rc=2`. Live desktop verification passed: `ctos-ai
open-vms` and `ctos-jarvis text "ouvre vms" --json` both opened the VMS panel
with `rc=0`.

Jarvis stack manifest repair result 2026-07-08: restored
`ai/jarvis_stack.json` as the selected mature-stack manifest after it had been
overwritten with the voice intent catalog. `ai/voice_intents_fr.json` remains
the phrase catalog, while `ai/jarvis_stack.json` now owns the architecture,
`mature_adoption`, operator path, candidates, and authority boundary again.
Verification passed: `ctos-jarvis stack`, `ctos-jarvis mature-plan --commands`,
`ctos-jarvis mature-check --json`, `ctos-jarvis status`, `ctos-jarvis
status --json`, `ctos-jarvis bootstrap`, and `ctos-jarvis collect-next`.

Jarvis text-first daily cockpit result 2026-07-08: added `ctos-jarvis
stack-check` as a read-only JSON-role guard and `ctos-jarvis daily` as a
read-only daily cockpit view. `daily` aggregates stack integrity, host/agenda
brief, day plan, pending agenda proposals, and the next Jarvis action. It adds
no package, daemon, model runtime, microphone listener, agenda write, VM action,
or desktop mutation.

Jarvis text-first draft rail result 2026-07-08: added `ctos-jarvis draft` as
the typed staging path for natural requests. Default mode only routes and
prints the plan/proposal. `--save` stores a recognized agenda request as a
pending proposal, while the real agenda write remains `ctos-jarvis confirm
latest --yes` after review. Verified with temporary agenda/proposal DBs so the
operator agenda was not polluted.

Jarvis voice-to-draft routing result 2026-07-08: `ctos-jarvis listen`,
`calibrate`, `session`, and `run` now send normal STT transcripts through
`ctos-jarvis draft --source stt`. `--save-agenda` stages pending agenda
proposals through that same rail, while `--execute-safe` stays the only explicit
direct-action mode. Verified with plan commands, local backend-not-running
failure, and an in-memory mocked `cmd_listen` test.

Jarvis inbox consolidation result 2026-07-08: added one read-only
`ctos-jarvis inbox` view for pending agenda proposals and generic CTOS approval
queue items. `ctos-ai approvals` now uses a read-only SQLite path when listing,
so opening the inbox with no approval DB returns an empty list without creating
state. Verified empty inbox, temporary pending agenda proposal, and temporary
generic `kali-console` approval paths.

Jarvis run-to-inbox wiring result 2026-07-08: the normal
`ctos-jarvis run`/`session --save-agenda` path now ends on `ctos-jarvis inbox`
after staging proposals. `--no-inbox` returns to agenda-only `review`,
`--no-review` suppresses both, and contradictory `--inbox` combinations are
refused. Verified with run plans and an in-memory mocked session test.

Jarvis confirm/reject inbox follow-up result 2026-07-08: `ctos-jarvis confirm`
and `ctos-jarvis reject` now return to the consolidated read-only inbox after a
successful agenda decision unless `--no-inbox` is explicit. Both wrappers expose
JSON output for scripted callers, and `reject` stores a `--reason`. Verified
with temporary proposal/agenda DBs for text confirm, JSON confirm, text reject,
JSON reject, and confirm `--no-inbox`.

Jarvis request loop result 2026-07-08: added `ctos-jarvis request` with aliases
`do` and `handle`. It routes one typed natural request, auto-stages only
recognized agenda proposals as pending, and shows the consolidated inbox unless
`--no-inbox` is explicit. `--no-save` keeps route-only behavior, `--json`
returns structured output, and deterministic safe intents are reported but not
executed. Verified with temporary DBs for text request, JSON request, no-save
request, and deterministic `ouvre vms --inbox`.

Jarvis local chat wrapper result 2026-07-08: added `ctos-jarvis chat` with
alias `talk`. It wraps `ctos-ai-chat` with a CTOS bounded system prompt,
supports `--brief`, `--plan`, `--json`, `--speak`, server-start controls, and
one-shot or REPL mode. The authority is read-only: chat can explain and propose
CTOS commands but does not execute actions or write agenda state. Verified plan,
plan JSON with brief injection, structured runtime-unavailable JSON failure, and
`ctos-jarvis next`.

Token/cost-efficient AI lane research result 2026-07-09: reviewed `decolua/9router`
and `Panniantong/Agent-Reach` as current GitHub candidates. No package or daemon
was installed. Recommended next step is an explicit cheap/free CTOS lane:
local Ollama first, optional 9Router adapter second after privacy/secrets review,
Agent Reach only as a read/search capability layer in safe/dry-run mode, and
Codex reserved for final code edits, risky design, and review.

## Active Cheap AI Lane Trial

- [x] Add inert local/cheap coding-assistant profiles.
- [x] Add CTOS commands to inspect and plan the cheap lane.
- [x] Add a bounded local draft command that does not read repo files automatically.
- [x] Verify commands without installing packages or contacting external providers.
- [x] Record decision and verification.

Result 2026-07-10: added candidate runtime profiles for Aider, 9Router, and
Agent-Reach without installing packages, configuring services, adding secrets,
or activating external providers. Added `ctos-ai cheap-lane`,
`ctos-ai cheap-plan`, and `ctos-ai code-draft`. `code-draft` uses only the
explicit operator prompt and local Ollama on `ctos-core`; it does not read repo
files, inspect git state, execute commands, or edit files. Verification passed
for JSON/profile validation, Python compilation, cheap-lane/plan output,
runtime dry-runs for all three candidates, prompt rendering, and a live owned
T480 -> ctos-core 1.5B draft smoke test.

OpenJarvis / Free Claude Code scan result 2026-07-10: OpenJarvis is useful as a
Jarvis sandbox and architecture source, especially for local-first agents,
skills, schedules, and evaluation. Free Claude Code is useful only as a
high-risk optional proxy candidate for the cheap coding lane. Neither should be
installed on the T480 host yet; first test path is isolated, synthetic, and
secret-free.

## Active OpenJarvis Voice Bridge

- [x] Inspect current OpenJarvis installer and runtime requirements.
- [x] Install OpenJarvis in an isolated user/sandbox path, not as a host-wide
  authority.
- [x] Add a CTOS wrapper that can route spoken text toward OpenJarvis/local
  answer mode and CTOS/Codex handoff mode.
- [x] Verify with non-destructive status/help/smoke commands.
- [x] Record sources, constraints, and final install decision.

Result 2026-07-10: OpenJarvis was installed manually into
`~/.local/share/ctos/openjarvis` with a uv-managed Python 3.13 venv. CTOS did
not run the upstream one-line installer. Added `scripts/ctos-openjarvis` and
linked it into `~/.local/bin`. The wrapper writes a CTOS sandbox config with
analytics/update checks disabled, points OpenJarvis to the existing
`ctos-core` Ollama tunnel on `127.0.0.1:11435`, and uses
`qwen2.5-coder:1.5b` by default. Verified `status`, clean `ask`, voice command
planning, and Codex handoff brief generation. Live microphone use is available
through `ctos-openjarvis voice-once`, but should still be tested by the
operator with real speech samples.

## Active Voice Console V0

- [x] Add a localhost-only browser voice chat console.
- [x] Support record, pause, resume, stop/send, replay, typed input, and speak
  last answer.
- [x] Route voice/text to OpenJarvis local chat or Codex handoff brief without
  granting host action authority.
- [x] Add a launcher and user-bin link entry.
- [x] Verify syntax, local server health, and documented run path.

Result 2026-07-10: added `control/voice_console.py`,
`control/static/voice.html`, `control/static/voice.css`,
`control/static/voice.js`, `scripts/ctos-voice-console`, and
`docs/VOICE_CONSOLE.md`. The console is running at `http://127.0.0.1:8770`,
uses existing `ctos-voice`/`ctos-openjarvis`, deletes temporary audio by
default, and exposes no remote listener. Verified Python/Bash/JS syntax,
served HTML, backend status, user-bin link, `git diff --check`, and a local
text POST returning `OK` through OpenJarvis/Ollama.

Live-state update 2026-07-18: the code and launcher remain installed, but no
Voice Console process or `127.0.0.1:8770` listener is currently running. The
2026-07-10 statement above records the earlier verification, not current state.

## Active Browser Access And Network Visibility Plan

- [x] Install one official browser for localhost CTOS tools.
- [ ] Open the CTOS Voice Console through that browser.
- [x] Record the package/security rationale.
- [x] Add the first network-traffic visibility plan without installing capture
  tooling yet.
- [x] Verify CTOS voice console URL and network visibility V0.

Status 2026-07-10: no browser command is currently available on the T480.
Firefox from official Arch `extra` is selected, but installation needs the
operator password in a real sudo terminal:
`sudo pacman -S --needed firefox`. `ctos-voice-console` is already running at
`http://127.0.0.1:8770`. Added `scripts/ctos-netwatch` and
`docs/NETWORK_VISIBILITY.md`; `ctos-netwatch status` works outside the Codex
sandbox and confirmed local interfaces, DNS listeners, SSH, Ollama tunnel,
cockpit, and voice console ports.

Live-state update 2026-07-18: `/usr/bin/firefox` is now present, so the install
gate above is complete. The Voice Console itself is stopped and has not been
reopened during the voice-to-Codex intake.

## Active Voice Console Context Routing

- [x] Add a real CTOS status/brief route for "etat des lieux" style prompts.
- [x] Add a visible `Brief` mode.
- [x] Keep the route deterministic and read-only.
- [x] Verify local API and update documentation.

Result 2026-07-10: Voice Console now has `Chat`, `Brief`, and `Codex`.
`Chat` auto-routes status/config/network wording to the deterministic
read-only brief path, using `ctos-ai brief`, `ctos-netwatch status`, and
`ctos-openjarvis status --json`. Verified `/api/voice/ask-text` in both auto
and explicit `Brief` modes. TTS now speaks a short summary for long status
answers while keeping full details on screen.

## Active Voice Quality / TTS Replacement

- [x] Stop treating `espeak-ng` as the normal Jarvis voice.
- [x] Research current local French-capable TTS options: Piper voices first,
  then Kokoro/ONNX-style local engines if they are light enough.
- [x] Prefer offline/local, intelligible, low-latency, no cloud account, and
  no always-on daemon by default.
- [x] Add a `ctos-voice say --engine ...` or equivalent voice selector before
  changing the default.
- [x] Add a short A/B voice test command with 2-3 fixed French phrases.
- [x] Only then switch Voice Console `Speak`/`Auto speak` to the selected voice.

Result 2026-07-10: Piper is installed as the default offline TTS path for
`ctos-voice say`, and Voice Console `Speak`/`Auto speak` now uses it through
the existing `ctos-voice` wrapper. `espeak-ng` remains only as fallback.

## Active Voice Console Action Queue V0

- [x] Add localhost-only action routing endpoints to Voice Console.
- [x] Reuse existing `ctos-ai` approval and agenda-proposal queues.
- [x] Add UI controls for action mode, queue refresh, approve, and reject.
- [x] Keep execution gated behind explicit click approval.
- [x] Verify syntax and a non-destructive queue flow.
- [x] Record the security/routing decision.

Result 2026-07-10: Voice Console now has `Action` mode plus `Queue last`,
`Refresh`, `Approve`, and `Reject`. V0 recognizes Kali lifecycle/console,
Kali checkpoint, core sync/layout, and agenda proposals. It reuses
`ctos-ai` approval stores and never exposes arbitrary shell execution. Live
server restarted at `http://127.0.0.1:8770`; real queue endpoint is healthy and
previewing `demarre kali` maps to `approval:kali-start` without writing state.

## Active Voice Console Action Vocabulary V0.1

- [x] Add backend aliases for common STT mistakes around `kali`.
- [x] Show canonicalized text in Action preview when aliases are applied.
- [x] Add quick action buttons for Kali start/console/shutdown/checkpoint.
- [x] Keep quick buttons in the same queue/approval path.
- [x] Verify aliases, quick-button payloads, and UI syntax.
- [x] Update docs/context.

Result 2026-07-10: Action mode now canonicalizes observed `Kali` transcript
misses such as `cali`, `quali`, `callie`, `ka li`, and `qu a lit`. The preview
shows the canonical text before queueing. The UI now has quick buttons for
`Start Kali`, `Open Kali`, `Stop Kali`, and `Checkpoint`; they create pending
queue items only and still require `Approve`. Live preview verified
`demarre cali` -> `canonical demarre kali` -> `approval:kali-start`.

## Windows Apple Recovery VM — retired 2026-08-04

- [x] Confirm no live Windows/Apple domain exists.
- [x] Confirm no Windows/Apple libvirt volume, NVRAM, TPM, or managed ISO exists.
- [x] Preserve unrelated Kali VM state and retain source ISO/repository files.
- [x] Stop the Windows Apple-recovery implementation until a new explicit request.
