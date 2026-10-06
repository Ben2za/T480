# CTOS AI V0 Model

Date: 2026-06-17

Scope: first durable model for a Jarvis-like CTOS assistant that can help plan, code, operate owned machines, and eventually coordinate workers without giving an LLM uncontrolled shell access.

## Intent

The target is not a generic "Jarvis" fork. The target is `ctos-ai`: an operator assistant shaped around the existing CTOS architecture.

- T480 remains the mobile control plane and personal work machine.
- `ctos-core` is the heavier node for workers, local runtimes, model cache, and future services.
- Kali and offensive/security tooling remain in isolated lab boundaries.
- The assistant may help operate owned machines, but every action path must be explicit, auditable, and permission-scoped.

## Inspiration Scan

### OpenHands / Agent Canvas

Useful pattern:

- multi-agent developer control center;
- local, remote, VM, container, and cloud backends;
- scheduled or event-driven automations;
- agent backend switching from a central UI.

Do not copy directly for V0:

- it is a large platform relative to our current repo;
- its own quickstart warns that running without a sandbox gives broad filesystem access;
- CTOS needs a narrower permission contract before a general agent server is safe.

What to borrow:

- backend registry idea for future `ctos-worker-*`;
- automation queue idea for scheduled tasks;
- "agent server can run on a dedicated machine" shape for `ctos-core`.

### Open Interpreter

Useful pattern:

- natural-language terminal interface to code execution and computer capabilities;
- local model/provider flexibility;
- interesting reference for "assistant as local operator".

Do not copy directly for V0:

- a broad computer interface is too much authority for the first CTOS AI layer;
- CTOS already has scripts for cockpit, fleet, VMs, and remote desktop, so we should wrap those as named tools instead of exposing arbitrary shell.

What to borrow:

- a conversational terminal/UI surface;
- controlled code execution as a later sandboxed worker mode.

### LangGraph

Useful pattern:

- durable execution for long-running workflows;
- human-in-the-loop checkpoints;
- explicit state, memory, and resumable workflow design.

Do not add as a dependency in V0:

- the first slice can be deterministic Python/SQLite and repo scripts;
- LangGraph becomes useful once we have multi-step planning, approvals, retries, and workers.

What to borrow:

- workflow state model;
- pause/resume around approvals;
- persistent memory separation.

### MCP

Useful pattern:

- standard way to expose tools, data sources, and workflows to AI clients;
- good future boundary for CTOS tools so the same capability can be used from Codex, ChatGPT, or a local UI.

Do not expose broad local MCP servers yet:

- local MCP servers can become arbitrary-code execution surfaces if installed casually;
- CTOS needs explicit allowlists, stdio/local transport preference, and no secrets passthrough.

What to borrow:

- tool schemas and descriptions;
- resource/tool separation;
- consent and scope-minimization mindset.

### OpenAI Agents / Computer Use

Useful pattern:

- use an SDK when CTOS owns orchestration, tools, approvals, and state;
- computer-use style loops are valid for UI work when screenshots and actions are mediated by a harness.

Do not make this the V0 base:

- model/provider choice should remain a later ADR;
- computer use should run in an isolated browser, VM, or clearly bounded desktop harness, not directly over the whole operator session.

What to borrow:

- tool-first agent structure;
- explicit human review before high-impact actions;
- isolated UI harness when visual control is needed.

### Voice Stack

Candidates for later:

- wake word: `openWakeWord`;
- speech-to-text: `whisper.cpp`;
- text-to-speech: Piper or another maintained local TTS engine.

Do not implement always-on voice in V0:

- microphones create privacy and false-trigger risks;
- voice UX should sit on top of a proven text/tool assistant, not define the core.

### Push-To-Talk Voice Commands V1

Accepted 2026-07-07:

- real microphone commands are push-to-talk only;
- no always-on listener or wake word daemon;
- recordings are temporary by default and deleted after transcription;
- voice commands map only to Tier 0/Tier 1 intents:
  - CTOS brief/status;
  - agenda/day plan;
  - open or repair DESK;
  - open VMS panel;
  - show pending approvals;
  - show capability/help text.

Voice must not directly start/stop VMs, install packages, change firewall rules, sync mutable repo state, or run arbitrary shell commands. Those remain approval-queue or manual actions.

### Voice Backend V2 Runtime Bridge

Updated 2026-07-07:

- CTOS keeps Vosk push-to-talk as the live fallback while evaluating a more mature local voice stack.
- `ai/voice_intents_fr.json` is now the single catalog for safe French voice commands.
- `ai/voice_intents.py` provides deterministic matching for both `ctos-voice-v2` and the real
  `ctos-voice command` / `ctos-voice voice-command` runtime.
