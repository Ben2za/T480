# Repo Blueprint

Date: 2026-05-04

This is a proposed shape, not final implementation.

## Proposed Top Level

```text
.
|-- AGENTS.md
|-- README.md
|-- context/
|-- docs/
|-- assets/
|-- packages/
|-- dotfiles/
|-- scripts/
|-- systemd/
|-- security/
|-- hyprland/
|-- waybar/
|-- libvirt/
|-- ai/
|-- tests/
`-- Makefile
```

## Roles

- `context/`: working memory, plans, research, decisions.
- `docs/`: stable user-facing runbooks and architecture docs.
- `assets/`: visual assets such as CTOS background.
- `packages/`: package manifests by layer: base, desktop, dev, security, lab, ai.
- `dotfiles/`: shell, Git, editor, terminal, tmux, Neovim, and related config.
- `scripts/`: idempotent bootstrap and verification scripts.
- `systemd/`: user and system service units/timers.
- `security/`: nftables, DNS, kill-switch, log policy, hardening docs.
- `hyprland/` and `waybar/`: desktop configuration.
- `libvirt/`: VM definitions, network definitions, snapshot policy.
- `ai/`: local assistant, RAG, vector DB, model manifests.
- `tests/`: shellcheck, static validation, dry-run checks, VM checks where possible.

## Initial Design Constraints

- Host must stay clean and boring.
- Lab/offensive tooling must be isolated from host workflows.
- Configuration must be idempotent and repeatable.
- No secrets in Git.
- Heavy/generated artifacts stay outside the repo.
- Every non-trivial tool choice gets an ADR.

## Fleet Direction

The repo should support a full-in independent machine profile. Each workstation should be able to operate without depending on another laptop or server.

This does not mean every component must run all the time. It means every component needed for the operator environment is installable and locally recoverable on each machine:

- `base`: bootstrapping, shell, Git, editor, package manager, system hygiene.
- `desktop`: Hyprland, Waybar, theme, launcher, terminal, notifications.
- `dev`: compilers, language toolchains, containers, editor extensions.
- `security-lab`: VM orchestration, Kali/Arch Dev definitions, wordlists, authorized testing tools.
- `ai`: local models, RAG, vector database, knowledge ingestion.
- `server-sync`: future personal server integration for repo, package cache, model cache, and knowledge sync. Server sync is acceleration, not a hard dependency.
