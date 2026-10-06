# CTOS AI Runtime Profiles

This directory stores declarative AI runtime/provider profiles for CTOS.

The profiles are intentionally inert:

- no API keys;
- no model downloads;
- no package install decisions;
- no daemon or service activation;
- no personal context routing.

`scripts/ctos-ai runtimes` reads `runtime_profiles.json` so the cockpit can show candidate model backends before CTOS commits to one. A profile becoming `active_profile` requires a separate decision log entry, verification, and an explicit secrets/privacy boundary if it uses an external provider.

Dry-run checks:

- `ctos-ai runtime-check <id>` validates profile metadata, endpoint shape, declared secret environment variables, and readiness labels.
- The default check must not contact an external endpoint or a model runtime.
- `ctos-ai runtime-check <id> --target-probe` may probe owned CTOS nodes such as `ctos-core` for reachability and storage readiness.
- Secret values are never printed; only variable names and present/missing state are shown.

Ollama benchmark:

- `ai/benchmarks/ollama_core_local_v0.json` is the first local benchmark plan.
- `ctos-ollama-bench plan` shows the package, service, model, prompt, and metric plan.
- `ctos-ollama-bench preflight` is read-only and checks `ctos-core` readiness.
- `ctos-ollama-bench install`, `pull`, and `bench` all require explicit `--yes`.
- `ctos-ollama-bench install-interactive --yes` is the preferred first install path while
  `ctos-core` still requires a local sudo password; run it from a visible T480 terminal.
- The benchmark service plan binds Ollama to `127.0.0.1:11434` on `ctos-core`; it is not a LAN service.

Bounded local ask:

- `ctos-ai ask-local "prompt"` sends exactly that prompt to the local Ollama API on `ctos-core`
  through SSH.
- It does not expose CTOS tools, shell access, files, screenshots, or durable memory to the model.
- A CTOS identity contract is added by default so the local model does not claim to be a cloud
  model or an autonomous operator. Use `--raw-model` only for diagnostics.
- The current default smoke model is `qwen2.5-coder:0.5b`.
- `qwen2.5-coder:1.5b` is also available for slower deliberate checks:
  `ctos-ai ask-local --model qwen2.5-coder:1.5b "prompt"`.
- Use `--stats` for quick token/s feedback and `--json` for raw timing metadata.

Shared action planner:

- `ctos-ai route-text "agenda"` routes typed text or a future STT transcript through the CTOS
  action planner without executing mutable actions.
- `ctos-ai route-text --execute-safe "agenda"` executes only Tier 0/Tier 1 commands owned by
  `ctos-ai`; unmatched or mutable requests are refused.
- `ctos-voice command ...` now uses the same planner module, so Vosk, Speech-to-Phrase, Whisper,
  and typed text can converge on one permission boundary.
- Natural-language requests that do not match the deterministic catalog are kept as transcript
  text until the open-ended Jarvis parser/approval loop exists.

Permissioned agenda parser:

- `ctos-ai agenda-propose "ajoute acheter du lait demain 30 min priorité 4"` parses a natural
  French agenda request and prints the exact `ctos-agenda add ...` command.
- It writes nothing by default.
- `ctos-ai agenda-propose "...request..." --save --source voice` stores a pending proposal in
  the local CTOS approval DB without writing agenda state.
- `ctos-ai agenda-review` shows the latest pending proposal plus the exact confirm/reject
  commands.
- `ctos-ai agenda-proposals`, `ctos-ai agenda-show latest`, `ctos-ai agenda-confirm latest --yes`,
  and `ctos-ai agenda-reject latest` manage those saved proposals.
- `ctos-ai agenda-propose "...request..." --commit --yes` writes only the reviewed proposal.
- Use `CTOS_AI_DB=/tmp/test.sqlite3` while testing so the real user agenda is not touched.

Fast local API:

- `ctos-ai-tunnel ensure` opens a localhost-only SSH tunnel from `127.0.0.1:11435` on the T480
  to `ctos-core:127.0.0.1:11434`.