- The previous V1 hard-coded matcher remains as a compatibility fallback.
- This fixes the first weak spot seen in testing: `agenda` and nearby Vosk misrecognitions like
  `a jenda` now route to `ctos-ai plan-day`.
- `ctos-voice-v2 regression` is the first local harness for real voice samples: WAV files or
  known transcripts are checked against expected CTOS intents before changing the catalog.

## CTOS AI North Star

`ctos-ai` is a tool-governed assistant, not a root shell with a friendly voice.

The assistant should:

- converse with the operator;
- read CTOS repo context and cockpit state;
- maintain a local agenda and task memory;
- call named CTOS tools;
- help start/stop visible workflows;
- prepare commands for risky work instead of running them blindly;
- route heavy work to `ctos-core` or future workers when a worker contract exists.

The assistant should not:

- receive unrestricted shell/root access;
- store or copy secrets by default;
- scrape private app state without an explicit connector decision;
- operate third-party systems outside owned or explicitly authorized scopes;
- run persistent listeners before the security model is documented.

## Permission Tiers

Tier 0: read-only observation

- Read repo docs.
- Read cockpit status JSON.
- Read local/fleet status through existing scripts.
- Search CTOS context.

Tier 1: reversible local convenience

- Open local cockpit views.
- Open DESK/VMS/AI workspaces.
- Add agenda items.
- Draft a day plan.
- Generate commands for the operator to inspect.

Tier 2: CTOS-owned mutable actions with confirmation

- Start or shut down `ctos-kali`.
- Sync repo to `ctos-core`.
- Start a worker job.
- Edit CTOS config.
- Install packages.

Tier 3: privileged or hard-to-reverse actions

- `sudo` actions.
- Disk formatting.
- firewall changes.
- autologin/security posture changes.
- deleting state.

Tier 3 must be manual or require an explicit approval surface with exact command, target, and rollback note.

Tier 4: forbidden

- Credential theft or secret extraction.
- Stealth persistence.
- Evasion or destructive behavior.
- Unauthorized third-party access.
- Silent modification of logs, browser profiles, private keys, or VM disks.

## V0 Product Shape

V0 should be boring on purpose.

Components:

- `scripts/ctos-ai`: deterministic CLI/router first; no model dependency required.
- `scripts/ctos-agenda`: SQLite-backed agenda and planning helper.
- `ai/` or `control/ai_*`: shared Python modules if the script grows.
- `control/status.py` integration: expose agenda and AI readiness in `CTRL`.
- `AI` workspace: a terminal or local web panel for conversation and planning.

First tools:

- `status`: summarize T480, `ctos-core`, DESK, VMS, and Kali state.
- `search-context`: search `context/` and docs with `rg`.
- `agenda-add`: add a task/event/block.
- `agenda-list`: show today/upcoming.
- `plan-day`: produce a simple schedule from agenda items.
- `open-desk`: call the existing DESK recovery path.
- `open-vms`: open the VMS panel.

No LLM is required for this first tool contract. Once the CLI and storage are stable, the model layer can call those tools.

## Storage

V0 local state should start outside Git:

- T480 user state: `~/.local/share/ctos-ai/`.
- First database: `~/.local/share/ctos-ai/agenda.sqlite3`.
- No calendar secrets, API keys, browser state, voice recordings, or chat transcripts in the repo.

Future `ctos-core` service state can live under:

- `/srv/ctos/state/ai/`;
- `/srv/ctos/workers/queue`;
- `/srv/ctos/workers/{active,done,failed}`;
- `/srv/ctos/models/`.

Do not create long-lived AI services until a service/security ADR exists.

## Agenda V0

Agenda V0 is local and simple:

- tasks: title, notes, status, priority, estimate, due date;
- blocks: date, start, end, label, source task;
- recurring routines later;
- external calendars later only after a secrets/connectors decision.

The first planner can be deterministic:

- list fixed commitments first;
- place high-priority tasks into available blocks;
- leave explicit slack;
- output a plain text plan.

## Roadmap

V0: local tool contract and agenda

- deterministic CLI;
- SQLite agenda;
- context search;
- cockpit status integration;
- no background service.

V1: model-assisted operator

- one chat surface in `AI`;
- model can call Tier 0 and Tier 1 tools;
- Tier 2 produces an approval request, not direct execution;
- conversation summaries, not raw transcripts by default.

V2: worker orchestration

