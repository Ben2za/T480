# Open Questions

Date: 2026-05-04

## Immediate Clarifications

Reopened 2026-10-06: after preserving the current repository on GitHub, define
the T480's intended new role, target OS if changing, and which local data or VM
state must survive any conversion. Repository publication does not back up
home-directory data, credentials, VM disks, or runtime databases.

1. Base distro: pure Arch Linux or EndeavourOS minimal kept as the practical base?
2. Rebuild target: reinstall from bare disk, post-install bootstrap on an existing Arch install, or both?
3. Dotfile manager: plain Git + install scripts, GNU Stow, chezmoi, yadm, or another tool? Research required before decision.
4. Secrets model: age/sops, pass, KeePassXC, hardware key, SSH agent, or no secrets in repo at all? Research required.
5. RESOLVED: "Dead-laptop" was an image. Actual goal: reproduce the same config and knowledge across many PCs, first local, later via personal server.
6. Trace minimization target: local shell history, logs, browser traces, package cache, VM artifacts, application telemetry, Git metadata, or all of these?
7. VS Code choice: Microsoft VS Code package, Arch `code` build, VSCodium, or Cursor/Windsurf? Research required because privacy, extensions, and Codex support differ.
8. Codex scope: CLI only, VS Code extension, ChatGPT Codex cloud, or all three?
9. AI stack: Ollama + Qdrant still desired, or should we reassess current best local RAG stack for a T480-class laptop?
10. Offensive lab boundary: should Kali be a disposable VM rebuilt from scripts, a persistent VM snapshot, or both?
11. VPN: self-hosted WireGuard only, commercial VPN, Tor for specific workflows, or no network privacy layer until firewall/DNS are done?
12. Logs policy: what needs to be kept for debugging versus wiped for privacy?
13. RESOLVED: Fleet model is full-in independent machines. Role overlays are rejected for the current objective.
14. Personal server future: Git server only, secrets broker, package cache, model registry, knowledge sync, CI runner, or all of these?
15. Bug bounty AI workflow: target discovery, scope parsing, recon note-taking, duplicate clustering, report drafting, code review, payload generation for authorized targets, or all of these?
16. Tower inventory: exact CPU, GPU, RAM, storage layout, firmware mode, Secure Boot state, wired/wireless network, and whether Windows data must be preserved.
17. RESOLVED 2026-06-12: Tower install path is wipe Windows and install EndeavourOS as `ctos-core`.
18. Fleet update transport: GitHub only at first, LAN Git mirror on `ctos-core`, USB kit transfer, or all three in phases?
19. Fleet orchestrator timing: plain idempotent repo scripts first, or install Ansible once `ctos-core` exists?
20. Package cache/model cache: should `ctos-core` eventually cache pacman packages, AUR build artifacts, AI model weights, or only repo/bootstrap data?
21. RESOLVED for V1: KRFB is not the remote-control backend. Runtime note 2026-06-16: observed `krfb` default listener is `0.0.0.0:5900` and `[::]:5900`; after firewall guarding and SSH tunneling, TigerVNC could authenticate and display a frame, but no live refresh or input worked even with `allowDesktopControl=true`. Do not keep KRFB running.
22. RESOLVED for current Wayland session: `w0vncserver` is not the V1 backend. It stayed localhost-only and accepted the tunnelled client, but produced `0` framebuffer updates and no visible T480 viewer window. Next remote desktop backend test is Plasma X11 plus `x0vncserver`.
23. Remote desktop baseline: should `ctos-core` stay on Plasma X11 for V1 remote control if `x0vncserver` works, or should X11 remain a dedicated admin-mode session while daily desktop use returns to Wayland later?
24. RESOLVED for voice-to-Codex V1 on 2026-07-18: use authenticated Codex as the primary coding/reasoning executor and local Ollama only for bounded voice/spec preprocessing. Do not silently fall back from a Codex auth/quota/service failure to a weaker local model.
25. RESOLVED for voice-to-Codex V1 on 2026-07-18: use the supported direct `codex exec` CLI first. Add MCP only for a concrete tool/context requirement after the spec/approval boundary works; do not make MCP or UI automation a prerequisite.
26. CTOS AI approval UX: exact confirmation shape for Tier 2 actions before any model can mutate CTOS state.
27. CTOS AI memory/privacy: raw voice audio/transcripts may not be passed to Codex or persisted as project memory. Still decide which operator-reviewed normalized task specs/summaries, agenda items, and personal notes may persist locally and for how long.
28. CTOS AI voice: when, if ever, to enable always-on microphone/wake word versus push-to-talk only?
29. CTOS AI calendar integration: local-only agenda first, CalDAV/Google later, or no external calendar until the secrets model is solved?
30. RESOLVED for Voice V1: use local Vosk with `vosk-model-small-fr-0.22` for push-to-talk only. Whisper remains a later dictation-quality candidate; cloud STT and always-on microphone are out of scope.
31. ctos-core Wi-Fi hardware state: as of 2026-07-07, the saved `Livebox-8F18` profile exists but the kernel/NetworkManager see no Wi-Fi device and `lsusb` does not list a Wi-Fi adapter. Confirm whether the external Wi-Fi key is physically plugged in, powered, and recognized after a replug.
32. CTOS Speech-to-Phrase live test context: choose the smallest temporary Home Assistant/Wyoming context and token-file path for one localhost-only recognition loop on `ctos-core`; no persistent service until that test passes.
33. RESOLVED 2026-07-18: `/usr/bin/firefox` now exists on the T480, so the missing-browser gate is stale. The temporary Home Assistant container is currently stopped and its token is still missing; starting/onboarding it remains a separate live voice-backend step.
34. RESOLVED for TTS V0: current `espeak-ng`/`espeak` output was too harsh/incomprehensible for real Jarvis use. Piper is the first local French-capable replacement trial, installed in a user venv with `fr_FR-siwis-medium`; cloud TTS remains out of scope unless explicitly accepted later.
35. iPhone recovery: exact iPhone model and iOS version are unknown; these determine which Apple-supported on-device reset flow is available.
36. iPhone recovery: confirm whether the owner can sign in to the Apple Account currently linked to the phone, including trusted-number/device access and Activation Lock credentials.
37. iPhone recovery: before any erase, confirm whether iCloud Photos, an iCloud device backup, or a pre-existing Finder/Apple Devices/iTunes backup contains the family photos.
38. iPhone recovery: confirm whether the passcode was changed within the last 72 hours; supported recent-passcode recovery may exist on iOS 17 or later.
39. RESOLVED 2026-07-17: operator identified the phone as an iPhone XS using Google Lens. No IMEI, serial number, ECID, or account identifier was collected.
40. RESOLVED 2026-07-17: the operator has no Windows license for this VM. A durable Windows/Apple baseline must not be installed or sealed until an entitlement that explicitly covers this VM is identified; do not store a future key or account credential in repo or logs.
41. Windows Apple VM Store identity: determine during implementation whether Microsoft Store product `9NP83LWLPZ9K` installs through `winget --source msstore` without retaining a personal Microsoft account. If not, stop and choose an explicit non-personal account handling policy.
42. Windows Apple VM USB-C: after a guarded `intel_iommu=on` preflight reboot, confirm the complete IOMMU group and physical port mapping for `0000:3c:00.0`. Controller passthrough remains blocked until isolation, host charging, detach, and reattach all pass.
43. Windows Apple VM physical gate: the locked iPhone is currently present as `/sys/class/typec/port1-partner` in `source/host` roles even though `lsusb` is empty. It must be unplugged before the IOMMU boot change, reboot, controller detach, or VM start can proceed.
44. Windows media: media acquisition now follows the licensing choice. For a durable VM, obtain an eligible entitlement first and then re-verify the current consumer ISO on Microsoft's live page. The official Windows 11 Enterprise 25H2 Evaluation is a separate 90-day, Microsoft-account-dependent, disposable test option only; it has not been authorized. Do not use a mirror or stale CDN URL.
45. Windows Apple VM USB test: identify a non-sensitive removable USB peripheral for port mapping and re-enumeration. Do not substitute the iPhone for this test.
46. Windows Apple VM evaluation choice: decide whether to authorize a disposable official 90-day Enterprise Evaluation VM, accepting Microsoft-account use and mandatory deletion/rebuild before expiry, or leave Windows installation paused until an eligible durable VM entitlement is obtained.
47. RESOLVED 2026-07-18: EliteBook/ZLiteBook reconnect target is `BXEB` / `bxeb.home` / `192.168.1.24`, user `ben`. T480 key-based SSH succeeds. It is added as `ctos-zlitebook` worker candidate, not a full CTOS role node.
48. PARTIALLY RESOLVED 2026-07-18: for voice V1, `BXEB` is the operator/browser/microphone endpoint and the T480 remains the home control/Codex node; do not add worker services to `BXEB` for this POC. Its later OS conversion and general fleet worker role remain open.
49. Voice-to-Codex mutation gate: define the exact operator preview/approval UX and tests required before the accepted read-only ephemeral `codex exec` adapter may expose a workspace-write mode.
50. Outside-home transport approval: accept the recommended private Tailscale transport plus existing key-based OpenSSH, including its hosted control-plane/identity-provider tradeoff, or require a later self-hosted WireGuard design? In either case, do not expose SSH, Voice Console, VNC, or Funnel publicly.
51. T480 home availability: define AC power, lid-close/sleep/hibernate, boot-service, and recovery behavior before relying on outside-home access. A private overlay cannot reach or wake a sleeping/offline T480; wake-on-LAN through `ctos-core` would be a separate later design.
52. Voice-to-Codex live disclosure gate: authorize or decline one synthetic,
    secret-free, read-only smoke that sends the reviewed canonical spec and may
    request inspection of the six allowed repository files
    (`ai/voice_task_spec.py`,
    `ai/voice_task_spec.schema.json`, `ai/codex_readonly_result.schema.json`,
    `scripts/ctos-codex-voice`, `tests/test_voice_task_spec.py`, and
    `tests/test_ctos_codex_voice.py`) through OpenAI. The runner disables user
    config, web search, and automatic project instructions and tells Codex not
    to read outside that scope. However, `read-only` prevents writes rather
    than providing OS-enforced per-file read isolation, so informed approval
    must acknowledge that the rest of `/home/operator/T480` remains technically
    readable by the CLI process. The attempted acceptance run did not start.
    Until informed approval is recorded,
    `CTOS_VOICE_CODEX_RUN_ENABLED` stays unset/false and the browser cannot
    execute Codex.