- `ctos-ai-api health` checks that tunnel and lists the local Ollama models.
- `ctos-ai-api ask "prompt"` uses the tunnel directly, avoiding a fresh SSH/Ollama setup per
  call.
- `ctos-ai-api serve` exposes `GET /health`, `POST /ask`, and `POST /chat` on
  `127.0.0.1:8767` for local UI/voice/chat clients.
- `ctos-ai-api-server start|status|stop` manages that HTTP API as a detached local process.
- `ctos-ai-chat` is the first local chat loop. It uses in-memory conversation history only; it
  does not persist transcripts by default.

Cheap/free lane:

- `ctos-ai cheap-lane` shows the current low-cost AI lane without installing anything.
- `ctos-ai cheap-plan --tool aider` prints the Aider trial path while keeping package install,
  external provider routing, and private repo context out of scope.
- `ctos-ai code-draft "request"` sends only the explicit request to the bounded local Ollama
  model and produces a short draft. It does not read files, inspect git state, execute commands,
  or edit the repo.
- Aider, 9Router, and Agent-Reach are recorded as candidate profiles only. Aider is a possible
  coding client; 9Router is an optional external router/proxy; Agent-Reach is a read/search
  capability layer. None of them is an active CTOS authority.

Voice V1:

- `ctos-voice probe` reports available local TTS, recorders, and speech-to-text backends.
- `ctos-voice ask "prompt"` sends typed text to CTOS Local and speaks the response when local TTS
  is available.
- `ctos-voice chat` starts the same in-memory chat loop with spoken replies by default.
- `ctos-voice command "brief"` and `ctos-voice command "agenda"` are tiny read-only intent tests.
- `ctos-voice command "propositions agenda"` shows pending agenda proposals; it does not confirm
  or reject them.
- `ctos-voice route "ajoute acheter du lait demain"` sends typed transcript text through the
  same CTOS planner and prints any agenda proposal without writing it.
- `ctos-voice route "ajoute acheter du lait demain" --save-agenda` stores a pending agenda
  proposal for later review with `ctos-ai agenda-confirm latest --yes`.
- Vosk small French is the first selected local STT backend for push-to-talk voice input.
- `ctos-voice setup-vosk --print-commands` shows the exact package/model setup commands.
- `ctos-voice setup-vosk --yes` installs `python-vosk`/`vosk-api` from pacman when missing and downloads
  `vosk-model-small-fr-0.22` into `~/.local/share/ctos-ai/stt/`; the model is not stored in Git.
- `ctos-voice setup-vosk --model-only --yes` downloads/extracts only the model. This is useful
  when the package install still needs a visible sudo password prompt.
- `ctos-voice setup-vosk --venv --yes` installs Python Vosk into the local user venv
  `~/.local/share/ctos-ai/venvs/vosk` when pacman/sudo is not practical.
- `ctos-voice record-once --seconds 3 --out /tmp/ctos.wav` records a short mono WAV sample.
- `ctos-voice transcribe-file /tmp/ctos.wav` transcribes a WAV with the local Vosk model.
- `ctos-voice listen-once --seconds 4` records, transcribes, asks CTOS Local, speaks the answer,
  and deletes the temporary recording by default.
- `ctos-voice listen-once --from-wav /tmp/ctos.wav --no-speak` is the deterministic debug path
  for a pre-recorded sample.
- `ctos-voice voice-command --seconds 3` records one phrase and maps it through the CTOS-owned
  safe intent catalog in `ai/voice_intents_fr.json`, with the old V1 hard-coded matcher kept as
  fallback.
- `ctos-voice route-once --seconds 4` records one phrase and routes the transcript through the
  planner. It is the safer natural-language Jarvis debug path: agenda-like phrases produce a
  proposal, and `--execute-safe` still refuses mutable writes.
- `ctos-voice route-once --seconds 4 --save-agenda` keeps the same push-to-talk privacy model,
  deletes the temporary audio by default, and stores only the recognized agenda proposal.
- Always-on microphone and wake-word listening remain out of scope.

Voice-to-Codex read-only boundary:

