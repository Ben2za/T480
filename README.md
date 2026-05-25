# T480 CTOS Operator Environment

Personal Arch/EndeavourOS workstation rebuild repository.

The goal is a full-in, independent operator environment that can be recreated on each machine: desktop, dev tooling, red-team lab boundaries, AI/Codex workflow, and future personal-server sync.

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
