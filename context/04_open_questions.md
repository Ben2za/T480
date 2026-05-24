# Open Questions

Date: 2026-05-04

## Immediate Clarifications

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

## Current Missing Context

- `Setup.md` is not present in `/home/ben/Desktop/T480`, despite being open in the IDE tab list.

## Temporary Admin Access

- 2026-05-24: T480 reachable from EliteBook via `ssh operator@192.168.1.21`.
- 2026-05-24: temporary sudoers rule installed on T480: `operator ALL=(ALL:ALL) NOPASSWD: ALL`.
- 2026-05-24: VS Code/Codex bootstrap completed while this rule was active.
- 2026-05-24: repo cloned on T480 at `/home/operator/T480`; clone used temporary SSH agent forwarding from EliteBook because T480's own GitHub key is not yet accepted by GitHub.
- 2026-05-24: T480 GitHub SSH public key fingerprint is `SHA256:fWhXvZpNecLxn67fy/+KCi1LRa3W5fUa+sNfZ7lldy8`; add the corresponding public key to GitHub for independent push/pull.
- This rule must be removed after bootstrap/admin setup with:
  `sudo rm /etc/sudoers.d/90-codex-operator`.

## Initial Risk Notes

- "Always cutting edge" can conflict with reproducibility and laptop stability. Proposed interpretation: latest verified stable by default; alpha/nightly only when the decision log records a specific reason.
- "No fallback" is good against hidden downgrade paths, but bad if it means no recovery route. Proposed interpretation: no silent fallback; recovery steps may exist but must be explicit and documented.
- OPSEC requirements must stay inside lawful owned-system privacy and lab isolation.
- Bug bounty/red-team automation must remain scoped to authorized programs, owned lab infrastructure, and documented rules of engagement.
