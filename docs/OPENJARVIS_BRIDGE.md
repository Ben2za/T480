# CTOS OpenJarvis Bridge

OpenJarvis is installed as a CTOS sandbox under:

- `~/.local/share/ctos/openjarvis/src`
- `~/.local/share/ctos/openjarvis/.venv`
- `~/.local/share/ctos/openjarvis/state`

CTOS does not run the upstream installer as-is. The upstream installer can
install Ollama, pull a default model, install user commands, start a background
orchestrator, and enable anonymous analytics. CTOS keeps those choices explicit.

Current bridge:

```bash
ctos-openjarvis status
ctos-openjarvis ask "resume ma journee en 3 points"
ctos-openjarvis chat
ctos-openjarvis voice-once --seconds 5
ctos-openjarvis voice-once --mode codex --seconds 5
```

Model traffic goes to Ollama on `ctos-core` through the local CTOS tunnel:

```text
127.0.0.1:11435 -> ctos@10.42.0.2:127.0.0.1:11434
```

Default model:

```text
qwen2.5-coder:1.5b
```

Authority boundary:

- OpenJarvis may answer, plan, and help draft.
- CTOS owns action routing and approvals.
- Codex owns real repo edits when the operator explicitly hands off a task.
- Voice transcript does not get shell authority by default.
