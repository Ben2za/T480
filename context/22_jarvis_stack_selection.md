# CTOS Jarvis Stack Selection

Date: 2026-07-07

Refresh: 2026-07-18

## Decision

Do not build the Jarvis target by tuning one missed spoken word at a time.
The selected path is a hybrid local stack:

- mature local voice components for capture, STT, TTS, wake/satellite work later;
- CTOS as the only action, approval, and audit boundary;
- `ctos-core` as the heavier runtime host;
- the T480 as the operator and bastion.

## Current Product Path

Use `ctos-jarvis` as the daily operator surface.

The immediate usable POC is:

```bash
ctos-jarvis mature-plan
ctos-jarvis mature-check
ctos-jarvis status
ctos-jarvis calibrate
ctos-jarvis calibrate --save-agenda
ctos-jarvis run
ctos-jarvis improve
ctos-jarvis collect-next
ctos-jarvis collect
ctos-jarvis corpus
ctos-jarvis triage
ctos-jarvis evaluate
ctos-jarvis evaluate --backend both
ctos-jarvis sample "ajoute acheter du pain demain"
ctos-jarvis samples
ctos-jarvis regression
ctos-jarvis regression --backend open-stt --target-tunnel
ctos-jarvis session --save-agenda
ctos-jarvis review
ctos-jarvis confirm latest --yes
```

This is intentionally narrow. A natural French request can become a pending
agenda proposal, but it cannot write agenda state until a typed confirmation is
given.

`ctos-jarvis mature-plan` is the durable answer to the operator concern that
word-by-word tuning would take months. It explicitly selects a mature
open-source/local substrate now while keeping CTOS as the product layer:
Home Assistant/Wyoming for the voice bus, Wyoming Whisper/faster-whisper for
natural French STT, Speech-to-Phrase for fixed commands, Piper for local TTS,
and Ollama on `ctos-core` for local model work. Piper is now installed and
ready on the T480. Open Interpreter/01,
OpenVoiceOS, GLM-family models, and AirLLM-style offload remain reference or
sandbox tracks until they fit behind CTOS proposal/approval boundaries.

The 2026-07-08 refresh keeps the same decision. A missed word such as `agenda`
is not a reason to grow a synonym list forever. It is a reason to capture a
small reusable corpus, measure it against the local fallback and the
Whisper/Wyoming rail, and move the daily operator path toward a mature STT/TTS
substrate. CTOS should still own action schemas, agenda writes, desktop/VM
control, and typed approval.

`ctos-jarvis mature-check` is the matching read-only readiness command. It
checks the current local Jarvis/voice foundation, audio controls, and reusable
sample manifest, then prints the next command. `--full` includes `ctos-core`
backend probes. It does not install packages, start long-lived services, keep
the microphone open, or write agenda state.

Use `ctos-jarvis status` when the operator needs one short current-state view.
It combines mature readiness, corpus/improvement state, the next capture
phrase, and pending agenda proposal count, then prints one next action. It is
read-only.

Use `ctos-jarvis improve` as the normal "advance the voice stack" command. It
turns the current corpus state into one safe next step: collect when the corpus
is missing/incomplete, evaluate both backends when ready, or inspect samples
when repair is needed. Without `--run` it only prints the command. With `--run`
it executes that selected step, still behind the existing preflight and CTOS
boundaries.

Use `ctos-jarvis collect-next` when live corpus capture should move one phrase
at a time. It selects the next missing or weak phrase from the preset and
records only that phrase when run with `--run`.

Use `ctos-jarvis sample "..."` when live recognition misses a useful word such
as `agenda`. It stores reusable labeled WAVs outside the repo so the same human
audio can be replayed while changing STT backends or capture settings. This
keeps the work from becoming a long synonym-tuning loop. The sample manifest
uses `expected_text` for natural French transcript checks and optional
`intent_id` for fixed CTOS command regression.

