# Decision Log

All significant choices must be documented here before implementation.

Format:

```text
ID:
Date:
Status: proposed | accepted | rejected | blocked | superseded
Decision:
Context:
Options considered:
Sources:
Rationale:
Verification:
Consequences:
```

## ADR-0001: Use AGENTS.md plus context folder for Codex project knowledge

Date: 2026-05-04
Status: accepted

Decision:

Use a short repository-root `AGENTS.md` for durable Codex instructions and keep detailed knowledge in `context/`.

Context:

The user explicitly requested a local context folder and better agent configuration. OpenAI Codex documentation describes `AGENTS.md` as the project instruction file. The same documentation states Codex has a default project-doc size limit, so detailed memory should not be packed into one large instruction file.

Options considered:

- Put everything in `AGENTS.md`.
- Put only durable rules in `AGENTS.md` and detailed memory in `context/`.
- Use an undocumented filename such as `Setup.md` as the main instruction source.

Sources:

- OpenAI Codex AGENTS.md documentation, accessed 2026-05-04: https://developers.openai.com/codex/guides/agents-md
- OpenAI Codex config basics, accessed 2026-05-04: https://developers.openai.com/codex/config-basic
- OpenAI Codex skills documentation, accessed 2026-05-04: https://developers.openai.com/codex/skills
- OpenAI `agents.md` open format repository, accessed 2026-05-04: https://github.com/openai/agents.md

Rationale:

This gives Codex stable repo-local rules while keeping detailed project knowledge organized, editable, and less likely to be silently truncated.

Verification:

Files created in repo root and `context/`; final verification pending.

Consequences:

Future detailed context updates should go into `context/`, not into a growing `AGENTS.md`.

## ADR-0002: Install official VS Code binary and OpenAI Codex on T480

Date: 2026-05-24
Status: accepted

Decision:

Install Microsoft Visual Studio Code through AUR package `visual-studio-code-bin`, install Node.js/npm from Arch repositories, install Codex CLI with `npm install -g @openai/codex`, and install the official Codex VS Code extension `OpenAI.chatgpt`.

Context:

The T480 is EndeavourOS/Arch-like, reachable via `ssh operator@192.168.1.21`, with temporary passwordless sudo enabled for bootstrap. Git and yay are already installed; `code`, `node`, `npm`, and `codex` are not installed.

Options considered:

- `visual-studio-code-bin` from AUR: official Microsoft binary distribution, provides `code`/`vscode`, conflicts with `code`.
- `code` from Arch repositories: open-source Code - OSS build, but not the same Microsoft binary distribution.
- Manual tarball/RPM/deb: worse integration with Arch package management.
- Snap: not native to current EndeavourOS setup and unnecessary.

Sources:

- Microsoft VS Code Linux setup, accessed 2026-05-24: https://code.visualstudio.com/docs/setup/linux
- Microsoft VS Code download page, accessed 2026-05-24: https://code.visualstudio.com/download
- AUR `visual-studio-code-bin`, accessed 2026-05-24: https://aur.archlinux.org/packages/visual-studio-code-bin
- ArchWiki Visual Studio Code, accessed 2026-05-24: https://wiki.archlinux.org/title/Visual_Studio_Code
- OpenAI Codex GitHub README, accessed 2026-05-24: https://github.com/openai/codex
- npm `@openai/codex`, accessed 2026-05-24: https://www.npmjs.com/package/%40openai/codex
- Visual Studio Marketplace OpenAI Codex extension, accessed 2026-05-24: https://marketplace.visualstudio.com/items?itemName=OpenAI.chatgpt

Rationale:

The user asked for VS Code and Codex on the ThinkPad itself. The official VS Code binary is the closest match to "VS Code" and has the expected Microsoft Marketplace behavior. OpenAI documents Codex CLI installation through npm, and the Marketplace extension ID is `OpenAI.chatgpt`.

Verification:

Completed on 2026-05-24 over SSH to `operator@192.168.1.21`:

- `code --version`: `1.121.0`, commit `f6cfa2ea2403534de03f069bdf160d06451ed282`, `x64`.
- `node --version`: `v26.2.0`.
- `npm --version`: `11.14.1`.
- `codex --version`: `codex-cli 0.133.0`.
- `code --list-extensions --show-versions`: `openai.chatgpt@26.519.32039`.
- Pacman packages: `linux 7.0.10.arch1-1`, `linux-lts 6.18.33-1`, `nodejs 26.2.0-1`, `npm 11.14.1-1`, `visual-studio-code-bin 1.121.0-1`.

Consequences:

This accepts Microsoft VS Code proprietary licensing and npm global installation. A reboot is recommended because the running kernel is still `6.18.26-2-lts` while installed LTS is `6.18.33-1`. The temporary sudoers rule must be removed after bootstrap.