- `ai/voice_task_spec.schema.json` and
  `ai/codex_readonly_result.schema.json` are closed, bounded schemas. The
  matching deterministic validator in `ai/voice_task_spec.py` rejects unknown,
  raw transcript/audio, arbitrary command, secret-like, unresolved, or
  out-of-workspace content.
- `ai/voice_task_compiler.py` uses only the loopback Ollama API and treats its
  structured result as untrusted. Explicit repository file names are a hard
  deterministic scope ceiling even if the small model suggests broader paths.
- `ctos-codex-voice validate ai/examples/voice_task_readonly_smoke.json`
  validates and canonicalizes without starting Codex.
- `ctos-codex-voice plan ai/examples/voice_task_readonly_smoke.json` prints the
  exact read-only, ephemeral Codex arguments, canonical spec, and digest without
  starting Codex.
- `ctos-codex-voice run ... --yes` is the separate live cloud action. It sends
  only a fixed instruction and revalidated canonical spec over stdin, requires
  structured output, ignores user config/automatic project instructions,
  disables web search, and never falls back to Ollama. Read-only prevents
  writes, not disclosure: `allowed_scope` is an explicit agent constraint but
  not an OS-enforced per-file read jail over the workspace.
- The Voice Console Codex mode creates an editable preview first, keeps only a
  digest/expiry token in memory, and never implicitly executes Codex. Its live
  run endpoint is disabled unless the server is deliberately started with
  `CTOS_VOICE_CODEX_RUN_ENABLED=1` after informed external-disclosure approval.
- `ctos-voice render-wav --engine piper --output /tmp/result.wav --stdin`
  renders without local playback. The Voice Console uses that path to return a
  bounded `audio/wav` response for playback on the EliteBook and deletes its
  temporary file.
- Raw browser audio is deleted by default; raw transcripts are neither returned
  in Codex mode nor placed in the reviewed spec. Do not enable audio retention
  during normal operation.

Voice Backend V2 spike:

- `ai/jarvis_stack.json` records the selected hybrid Jarvis stack: mature local voice
  components plus CTOS as the action/approval boundary.
- `ctos-jarvis stack` renders that selection for daily operator use.
- `ai/voice_backends.json` records candidate voice backends and CTOS constraints.
- `ai/voice_intents_fr.json` is the CTOS-owned French intent catalog for safe commands.
- `ai/voice_intents.py` is the shared deterministic matcher used by `ctos-voice` and
  `ctos-voice-v2`.
- `ai/action_planner.py` turns typed or transcribed text into a CTOS action plan and safe execution
  decision. It is the boundary that the mature voice stack will feed.
- `ctos-voice-v2 plan` shows the selected direction: Home Assistant Assist/Wyoming ecosystem,
  Speech-to-Phrase-style fixed command recognition, installed Piper TTS, and Vosk V1 as fallback.
- `ctos-voice-v2 status` validates the registry and checks local voice/tool readiness.
- `ctos-voice-v2 doctor` summarizes the live voice stack and prints the next concrete action.
- `ctos-voice-v2 stp-transcribe --target-tunnel --record-seconds 3 --route` runs the first
  Speech-to-Phrase/Wyoming one-shot test once Home Assistant readiness and the STP container are
  green.
- `ctos-voice-v2 wyoming-selftest` runs a localhost-only mock Wyoming transport test and routes
  the fixed transcript through CTOS; it does not test real speech recognition.
- `ctos-voice-v2 intents` prints the current safe intent catalog.
- `ctos-voice-v2 match "agenda"` tests a recognized phrase against the safe intent catalog.
- `ctos-voice-v2 export-phrases --format jsonl` emits phrase rows for a future backend adapter.
- `ctos-voice-v2 sample-plan --dir /tmp/ctos-voice-samples --write-manifest` prints and stores
  the temporary sample plan for real voice tests.
- `ctos-voice-v2 regression --dir /tmp/ctos-voice-samples` transcribes WAV samples and checks
  expected intents.
- `ctos-voice-v2 next-commands` prints the next manual tests without installing any daemon.
- `ctos-voice command --no-speak agenda` uses the same catalog in the real runtime path.