Use `ctos-jarvis collect` before deeper backend work. It captures a compact
operator corpus with the default `core` preset: the key commands `agenda`,
`brief`, `ouvre desk`, `ouvre vms`, plus one natural agenda request. This makes
missed recognition reproducible across Vosk, open-STT/Wyoming, Speech-to-Phrase,
or a later local model-assisted parser. It now runs a read-only audio preflight
before recording so obvious speaker/microphone control failures are visible
before the operator captures the suite. The preflight warns by default, can be
made blocking with `--strict-preflight`, and can be skipped with
`--no-preflight` for debugging.

Use `ctos-jarvis corpus` after collection. It is the read-only gate that reports
whether the corpus is empty, incomplete, broken by missing files, or ready for
regression. It does not record audio or start a backend.

Use `ctos-jarvis triage` when the operator needs the next concrete action from
the current corpus state. It wraps the read-only corpus and sample checks into a
single verdict without recording, transcribing, starting services, or mutating
agenda state.

Use `ctos-jarvis evaluate` after the corpus is collected. It runs the corpus
gate first, refuses to test empty/broken samples, and only then launches
regression. `--backend both` compares local fallback recognition and the
open-STT/Wyoming rail from the same reusable samples.

Use `ctos-jarvis samples` to inspect the current reusable sample manifest, and
`ctos-jarvis regression` to replay that default manifest without copying the
long state path. Add `--backend open-stt --target-tunnel` to score the same WAVs
against the current Wyoming/Whisper rail on `ctos-core`.

## Selected Stack

| Layer | Choice | Status | Why |
| --- | --- | --- | --- |
| Operator facade | `ctos-jarvis` | Active | One human command surface without new authority. |
| Voice bus | Home Assistant Assist + Wyoming | Primary ecosystem target | Best fit for local voice services, custom sentences, and future satellites. |
| Fixed commands | Speech-to-Phrase through Wyoming | Token-gated | Deterministic command rail for known CTOS intents. |
| Open-ended STT | Wyoming Whisper / faster-whisper | Smoke candidate selected | Better fit for natural French requests than phrase matching. |
| TTS | Piper / Wyoming Piper | Installed and ready on T480 | Current local French output; benchmark before changing or upgrading it. |
| Model runtime | Ollama on `ctos-core` first | Installed smoke runtime | Simple local model host before larger RAM/GPU upgrades. |
| Computer control | CTOS proposals and approvals | Mandatory | No assistant stack gets direct shell/system authority. |

## Candidates Not Selected As Primary Runtime

- OpenVoiceOS: useful full-assistant and skills reference; too broad as the
  immediate CTOS runtime.
- Leon: useful personal-assistant product reference; not aligned with the
  current Python/EndeavourOS CTOS tooling.
- Open Interpreter / 01-style agents: useful inspiration for computer-control
  UX, but too powerful to run unattended against CTOS machines.
- GLM-5.2 / GLM-family models: future frontier or expanded-hardware model
  research only; no GLM 5.x runtime is selected for this hardware pass.
- AirLLM-style offload: interesting constrained-inference experiment; not the
  first Jarvis runtime.

## Safety Boundary

Voice, STT, TTS, and model runtimes are input/output adapters. CTOS owns:

- intent classification;
- agenda proposals;
- action schemas;
- typed confirmation;
- VM/system command boundaries;
- audit docs and reproducible scripts.

No transcript or model response may execute shell, install packages, change
firewall rules, start/stop VMs, approve agenda writes, or mutate desktop state
without a CTOS-owned proposal/approval path.

## Next Work

1. Define the validated, transcript-free task-spec boundary before any direct
   `codex exec` integration.
2. Run one live `ctos-jarvis calibrate` test with a natural agenda phrase.
3. Use `ctos-jarvis run` as the daily loop once the transcript shape is readable.
4. Save failed/important phrases with `ctos-jarvis sample` so later STT tests
   are repeatable.
5. If repeated diagnostics are needed, use `ctos-jarvis session` to keep open-STT warm between attempts.
6. If the staged proposal is correct, review and confirm typed.
7. If transcription is weak, fix audio capture and preprocessing before adding
   more phrase synonyms.
8. Keep Home Assistant/Speech-to-Phrase token onboarding as the deterministic
   rail, not the only Jarvis path.