- `ctos-core` worker queue;
- model/runtime selection ADR;
- local model cache and cloud model split;
- job records under `/srv/ctos/workers`.

V3: computer use and voice

- isolated visual harness first;
- voice wake/transcribe/speak after text assistant is stable;
- no always-on microphone until privacy and false-trigger handling are explicit.

## Open Questions

- Which model provider powers V1: OpenAI API, local Ollama, hybrid, or Codex-facing tool bridge?
- Should `ctos-ai` expose MCP first, consume MCP first, or stay plain CLI until V1 is stable?
- What is the exact approval UX for Tier 2 actions?
- What personal data is allowed in agenda/memory?
- When should `ctos-core` run a persistent AI service rather than only scripts?
- Which calendar integration is acceptable after the secrets model is decided?

## Runtime Scan: GLM-5.2 And AirLLM

Checked on 2026-06-19.

GLM-5.2:

- Treat as a candidate external/frontier model for future long-context coding, agent planning, and deep reasoning.
- Do not treat as a local runtime target for current CTOS hardware. The public GLM-5.2 distribution is frontier-scale and the official repo presents it around large serving stacks, not a laptop/tower workstation footprint.
- If used later, CTOS should consume it through a provider profile with privacy notes, cost/latency notes, and the same tool approval boundary as any other model.

AirLLM:

- Treat as inspiration for layer-wise/disk-offloaded inference under tight VRAM.
- Do not select it as the V1 assistant runtime without a fresh local benchmark. Its public package/repo state is better suited to experiments than to the always-available Jarvis surface.
- It may become a future offline batch experiment on `ctos-core` service storage, not a dependency of the first interactive assistant.

Consequence:

Model power is not the current blocker. The current blocker is safe action authority: before attaching any strong model to CTOS tools, add an explicit approval surface for Tier 2 actions and keep Tier 3 manual.

## Next Implementation Slice

Completed on 2026-06-17:

1. Added `scripts/ctos-agenda` with a Python stdlib SQLite backend.
2. Added `scripts/ctos-ai` with deterministic commands: `status`, `search-context`, `agenda`, `plan-day`, `open-desk`, and `open-vms`.
3. Added narrow verification: Python compile, empty DB creation, sample agenda item, JSON list, and plan rendering with a temporary DB.
4. Added read-only cockpit status for tool availability, agenda counts, DB metadata, and deferred model runtime.

Completed on 2026-06-18:

1. Added `scripts/ctos-ai brief` as the first operator-facing Jarvis-like entrypoint.
2. The brief reads the control snapshot, agenda state, `ctos-core`, Kali state, and battery/RAM/load, then emits a deterministic next recommendation.
3. Verified with a temporary agenda DB and with live host access: `ctos-core` was visible, Kali reported `shut off`, and the empty real agenda recommended adding one concrete task.
4. Added `scripts/ctos-install-user-bin` and installed user-local command shims under `~/.local/bin`, so `ctos-ai brief` and `ctos-agenda` work from a normal terminal without `cd ~/T480`.

Completed on 2026-06-19:

1. `ctos-ai` with no subcommand now defaults to `brief`, making the shortest operator command useful.
2. Help remains available with `ctos-ai -h`; agenda management still stays explicit through `ctos-agenda` or `ctos-ai agenda ...`.
3. Added the first local approval surface: `ctos-ai actions`, `propose`, `approvals`, `show`, `approve`, and `reject`.
4. The approval queue is allowlist-only and stored outside Git at `~/.local/share/ctos-ai/approvals.sqlite3` unless `CTOS_AI_APPROVAL_DB` overrides it.
5. First allowlisted actions are `kali-start`, `kali-shutdown`, `kali-console`, `kali-checkpoint`, `core-sync-repo`, and `core-apply-layout`.
6. Surfaced pending approvals in `CTRL`: the status snapshot exposes read-only approval counts and recent pending records; the terminal cockpit and web dashboard render that state without adding an execute button.
7. Added inert provider/runtime profiles in `ai/runtime_profiles.json` and exposed them through `ctos-ai runtimes`, `ctos-ai runtime <id>`, and `ctos-ai runtime-recommend`.
8. First profiles are OpenAI Responses API, Ollama on `ctos-core`, llama.cpp server on `ctos-core`, GLM-5.2 external/provider, and AirLLM offload experiment.
9. `CTRL` now renders runtime profile count and active profile; `ctos-ai brief` reports profile count while keeping `active_profile` unset.
10. Added `ctos-ai runtime-check <id>` as a no-network-by-default dry-run adapter. It validates runtime metadata, endpoint shape, secret env names, and optional owned `ctos-core` readiness without sending model prompts or private context.
11. Added `ai/benchmarks/ollama_core_local_v0.json` and `ctos-ollama-bench` for the first local Ollama benchmark path. The plan is CPU-safe, localhost-only, stores models under `/srv/ctos/models/ollama`, and keeps package install, model pull, and benchmark execution explicit.