## Current Missing Context

- `Setup.md` is not present in `/home/ben/Desktop/T480`, despite being open in the IDE tab list.

## Runtime Verification Needed

- 2026-05-26: Codex sandbox blocks system bus, netlink, libvirt socket, EFI, and sudo runtime checks. Future implementation that depends on actual service state, network state, libvirt VM state, EFI loader state, or sudo policy needs a narrow out-of-sandbox verification step.
- 2026-05-26: Confirm whether existing host config should be imported as-is into the repo or treated as a disposable prototype to be rebuilt declaratively.
- 2026-05-26: Confirm trace policy before deleting or rotating local shell history, Codex state/logs, npm logs, package cache, system logs, ISO files, or VM artifacts.
- 2026-06-02: RESOLVED for CTOS-managed domains: use `qemu:///system`; keep `qemu:///session` read-only inventory only.
- 2026-06-02: RESOLVED initial pool layout: dedicated `ctos-images` and `ctos-snapshots` system pools under `/var/lib/libvirt/ctos/`. Current Kali volume and ISO metadata still show owner `nobody:nobody`; decide separately whether to remove/import the existing Kali qcow2 stub.
- 2026-06-02: Snapshot policy partially resolved: first automation should use shutoff disk snapshots only. Still open: naming, retention, and exact internal-vs-external implementation.
- 2026-06-03: Decide the post-install transition for `ctos-kali`: detach ISO, change boot order, create baseline snapshot, and rename/remove `ctos-kali.install.xml` from active use.
- 2026-06-09: RESOLVED 2026-06-12 for tower: user explicitly chose Windows wipe and EndeavourOS install. Remaining destructive actions still require visible disk confirmation.

