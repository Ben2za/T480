# CTOS Arch Rebuild Repo Instructions

## Working Contract

- Be factual, impartial, and precise. Do not optimize for user satisfaction when it conflicts with technical quality.
- Use pragmatic engineering judgement: prefer simple, auditable, reproducible mechanisms over aesthetic complexity.
- Do not make undocumented technical choices. For any package, service, security control, or architecture decision, record the date, sources, constraints, and final rationale in `context/02_decision_log.md`.
- For time-sensitive choices, use current web research before deciding. Prefer official upstream docs, Arch Wiki, package release notes, and primary security documentation.
- No silent fallback. If a leading/current option cannot be verified or made reliable, stop, document the blocker, and propose the smallest next investigation.
- Treat OPSEC as privacy and safety engineering for owned systems only. Do not implement unauthorized access, stealth persistence, credential theft, destructive behavior, or evasion for third-party systems.
- Minimize durable local traces: never commit secrets, tokens, private keys, loot, VM disks, logs, browser state, command transcripts, or generated sensitive artifacts.

## Repo Knowledge

- Read `context/README.md` before substantial work.
- Keep `AGENTS.md` short enough to avoid instruction truncation. Put detailed memory, research, and plans under `context/`.
- Update `context/05_task_board.md` before and after multi-step work.
- Add unresolved assumptions to `context/04_open_questions.md`; do not bury them in chat only.
- When a source file mentioned by the user is missing, record it as missing context instead of guessing.

## Implementation Rules

- Prefer declarative, idempotent setup over manual shell history: scripts, package manifests, dotfiles, systemd units, and documented bootstrap steps.
- Separate host, lab VMs, AI stack, secrets, and offensive tooling boundaries. The host stays clean; offensive workflows belong in isolated lab VMs.
- Avoid global Python package installs. Use virtual environments, `uv`, or package-manager native installs after research and documentation.
- Before editing config, inspect existing files and preserve user changes.
- Verify changes with the narrowest useful command, then record what was verified.