9. Add richer CTOS proposal schemas only after agenda proves useful.
10. Defer wake word and always-on listening until privacy, false positives, and
   action gating are stronger.

## Latest Verification

2026-07-18:

- Live Piper probe reports `piper-tts 1.4.2` and
  `fr_FR-siwis-medium` ready; registry entries that still said `planned` were
  corrected without upgrading the runtime.
- Live full Jarvis status reports T480 audio ready, no human sample corpus,
  Home Assistant and Speech-to-Phrase containers missing, and the open-STT
  image/path present but stopped.
- The voice-to-Codex intake selected direct supported `codex exec` behind a
  validated spec-only boundary. Current `codex_handoff()` remains printable
  raw text and must not be wired directly to execution.

2026-07-08:

- `ctos-audio doctor [--json]` reports structured output/microphone readiness
  without changing audio settings.
- `ctos-jarvis mature-check --json` now reports restricted PipeWire/DBus access
  as an execution-context warning instead of a generic audio failure.
- In the restricted Codex context, audio doctor reports `pipewire_context_denied`;
  in the live desktop context it reported output 77% and microphone 20%.
- `ctos-jarvis status` still points to the next real Jarvis action:
  `ctos-jarvis collect-next --run`.
- `ctos-jarvis bootstrap` now wraps the current status/next-action path: plan by
  default, one existing command with `--run`, then status recheck.

2026-07-07:

- `ctos-jarvis mature-plan`, `ctos-jarvis mature-plan --commands`, and
  `ctos-jarvis mature-plan --json` render the open-source adoption path from
  `ai/jarvis_stack.json`.
- `ctos-jarvis mature-check` and `ctos-jarvis mature-check --json` render a
  read-only local readiness report and next action for the same mature path.
- `ctos-jarvis smoke` still passes the local non-destructive Jarvis checks
  after adding the mature-plan surface.
- `ctos-jarvis stack`, `ctos-jarvis stack --json`, and `ctos-jarvis stack --verbose` render the
  selected stack from `ai/jarvis_stack.json`.
- `ctos-voice-v2 open-stt start` now waits for `Ready` in container logs before returning.
- A synthetic French WAV reached the open-STT backend through `ctos-jarvis calibrate --from-wav`.
- The synthetic transcript was speech-like but still degraded and produced no agenda proposal,
  so it proves transport/readiness only.
- `ctos-voice-v2 open-stt status --json` confirmed the temporary container stopped and port
  `10301` was free.
- `ctos-jarvis sample --help`, `ctos-jarvis sample "..." --plan`, and a `/tmp`
  imported WAV sample verified the reusable sample manifest path without writing
  audio into the repo.
- `ctos-jarvis collect --help` and `ctos-jarvis collect --plan` verified the
  guided corpus path without recording audio; `ctos-jarvis mature-check --json`
  now recommends `ctos-jarvis collect` when the reusable sample manifest is
  empty.
- `ctos-jarvis corpus --json` verified the empty-corpus gate, and a temporary
  manifest verified the ready-state path without recording live audio.

## Sources

- Home Assistant voice control: https://www.home-assistant.io/voice_control/
- Home Assistant local voice assistant: https://www.home-assistant.io/voice_control/voice_remote_local_assistant/
- Home Assistant Wyoming integration: https://www.home-assistant.io/integrations/wyoming/
- Wyoming protocol: https://github.com/rhasspy/wyoming
- Speech-to-Phrase: https://github.com/OHF-Voice/speech-to-phrase
- Wyoming faster-whisper: https://github.com/rhasspy/wyoming-faster-whisper
- Wyoming Whisper container: https://hub.docker.com/r/rhasspy/wyoming-whisper
- Wyoming Piper: https://github.com/rhasspy/wyoming-piper
- OpenVoiceOS core: https://github.com/OpenVoiceOS/ovos-core
- Open Interpreter 01: https://github.com/OpenInterpreter/01
- AirLLM reference implementation: https://github.com/lyogavin/Anima/tree/main/air_llm
- GLM-5.2 / GLM-family lookup: https://github.com/zai-org/GLM-5