## Temporary Admin Access

- 2026-05-24: T480 reachable from EliteBook via `ssh operator@192.168.1.21`.
- 2026-05-24: temporary sudoers rule installed on T480: `operator ALL=(ALL:ALL) NOPASSWD: ALL`.
- 2026-05-24: VS Code/Codex bootstrap completed while this rule was active.
- 2026-05-24: repo cloned on T480 at `/home/operator/T480`; clone used temporary SSH agent forwarding from EliteBook because T480's own GitHub key is not yet accepted by GitHub.
- 2026-05-24: T480 GitHub SSH public key fingerprint is `SHA256:fWhXvZpNecLxn67fy/+KCi1LRa3W5fUa+sNfZ7lldy8`.
- 2026-05-25: T480 GitHub SSH key added to GitHub and validated with `git fetch origin main` from `/home/operator/T480`.
- 2026-05-24: Codex CLI on T480 logged in successfully with ChatGPT device auth.
- 2026-05-25: temporary sudoers rule removed. `sudo -n` now fails again as expected.

## Initial Risk Notes

- "Always cutting edge" can conflict with reproducibility and laptop stability. Proposed interpretation: latest verified stable by default; alpha/nightly only when the decision log records a specific reason.
- "No fallback" is good against hidden downgrade paths, but bad if it means no recovery route. Proposed interpretation: no silent fallback; recovery steps may exist but must be explicit and documented.
- OPSEC requirements must stay inside lawful owned-system privacy and lab isolation.
- Bug bounty/red-team automation must remain scoped to authorized programs, owned lab infrastructure, and documented rules of engagement.