Completed on 2026-06-21:

1. Installed `ollama 0.30.8-1` on `ctos-core` through the interactive helper path after the operator entered the local sudo password.
2. Confirmed `ollama.service` active/enabled, bound to `127.0.0.1:11434`, with model cache under `/srv/ctos/models/ollama`.
3. Pulled and benchmarked `qwen2.5-coder:0.5b` as the first smoke model. All benchmark prompts completed; the non-trivial prompts generated at about 35 tokens/s after load.
4. Added `ctos-ai ask-local` as the first bounded model-backed command. It sends only the explicit prompt to the local Ollama runtime and does not expose tools, files, memory, or shell access.
5. Live proof returned `CTOS_LOCAL_OK` through `qwen2.5-coder:0.5b`; `ollama-core-local` is now `ready` / `bounded_call_verified` while keeping `active_profile` unset.
6. Pulled and benchmarked `qwen2.5-coder:1.5b`. It completed all prompts and is available through `ctos-ai ask-local --model qwen2.5-coder:1.5b`, but measured around 16 tokens/s on non-trivial prompts versus about 35 tokens/s for 0.5B.

Next:

1. Design the V1 chat/CLI surface before selecting an active backend.
2. Define the first routing policy: 0.5B for fast checks, 1.5B for deliberate coding/ops prompts, external models only after secrets/privacy policy.
3. Keep external providers blocked until API-key handling, privacy boundaries, and cost controls are documented.

## CTOS AI Loop Methodology

Added on 2026-06-23.

The assistant must be built as small durable loops, not as an ever-growing prompt stack.

Each loop has six steps:

1. Observe the real machine state with a command or a narrow status file.
2. State the smallest hypothesis being tested.
3. Make one durable repo/script/config change.
4. Verify with a real command and capture the observable result.
5. Record the decision, blocker, or next loop in `context/`.
6. Keep any model authority at the lowest useful tier.

Initial loop classes:

- Identity loop: ensure the local model always knows it is `CTOS Local`, not a cloud model or an autonomous operator.
- Runtime loop: keep Ollama localhost-only, benchmark models, and route fast/slow prompts deliberately.
- API loop: expose a small localhost API before building visual or voice UX.
- Voice loop: start with typed input plus spoken output; add speech-to-text only after a backend is verified.
- Tool-authority loop: read-only first, Tier 2 approval queue second, no arbitrary shell from model output.

V1 boundary:

CTOS Local may answer prompts, summarize status, and route tiny read-only commands. It must not launch arbitrary processes, mutate files, operate the desktop, or keep private memory through model output alone.

## Local API And Voice V1 Slice

Started on 2026-06-23.

Planned implementation:

1. Add a default CTOS identity contract to `ctos-ai ask-local`.
2. Add a localhost Ollama tunnel helper for fast repeated calls.
3. Add a stdlib HTTP API on `127.0.0.1:8767` with `GET /health` and `POST /ask`.
4. Add `ctos-voice` as a bounded voice wrapper: typed input, spoken output, and read-only command intents.
5. Keep speech-to-text blocked until a local backend is chosen and tested.

Completed on 2026-06-23:

1. `ctos-ai ask-local` now applies a default CTOS identity contract, with `--raw-model` reserved for diagnostics.
2. `ctos-ai-tunnel ensure` opens a detached localhost-only SSH tunnel: `127.0.0.1:11435 -> ctos-core:127.0.0.1:11434`.
3. `ctos-ai-api health` verified Ollama `0.30.8` and both cached models through the tunnel.
4. `ctos-ai-api ask` returned `CTOS_API_OK` through the fast tunnel path.
5. `ctos-ai-api serve --port 8767` answered `GET /health` during a short start/curl/stop test.
6. `ctos-voice probe` found local TTS and recorder commands but no verified STT backend.
7. `ctos-voice ask --no-speak --model qwen2.5-coder:1.5b` returned `CTOS_VOICE_OK`.
8. `ctos-voice command --no-speak brief` displayed the read-only CTOS brief without launching mutable actions.

Extended on 2026-06-23:

