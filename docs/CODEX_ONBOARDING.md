# Codex Onboarding

This guide is for quickly taking control of the repo from the T480 itself.

## 1. Health Check

Run from a terminal on the T480:

```bash
cd ~/T480
git status --short --branch
git pull --ff-only origin main
codex login status
codex --version
```

Expected:

- Git branch is `main`.
- GitHub SSH works without agent forwarding.
- `codex login status` says you are logged in.

If Codex is logged out:

```bash
codex login --device-auth
```

Open the displayed URL on any browser-capable device, enter the one-time code, then rerun:

```bash
codex login status
```

## 1.1 Auth Reset If Refresh Token Breaks

Symptom:

```text
your access token could not be refreshed because your refresh token was already used
```

Do not reboot first. Reset the local Codex auth state:

```bash
# Close VS Code first so the OpenAI extension does not run a Codex app-server.
pkill -u "$USER" -x codex 2>/dev/null || true
codex logout || true
mv ~/.codex/auth.json ~/.codex/auth.json.invalid-$(date +%Y%m%d%H%M%S) 2>/dev/null || true
codex login --device-auth
codex login status
codex doctor --summary
```

Expected final doctor result:

```text
0 warn · 0 fail
```

## 2. Start Codex In This Repo

```bash
cd ~/T480
codex
```

Useful variants:

```bash
codex --search
codex --no-alt-screen
codex -s workspace-write -a on-request
codex resume
codex doctor
```

Use `--search` when asking for current package, security, Arch, VS Code, or OpenAI/Codex guidance.

## 3. First Prompt Template

Use a prompt like:

```text
Read AGENTS.md and context/README.md first. Then inspect the relevant repo files before making changes. Keep decisions documented in context/02_decision_log.md and update context/05_task_board.md.
```

## 4. What Codex Should Treat As Memory

Codex conversations do not sync through Git. Durable project memory is stored in:

- `AGENTS.md`
- `context/00_project_brief.md`
- `context/02_decision_log.md`
- `context/04_open_questions.md`
- `context/05_task_board.md`
- `context/06_source_registry.md`

If a decision matters later, put it in `context/`, not only in chat.

## 5. Git Workflow

```bash
cd ~/T480
git pull --ff-only origin main
git status
git add <files>
git commit -m "Short factual message"
git push origin main
```

Do not commit:

- private keys
- tokens
- `.env`
- logs
- VM images
- loot
- private reports
- large generated artifacts

## 6. VS Code Notes

Open the repo:

```bash
cd ~/T480
code .
```

Git operations inside VS Code should work because the repo remote uses SSH and the T480 GitHub key is validated.

VS Code account sign-in is separate from Git CLI SSH. If Git pull/push works but a VS Code feature asks you to sign in, use the Accounts icon in VS Code for that specific feature.

## 7. Admin Boundary

The temporary passwordless sudo bootstrap rule has been removed.

If a future task needs root, Codex should ask explicitly and the user should approve a narrow command or run it locally.
