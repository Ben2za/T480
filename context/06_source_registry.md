# Source Registry

Sources consulted for project setup and future decisions.

## 2026-05-04

### Codex project instructions

Question:

What file should be used to configure Codex behavior for this repository, and how should detailed context be organized?

Sources:

- OpenAI Codex AGENTS.md docs: https://developers.openai.com/codex/guides/agents-md
- OpenAI Codex config basics: https://developers.openai.com/codex/config-basic
- OpenAI Codex sample config: https://developers.openai.com/codex/config-sample
- OpenAI Codex hooks docs: https://developers.openai.com/codex/hooks
- OpenAI Codex skills docs: https://developers.openai.com/codex/skills
- OpenAI `agents.md` repository: https://github.com/openai/agents.md
- OpenAI Codex repository AGENTS.md example: https://github.com/openai/codex/blob/main/AGENTS.md

Conclusion:

Use root `AGENTS.md` for short, durable instructions. Put detailed working memory in `context/`. Avoid large instruction files because Codex project-doc loading has a configured size limit by default.

### T480 VS Code and Codex installation

Question:

What should be installed on EndeavourOS/Arch for VS Code and OpenAI Codex?

Sources:

- Microsoft VS Code Linux setup: https://code.visualstudio.com/docs/setup/linux
- Microsoft VS Code download page: https://code.visualstudio.com/download
- AUR `visual-studio-code-bin`: https://aur.archlinux.org/packages/visual-studio-code-bin
- ArchWiki Visual Studio Code: https://wiki.archlinux.org/title/Visual_Studio_Code
- OpenAI Codex GitHub README: https://github.com/openai/codex
- npm `@openai/codex`: https://www.npmjs.com/package/%40openai/codex
- Visual Studio Marketplace OpenAI Codex extension: https://marketplace.visualstudio.com/items?itemName=OpenAI.chatgpt

Conclusion:

Install `visual-studio-code-bin` through AUR for the official Microsoft binary, `nodejs`/`npm` from Arch repositories, Codex CLI through npm global install, and the official VS Code extension `OpenAI.chatgpt`.

### OpenAI Docs MCP note

Question:

Is the OpenAI Docs MCP available in this session?

Result:

No MCP documentation resources were exposed by the local tool context. Fallback browsing was restricted to official OpenAI domains for OpenAI/Codex documentation, then GitHub was used only for public AGENTS.md examples.