1. Added `POST /chat` to the local API for message-list based chat calls.
2. Added `ctos-ai-api-server start|status|stop` to keep the API available as a detached local process.
3. Added `ctos-ai-chat` as the first operator chat loop with in-memory-only history.
4. Added `ctos-voice chat` to route the chat loop through the voice wrapper; STT is still blocked, but replies can be spoken.
5. Live proof: `ctos-ai-chat --model qwen2.5-coder:1.5b ...` returned `CTOS_CHAT_OK`.
6. Live proof: `ctos-voice chat --no-speak --model qwen2.5-coder:1.5b ...` returned `CTOS_VOICE_CHAT_OK`.

Current boundary:

The system has a first text/API/chat/voice-output loop. It does not yet have live speech-to-text, wake word, autonomous tool calls, or persistent memory.

## Voice Input V1: Vosk Push-To-Talk

Added on 2026-06-23.

Decision:

Use local Vosk with `vosk-model-small-fr-0.22` as the first speech-to-text backend.

Why:

- offline and local;
- small enough for short commands on T480-class hardware;
- available through Arch packages as `python-vosk` and `vosk-api`;
- official Vosk model page lists the French small model directly.

Boundary:

- no always-on microphone;
- no wake word;
- no cloud STT;
- no persistent recordings by default;
- no arbitrary command execution from speech.

Commands:

1. `ctos-voice setup-vosk --print-commands` prints the package/model setup.
2. `ctos-voice setup-vosk --yes` installs `python-vosk`/`vosk-api` and downloads the model under `~/.local/share/ctos-ai/stt/`.
3. `ctos-voice probe` verifies module, model, recorder, and TTS readiness.
4. `ctos-voice record-once --seconds 3 --out /tmp/ctos.wav` records a short sample.
5. `ctos-voice transcribe-file /tmp/ctos.wav` transcribes a WAV.
6. `ctos-voice listen-once --seconds 4` records one prompt, transcribes it, asks CTOS Local, speaks the response, and deletes the temp WAV.
7. `ctos-voice voice-command --seconds 3` maps one phrase only to read-only `brief/status/agenda` intents.

Verification so far:

- `python3 -m py_compile scripts/ctos-voice` passed.
- `ctos-voice probe --json` correctly reports recorder/TTS availability and missing Vosk/model readiness before install.
- Official Vosk model listing was checked with approved `curl`; the French section contains `vosk-model-small-fr-0.22.zip`.
- `ctos-voice setup-vosk --model-only --yes` downloaded the French small model to `~/.local/share/ctos-ai/stt/vosk-model-small-fr-0.22`; `ctos-voice probe` now reports `model_ready=true`.
- `ctos-voice setup-vosk --venv --yes` installed PyPI `vosk 0.3.45` into `~/.local/share/ctos-ai/venvs/vosk` without sudo; `ctos-voice probe` now reports `voice_input_ready=true`.
- `ctos-voice transcribe-file` transcribed a synthetic French WAV.
- `ctos-voice listen-once --from-wav ... --no-speak` completed the STT-to-CTOS model loop.
- `ctos-voice record-once --seconds 1` produced a valid microphone WAV.
- `ctos-voice voice-command --from-wav ... --no-speak` triggered the read-only CTOS brief command.

Current state:

The V1 voice loop is usable as push-to-talk. Quality still depends on the microphone and the small French Vosk model, so longer dictation remains a future Whisper/Piper-quality pass rather than a V1 blocker.

## Voice Backend V2 Spike

Added on 2026-07-07.

The operator tested real voice and hit the expected V1 limit: command recognition quality will not scale if CTOS keeps extending Vosk with manual phrase guesses. The V2 direction is now recorded separately in `context/21_ctos_voice_backend_v2.md`.

Implementation artifacts:

1. `ai/voice_backends.json`: inert backend registry for Home Assistant Assist/Wyoming, Speech-to-Phrase, Piper, Whisper-class dictation, OpenVoiceOS, and Leon.
2. `ai/voice_intents_fr.json`: CTOS-owned French intent catalog for the current safe commands.
3. `docs/VOICE_BACKEND_V2.md`: operator runbook.
4. `scripts/ctos-voice-v2`: planning/status/intent helper.
5. `ctos-voice-v2 match`, `sample-plan`, `regression`, and `export-phrases`: deterministic intent regression and backend handoff tools.

Boundary:

- Vosk push-to-talk V1 remains the fallback.
- Speech-to-Phrase-style fixed intent recognition is the next practical spike.
- Home Assistant Assist/Wyoming is the mature ecosystem target, not an immediate blind install.
- Piper-quality TTS comes after intent recognition is reliable.
- Always-on microphone, cloud STT, and direct mutable voice actions remain blocked.
