# Working Agreements

Date: 2026-05-04

## Quality Standard

- Factual and impartial output over pleasing language.
- Professional precision: each assumption must be visible, each decision must have a reason.
- Pragmatic execution: smallest reliable step that advances the architecture.
- No hidden compromises. If a choice is uncertain, mark it as uncertain.

## Research Standard

- Current web research is required before package, service, editor, security, AI-stack, or architecture choices.
- Use targeted queries, not generic browsing.
- Prefer primary sources:
  - official project docs
  - Arch Wiki and Arch package metadata
  - upstream GitHub/GitLab repos and release notes
  - security advisories and man pages
- Record the source, date accessed, and conclusion in `context/06_source_registry.md`.

## Planning Standard

- Before multi-step work, update `context/05_task_board.md`.
- Keep unresolved questions in `context/04_open_questions.md`.
- Do not rely on chat history as the only memory.
- Split work into phases small enough to verify.

## Security And Privacy Boundary

- Low trace means: avoid retaining secrets, logs, tokens, loot, browser state, shell transcripts, VM disks, and sensitive generated artifacts in Git.
- This project is for owned devices and authorized lab systems.
- Do not build stealth persistence, third-party evasion, malware behavior, credential theft, destructive tooling, or unauthorized offensive workflows.

## Style

- Text should be human and direct.
- Avoid inflated wording.
- Prefer concrete checklists, commands, and decision records.
