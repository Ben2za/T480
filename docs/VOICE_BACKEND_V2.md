# CTOS Voice Backend V2

Date: 2026-07-07

This runbook defines the next voice direction after the Vosk push-to-talk V1.

## Problem

V1 proves that the microphone, local TTS, Vosk, and CTOS command routing work. It is not strong enough to become the long-term "Jarvis" interface:

- Vosk small French is light, but phrase recognition is fragile.
- Expanding synonyms manually will not scale.
- A mature assistant needs clearer TTS, better intent recognition, and later wake/satellite support.
- CTOS must still keep action authority explicit and reviewable.

## Direction

Use a mature local voice stack for voice I/O, while CTOS remains the action/security layer.

Primary spike:

- Home Assistant Assist / Wyoming as the mature local voice-assistant ecosystem.
- Speech-to-Phrase for fixed CTOS command recognition.
- Piper or Wyoming Piper for clearer local TTS.
- Whisper-class dictation later, only for explicit long-form conversation/dictation.

Deferred:

- always-on wake word;
- cloud STT;
- direct voice execution of Tier 2/Tier 3 actions;
- OpenVoiceOS/Leon as primary runtime.

## CTOS Boundary

Voice V2 may identify intents. CTOS decides what the intent is allowed to do.

Allowed without approval:

- read CTOS brief/status;
- show agenda/day plan;
- open or repair DESK;
- open VMS panel;
- list approvals/capabilities.

Not allowed directly from voice:

- start/stop VMs;
- install packages;
- edit firewall/network rules;
- sync repo state;
- run arbitrary shell commands;
- keep private transcripts by default.

## Placement

Current preferred shape:

- T480: microphone, push-to-talk launcher, bastion, CTOS command execution.
- `ctos-core`: heavier voice/model services after install path is decided.

This keeps the current network model intact: `ctos-core` remains behind the T480 bastion until its uplink is deliberately changed.

## Repo Artifacts

- `ai/voice_backends.json`: backend registry and constraints.
- `ai/voice_intents_fr.json`: CTOS-owned French intent catalog.
- `ai/voice_intents.py`: shared deterministic intent matcher used by both helpers and runtime.
- `scripts/ctos-voice-v2`: helper for plan/status/intent handoff.
- `scripts/ctos-voice`: current V1 push-to-talk runtime; it now consumes the V2 catalog first and keeps the old V1 matching as compatibility fallback.

## Operator Commands

Inspect the V2 plan:

```bash
ctos-voice-v2 plan
```

Inspect local readiness:

```bash
ctos-voice-v2 status
```

Summarize the live stack and the next concrete action:

```bash
ctos-voice-v2 doctor
```

`doctor` is the fastest operator check before working on voice. It verifies the local CTOS
catalog/tools, probes `ctos-core`, checks the temporary Home Assistant context, checks the
Home Assistant token gate, checks the Speech-to-Phrase container state, and confirms whether the
open-ended STT directories exist. It does not start containers, write tokens, download models, or
create services.

Probe the tower when the T480-to-core SSH link is up:

```bash
ctos-voice-v2 status --target-probe
```

Show the CTOS intent catalog:

```bash
ctos-voice-v2 intents
```

Match recognized text against the safe CTOS intent catalog:

```bash
ctos-voice-v2 match agenda
```

Run the real push-to-talk command router with the same catalog:

```bash
ctos-voice command --no-speak agenda
ctos-voice command --no-speak "a jenda"
ctos-voice command --no-speak "propositions agenda"
```

`agenda` shows the day plan. `propositions agenda` shows pending agenda proposals and prints the
exact typed confirm/reject commands; it does not approve anything by voice.

Route natural transcript text through the same planner without mutating state:

```bash
ctos-voice route --no-speak "ajoute acheter du lait demain 30 min priorité 4"
ctos-voice route --no-speak --execute-safe "ajoute acheter du lait demain 30 min priorité 4"
ctos-voice route --no-speak --save-agenda "ajoute acheter du lait demain 30 min priorité 4"
```

The second command intentionally refuses the agenda write because natural agenda mutations need
review plus explicit confirmation. The third command stores a pending proposal only; it does not
write to the agenda.

Use the same path from one push-to-talk Vosk recording:

```bash
ctos-voice route-once --seconds 4 --no-speak
ctos-voice route-once --seconds 4 --no-speak --save-agenda
```

Use the bounded assistant mode while the mature Home Assistant/Speech-to-Phrase rail is still
token-gated:

```bash
ctos-voice assistant "agenda" --no-speak
ctos-voice assistant "ajoute acheter du lait demain 30 min priorité 4" --save-agenda --no-speak
ctos-voice assistant "explique en une phrase ce que tu peux faire" --no-speak
ctos-voice assistant-once --seconds 4 --no-speak
ctos-voice assistant-once --seconds 4 --save-agenda --no-speak
```

`assistant` first tries the CTOS safe action planner, then stages agenda proposals when requested,
then falls back to the local model through the CTOS prompt. The model response has no tool
authority: it cannot run shell, install packages, start VMs, or approve agenda writes from its own
text.

The operator-facing facade wraps those rails under shorter commands:

```bash
ctos-jarvis stack
ctos-jarvis mature-plan
ctos-jarvis mature-check
ctos-jarvis status
ctos-jarvis smoke
ctos-jarvis text "agenda"
ctos-jarvis voice --seconds 4
ctos-jarvis voice --seconds 4 --save-agenda
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
ctos-jarvis session
ctos-jarvis session --save-agenda
ctos-jarvis session --strict-preflight
ctos-jarvis listen --seconds 5
ctos-jarvis listen --seconds 5 --save-agenda --keep-backend
ctos-jarvis review
ctos-jarvis confirm latest --yes
ctos-jarvis doctor
ctos-jarvis unlock-voice
ctos-jarvis unlock-voice --interactive
ctos-jarvis unlock-voice --start
ctos-jarvis unlock-voice --test
ctos-jarvis setup-voice --plan
```

Use `ctos-jarvis` for daily operation and the lower-level `ctos-voice*` commands for debugging the
backend. `ctos-jarvis stack` prints the selected hybrid open-source/local Jarvis stack.
`ctos-jarvis mature-plan` prints the current adoption path so the operator does not keep tuning
single missed words as the main strategy. The accepted path is mature local voice infrastructure
behind CTOS authority: Home Assistant/Wyoming, Wyoming Whisper/faster-whisper, Speech-to-Phrase,
Piper, and Ollama on `ctos-core`; broader assistants or computer-control agents stay sandboxed
until their actions are mediated by CTOS proposals and typed approvals.
`ctos-jarvis mature-check` is the read-only readiness report for that plan. It
checks local voice/Jarvis state and audio controls by default, reports reusable
sample coverage, and prints the next command. `--full` adds `ctos-core`
SSH/backend probes; `--prefer deterministic` points next actions toward
Home Assistant/Speech-to-Phrase instead of the open-STT rail.
`ctos-jarvis status` is the compact read-only mission view. It combines
mature readiness, corpus/improvement state, the next capture phrase, and
pending agenda proposal count, then prints one next operator action.
`ctos-jarvis smoke` runs a non-destructive local readiness check with temporary agenda state.
Add `--full` to include `ctos-core` SSH/backend checks, and `--with-model` to include the local
model fallback.

`ctos-jarvis calibrate` is the preferred live open-STT loop. It wraps `listen --json`, keeps a
raw WAV and a preprocessed STT WAV, then prints the useful parts only: microphone level, STT-input
level, transcript, transcript guard result, CTOS route reason, best route candidate, agenda-save
refusal reason, and any agenda proposal. By default it does not save a proposal; use
`--save-agenda` only after the transcript/proposal shape looks correct. If `--save-agenda` is used
and CTOS cannot parse a safe agenda proposal, the report must show the refusal reason and leave the
agenda unchanged. Use `--clean` when the WAVs should be removed after the report.

`ctos-jarvis session` is the preferred repeated human test loop. It prompts before each recording,
keeps open-STT running between rounds, and stops the backend at the end unless `--keep-backend` is
explicit. It starts with a read-only preflight for microphone status, open-STT status, and pending
agenda proposals. The preflight warns by default and blocks only with `--strict-preflight`. With
`--save-agenda`, it runs the read-only agenda review at the end so the operator can see staged
proposals immediately. It is only a wrapper around `calibrate`; it does not approve agenda writes or
add model authority.

`ctos-jarvis run` is the daily operator shortcut above `session`. It stages agenda proposals by
default, runs the same preflight and review, and leaves final agenda writes behind typed
`ctos-jarvis confirm latest --yes`. Use `ctos-jarvis run --plan` to inspect the exact lower-level
session command before starting a voice loop.

`ctos-jarvis improve` is the shortest controlled loop for corpus/backend work.
It runs read-only triage first, then prints one selected next step. With
`--run`, it executes that step: strict guided collection for empty/incomplete
corpus, backend evaluation for ready corpus, or sample/manifest inspection for
repair states.

`ctos-jarvis collect-next` records only the next missing or weak corpus phrase.
Use it when full-suite capture is too heavy. It is plan-only unless `--run` is
passed.

`ctos-jarvis sample "..."` captures or imports a labeled WAV outside the repo, then appends a
JSONL manifest row with audio level metadata and replay commands. Use it to stop repeating the
same phrase manually when one word is missed. A sample can be replayed with
`ctos-jarvis calibrate --from-wav ...` against open-STT now and against Speech-to-Phrase or another
local backend later. Audio artifacts must stay under local state or `/tmp`, not Git. The manifest
stores `expected_text` for open-ended transcript checks; fixed-command samples can also carry
`intent_id` for strict intent regression.

`ctos-jarvis collect` records a compact reusable suite instead of one isolated
word. The default `core` preset captures the most important operator phrases
and one natural agenda request, then prints the inventory and regression
commands. It first runs a read-only local audio preflight so output and
microphone status are visible before recording. Use
`ctos-jarvis collect --strict-preflight` when bad audio state should block the
capture, `--no-preflight` when deliberately debugging the recorder, and
`ctos-jarvis collect --plan` before recording. Use
`ctos-jarvis collect --run-regression` only when the captured samples should be
tested immediately.

`ctos-jarvis corpus` is the read-only verdict between recording and testing. It
checks sample count, expected preset coverage, referenced WAV files, and obvious
audio-state warnings. It does not record, transcribe, start backends, or mutate
agenda state.

`ctos-jarvis triage` turns the current corpus/sample state into a concrete
operator decision: capture, complete, repair, recapture weak audio, or benchmark
the backends. It is read-only and does not start STT.

`ctos-jarvis evaluate` chains that verdict into regression. It stops before
recognition when the corpus is not ready, and can compare the local fallback
and open-STT/Wyoming with `--backend both`.

`ctos-jarvis listen` is the operator shortcut for the open-ended Whisper/Wyoming rail. It checks
the temporary open-STT backend on `ctos-core`, starts it if needed, records one push-to-talk
sample on the T480, sends it through the localhost SSH tunnel, routes the transcript through CTOS,
and stops the backend again if this command started it. Use `--keep-backend` for repeated prompts
in the same test window. Use `--save-agenda` to store a recognized agenda request as a pending
proposal; it still does not write to the agenda until `ctos-jarvis confirm latest --yes`.

`ctos-voice-v2 open-stt start` waits for the container logs to report `Ready` before returning
success. A socket being open is not enough: the first synthetic `--from-wav` test showed that the
backend could still return `Broken pipe` during startup. After this guard was added, synthetic WAV
transport returned a transcript, but CTOS correctly refused agenda staging when the synthetic
transcript was too degraded to parse safely.

`ctos-jarvis unlock-voice` is the operator-safe path into the mature Home
Assistant/Speech-to-Phrase rail. Without flags, it ensures the localhost Home Assistant tunnel,
runs the live doctor, and reports the exact blocker. With `--interactive`, it delegates to
`ctos-voice-setup`, which may request hidden Home Assistant onboarding credentials and then start
Speech-to-Phrase once the token gate is green. With `--start`, it starts Speech-to-Phrase only
when the doctor reports `ready_to_start_speech_to_phrase`. With `--test`, it also records one
short sample and routes the returned transcript through CTOS.

Route any typed text or STT transcript through the shared CTOS action planner:

```bash
ctos-ai route-text "agenda"
ctos-ai route-text --source voice --execute-safe "agenda"
ctos-ai route-text "ajoute un rendez-vous demain"
```

The planner is intentionally conservative. It may execute only Tier 0/Tier 1 commands owned by
`ctos-ai` when `--execute-safe` is passed. Natural-language agenda edits, VM lifecycle requests,
package installs, and shell-like requests remain transcript text until CTOS adds a parser plus an
approval loop.

The first permissioned natural-language agenda loop is:

```bash
ctos-ai agenda-propose "ajoute acheter du lait demain 30 min priorité 4"
ctos-ai agenda-propose "ajoute acheter du lait demain 30 min priorité 4" --save --source voice
ctos-ai agenda-review
ctos-ai agenda-proposals
ctos-ai agenda-confirm latest --yes
ctos-ai agenda-propose "ajoute acheter du lait demain 30 min priorité 4" --commit --yes
```

The first command only proposes. The `--save` path keeps a pending local proposal that can be
confirmed or rejected later. `agenda-confirm latest --yes` writes to `ctos-agenda` after explicit
confirmation. The direct `--commit --yes` path remains available for reviewed typed use. This is a
local CTOS agenda feature, not a general voice-to-shell mechanism.

Export phrases for the next backend adapter:

```bash
ctos-voice-v2 export-phrases --format jsonl
```

Export Home Assistant / Speech-to-Phrase custom sentences:

```bash
ctos-voice-v2 export-phrases --format ha-sentences
```

Write a backend handoff bundle:

```bash
ctos-voice-v2 export-backend --backend home-assistant --dir /tmp/ctos-voice-backend
ctos-voice-v2 export-backend --backend speech-to-phrase --dir /tmp/ctos-voice-backend
```

Validate a generated backend bundle:

```bash
ctos-voice-v2 validate-backend --dir /tmp/ctos-voice-backend
```

Print the next safe handoff commands for a backend:

```bash
ctos-voice-v2 backend-commands --backend speech-to-phrase --dir /tmp/ctos-voice-backend
ctos-voice-v2 backend-commands --backend home-assistant --dir /tmp/ctos-voice-backend
```

Preflight a backend bundle and runtime path:

```bash
ctos-voice-v2 backend-preflight --backend speech-to-phrase --dir /tmp/ctos-voice-backend
```

To check a disposable runtime venv without changing the system Python:

```bash
ctos-voice-v2 backend-preflight \
  --backend speech-to-phrase \
  --dir /tmp/ctos-voice-backend \
  --runtime-python /tmp/ctos-speech-to-phrase-smoke-venv/bin/python
```

Inspect the Speech-to-Phrase model/tools cache:

```bash
ctos-voice-v2 stp-cache \
  --runtime-python /tmp/ctos-speech-to-phrase-smoke-venv/bin/python
```

Probe the recommended `ctos-core` cache paths when the SSH link is up:

```bash
ctos-voice-v2 stp-cache \
  --runtime-python /tmp/ctos-speech-to-phrase-smoke-venv/bin/python \
  --target-probe
```

Print the official Wyoming/Speech-to-Phrase container test plan:

```bash
ctos-voice-v2 stp-container-plan
ctos-voice-v2 stp-container-plan --target-probe
```

Start/check/stop the temporary Speech-to-Phrase container after Home Assistant readiness is green:

```bash
ctos-voice-v2 stp-container status
ctos-voice-v2 stp-container start
ctos-voice-v2 stp-container logs
ctos-voice-v2 stp-container stop
```

`stp-container start` refuses to run until `hass-context readiness` reports a valid Home Assistant token/API state. It does not create a systemd unit.

Run one temporary Speech-to-Phrase recognition loop from the T480:

```bash
ctos-voice-v2 stp-transcribe --target-tunnel --record-seconds 3 --preprocess auto --route
ctos-voice-v2 stp-transcribe --target-tunnel --record-seconds 3 --preprocess auto --execute-safe
```

`stp-transcribe` records a short local WAV with the existing `ctos-voice` recorder, opens a
temporary SSH tunnel to `ctos-core:127.0.0.1:10300`, sends the audio to the Speech-to-Phrase
Wyoming endpoint, then routes the returned transcript through CTOS. `--route` prints the CTOS
plan only; `--execute-safe` is still limited to CTOS-owned Tier 0/1 actions. No long-lived tunnel,
daemon, token, or recording is kept unless `--keep-wav` is explicitly passed.

Check the local Wyoming transport and CTOS routing without Home Assistant or Speech-to-Phrase:

```bash
ctos-voice-v2 wyoming-selftest
ctos-voice-v2 wyoming-selftest --json
```

`wyoming-selftest` starts a one-shot mock Wyoming server on `127.0.0.1`, writes a temporary mono
WAV, receives a mock transcript such as `agenda`, and routes that text through CTOS. It proves the
event framing and CTOS planner handoff only; it is not a real speech-recognition test.

Print and prepare the temporary Home Assistant websocket/token context:

```bash
ctos-voice-v2 hass-context-plan
ctos-voice-v2 hass-context-plan --target-probe
ctos-voice-v2 hass-context-plan --target-prepare --target-probe
```

Start/check/stop the temporary Home Assistant test container:

```bash
ctos-voice-setup --plan
ctos-voice-setup
ctos-voice-v2 hass-context status
ctos-voice-v2 hass-context start
ctos-voice-v2 hass-context logs
ctos-voice-v2 hass-context token-status
ctos-voice-v2 hass-context readiness
ctos-voice-v2 hass-context tunnel-command
ctos-voice-v2 hass-context tunnel-status
ctos-voice-v2 hass-context tunnel-start
ctos-voice-v2 hass-context onboarding-status
ctos-voice-v2 hass-context token-command
ctos-voice-v2 hass-context token-save
ctos-voice-v2 hass-context onboard-api
ctos-voice-v2 hass-context stop
```

`ctos-voice-setup` is the guided path for the current live test window. It checks the local/core state, starts the temporary Home Assistant context if needed, runs browserless onboarding when the token is missing, re-checks readiness, then starts the temporary Speech-to-Phrase container. Use `--plan` to audit the sequence before running it.

This temporary Home Assistant context is only for the first live Speech-to-Phrase loop. It should run as a manual `podman run --rm` container on `ctos-core`, bind only to `127.0.0.1:8123`, and be reached from the T480 through the printed SSH tunnel. Complete onboarding in the tunneled browser, create a long-lived access token, and write only the token value to `/run/user/$UID/ctos-ha-token`. Do not paste the token into shell history or Git.

Preferred token handoff:

```bash
ctos-voice-v2 hass-context token-save
```

This reads the token with hidden input on the T480, sends it over the existing SSH link, strips newlines, writes it to `/run/user/$UID/ctos-ha-token` on `ctos-core`, and sets mode `600`. It does not print the token.

Browserless first onboarding:

```bash
ctos-voice-v2 hass-context onboard-api
```

Use this only while the temporary Home Assistant instance is still at the first onboarding step. It prompts for the Home Assistant display name, username, and password, posts to the local tunneled onboarding API, exchanges the returned auth code, creates a long-lived access token through the local websocket API, and stores only that token on `ctos-core` using the same `/run/user/$UID/ctos-ha-token` path. It does not print the password, auth code, access token, refresh token, or long-lived token.

Before launching Speech-to-Phrase, use `ctos-voice-v2 hass-context readiness`. It must report `state=ready`; missing or invalid tokens intentionally return a non-zero exit code.

When a temporary Home Assistant test instance exists, pass only references to it:

```bash
ctos-voice-v2 backend-preflight \
  --backend speech-to-phrase \
  --dir /tmp/ctos-voice-backend \
  --runtime-python /tmp/ctos-speech-to-phrase-smoke-venv/bin/python \
  --hass-websocket-uri ws://127.0.0.1:8123/api/websocket \
  --hass-token-file /run/user/$UID/ctos-ha-token
```

Do not paste Home Assistant tokens into shell history and do not store them in Git.

The bundle contains:

- `custom_sentences/fr/ctos.yaml`: recognition phrases in Home Assistant custom sentence format.
- `ctos_intent_map.json`: sidecar map from backend intent names to CTOS intent IDs, commands, tiers, and spoken replies.
- `README.md`: short boundary reminder.

This is intentionally inert. The backend may recognize `CTOSAgenda`, but CTOS still decides that this maps to `ctos-ai plan-day` and whether the action is safe.

The validator checks:

- generated YAML exists under `custom_sentences/fr/ctos.yaml`;
- the sidecar map exists and has a `backend_intents` object;
- every backend intent in the map exists in the YAML;
- every CTOS catalog phrase is present;
- command, tier, and CTOS intent ID still match `ai/voice_intents_fr.json`;
- exported voice actions stay Tier 0 or Tier 1.

The preflight checks:

- the generated bundle shape and Tier 0/1 boundary;
- local tools such as `python3`, `git`, `ffmpeg`, `ssh`, `ctos-voice`, and `ctos-ai`;
- whether the `speech_to_phrase` and `wyoming` Python modules are importable;
- whether the generated CTOS custom-sentence YAML parses through `hassil`;
- whether `python -m speech_to_phrase.train --help` exists for the no-Home-Assistant training path;
- whether the selected Speech-to-Phrase model/tools cache is present;
- whether a temporary Home Assistant websocket URI and token file have been provided;
- optionally, whether `ctos-core` has the expected basic tools when `--target-probe` is used.

The temporary Home Assistant plan checks:

- the selected container image and rootless runtime;
- the temporary config directory under `/srv/ctos/voice/home-assistant-test/config`;
- localhost-only bind `127.0.0.1:8123:8123`;
- SSH tunnel command from the T480;
- token-file handling outside Git and shell history;
- optional `ctos-core` runtime/path/port probe without starting a persistent service.

The temporary Home Assistant manager checks or controls:

- `status`: rootless runtime, image cache, container state, localhost port, and HTTP status;
- `start`: creates the config dir if needed and runs `ctos-ha-test` with `--rm`, `--pull=missing`, and localhost-only port binding;
- `logs`: prints a short container log tail for first-start diagnostics;
- `token-status`: checks the token file metadata and Home Assistant API readiness without printing the token; exits non-zero until the token is valid;
- `readiness`: combines container status and token/API status, then prints the Speech-to-Phrase plan command only when the token check is ready; exits non-zero until the context is usable;
- `tunnel-command`: prints the T480 SSH tunnel and local URL again without touching the remote host;
- `tunnel-status`: checks whether the T480 can reach the tunneled Home Assistant onboarding API on `127.0.0.1`;
- `tunnel-start`: starts the T480 localhost-only SSH tunnel with `ExitOnForwardFailure=yes` unless it is already reachable;
- `onboarding-status`: reads Home Assistant first-run onboarding steps through the T480 localhost tunnel without creating users or tokens;
- `token-command`: prints the SSH/editor command for creating the token file without putting the token into shell history;
- `onboard-api`: performs first-run onboarding through verified local Home Assistant endpoints and stores a generated long-lived token without printing secrets;
- `stop`: stops the temporary container.

The temporary Speech-to-Phrase manager checks or controls:

- `status`: remote runtime/image/path/container/port state plus token-file presence;
- `start`: checks Home Assistant token/API readiness first, then starts `ctos-speech-to-phrase` with `podman run -d --rm`;
- `logs`: prints a short log tail from the temporary container;
- `stop`: stops the temporary container if present.

The stack doctor reports the next action from the live state:

- `ctos_core_unreachable`: restore the T480 to `ctos-core` SSH/link first;
- `hass_not_running`: run `ctos-voice-v2 hass-context start`;
- `missing_token` / `missing_token_file`: run `ctos-voice-v2 hass-context onboard-api` or `token-save`;
- `ready_to_start_speech_to_phrase`: run `ctos-voice-v2 stp-container start`;
- `ready`: capture samples or run the next recognition test.

Important: Speech-to-Phrase is not treated as a tiny offline WAV-to-intent binary here. The CTOS path is:

1. export and validate CTOS custom sentences;
2. run a local import/help and `hassil` parse smoke test in a venv;
3. prepare an offline training context with the French `fr_FR-rhasspy` model plus Kaldi/OpenFST/OpenGRM/Phonetisaurus tools;
4. run a temporary Home Assistant/Wyoming recognition test;
5. only then consider a service.

The first venv smoke commands are rendered by:

```bash
ctos-voice-v2 backend-commands --backend speech-to-phrase --dir /tmp/ctos-voice-backend
```

The observed upstream entry point in the smoke test is:

```bash
python -m speech_to_phrase --help
```

The no-Home-Assistant trainer can be inspected without starting a daemon:

```bash
/tmp/ctos-speech-to-phrase-smoke-venv/bin/python -m speech_to_phrase.train --help
```

The real offline training command is deliberately rendered commented-out by `backend-commands`, because it needs a chosen cache/storage boundary for model and tool downloads:

```bash
# /tmp/ctos-speech-to-phrase-smoke-venv/bin/python -m speech_to_phrase.train \
#   --model fr_FR-rhasspy \
#   --sentences /tmp/ctos-voice-backend/custom_sentences/fr/ctos.yaml \
#   --train-dir /srv/ctos/cache/speech-to-phrase/train \
#   --tools-dir /srv/ctos/cache/speech-to-phrase/tools \
#   --models-dir /srv/ctos/models/speech-to-phrase
```

Current readiness levels:

- `backend_runtime_ready`: Python imports, module help, and `hassil` parsing are OK.
- `offline_training_context_ready`: model and speech-tool caches are present.
- `home_assistant_context_ready`: a temporary websocket URI and token file are provided.
- `full_recognition_ready`: all previous layers are true.

Current cache placement:

- preferred owner: `ctos-core`;
- model cache: `/srv/ctos/models/speech-to-phrase`;
- training cache: `/srv/ctos/cache/speech-to-phrase/train`;
- tools cache: `/srv/ctos/cache/speech-to-phrase/tools`.

The `stp-cache --target-probe` check on 2026-07-07 reached `ctos-core` over SSH and confirmed that the model/tool cache is not present yet.

Current container-first live test placement:

- image: `docker.io/rhasspy/wyoming-speech-to-phrase`;
- runtime: `podman` on `ctos-core` if available;
- bind-mounted CTOS custom sentences: `/srv/ctos/voice/backend/speech-to-phrase/custom_sentences`;
- training cache: `/srv/ctos/cache/speech-to-phrase/train`;
- model cache: `/srv/ctos/models/speech-to-phrase`;
- speech tools: image-internal `/usr/src/tools` through `/run.sh`, not a host mount in the first container test;
- Home Assistant token: mounted read-only into the temporary container from `/run/user/$UID/ctos-ha-token`, not passed as a host shell token argument;
- Wyoming URI: `tcp://127.0.0.1:10300`, tunneled from the T480 only when needed.

The 2026-07-07 `stp-container-plan --target-probe` check reached `ctos-core`, found `/usr/bin/podman`, and confirmed that the CTOS Speech-to-Phrase backend bundle is present under `/srv/ctos/voice/backend/speech-to-phrase`.

The 2026-07-07 `stp-container-inspect` check pulled and inspected `docker.io/rhasspy/wyoming-speech-to-phrase` on `ctos-core`. The image help passed, the entrypoint is `bash /run.sh`, and `/run.sh` uses image-internal `./tools` under `/usr/src`. The pulled image digest was `sha256:9ef75f4a4f21484ebbe7e0c0f81a53bb7670e6b57430c7d8fa632239ba318289`.

## Open-Ended STT Rail

The fixed-command rail should not become an endless synonym list. If `agenda` is missed in a live command, that is useful feedback, but it does not mean every natural request should be forced through Speech-to-Phrase.

The practical product path is now:

- use the current `ctos-jarvis text` / `ctos-jarvis voice` bridge as the operator surface;
- evaluate a mature Whisper-class local backend for open-ended French STT;
- feed transcripts into CTOS planning and approvals;
- keep Speech-to-Phrase as the strict rail for a small set of fixed Tier 0/1 commands;
- defer any generic assistant platform that wants direct authority over the host.

`ctos-voice-v2 open-stt-plan` describes the next rail:

- Speech-to-Phrase remains the deterministic rail for fixed Tier 0/1 commands.
- A Whisper-class local STT backend transcribes natural French requests.
- CTOS receives text, proposes an intent/action, and applies the permission tier.
- Raw transcript text is never executed as shell.
- Transcripts and recordings are temporary by default.

First selected candidate:

- primary: `wyoming-faster-whisper` via the official `docker.io/rhasspy/wyoming-whisper` image
- reason: it matches the current Wyoming/Home Assistant direction, but can still be tested as a
  localhost-only backend on `ctos-core`;
- first smoke models: `base-int8`, then `small-int8`; both prove the route works, but neither is
  yet good enough as a Jarvis input without better live capture preprocessing and hallucination
  filtering;
- fallbacks: `whisper.cpp` or a direct `faster-whisper` CTOS adapter if the Wyoming wrapper is not
  reliable on this hardware.

The direct Python venv path is not the preferred first route anymore. On 2026-07-07 the upstream
venv install reached `ctos-core` but failed while building `pysilero-vad` under the current Python
3.14 toolchain. The official container `docker.io/rhasspy/wyoming-whisper` did pass `--help`, then
started as a temporary localhost-only Wyoming STT backend on port `10301`.

Default future placement:

- model dir: `/srv/ctos/models/open-stt`
- cache dir: `/srv/ctos/cache/open-stt`
- backend dir: `/srv/ctos/voice/backend/open-stt`
- future localhost-only Wyoming port: `127.0.0.1:10301`

Preflight:

```bash
ctos-voice-v2 open-stt-plan
ctos-voice-v2 open-stt-candidates
ctos-voice-v2 open-stt-plan --target-probe
ctos-voice-v2 open-stt-plan --target-prepare --target-probe
```

This command does not install packages, download models, start services, or enable an always-on microphone. With `--target-prepare`, it only creates the planned `/srv/ctos` directories on `ctos-core`.

`open-stt-candidates` is still non-mutating, but the runnable smoke sequence now points to the
managed temporary container command instead of raw SSH/podman snippets:

```bash
ctos-voice-v2 open-stt status
ctos-voice-v2 open-stt start
ctos-jarvis calibrate
ctos-jarvis calibrate --save-agenda
ctos-jarvis session
ctos-jarvis session --save-agenda
ctos-jarvis listen --seconds 5
ctos-jarvis listen --seconds 5 --save-agenda --keep-backend
ctos-voice-v2 stp-transcribe --wyoming-port 10301 --target-tunnel --record-seconds 5 --preprocess auto --route
ctos-voice-v2 stp-transcribe --wyoming-port 10301 --target-tunnel --record-seconds 5 --preprocess auto --save-agenda
ctos-voice-v2 open-stt logs
ctos-voice-v2 open-stt stop
```

`open-stt start` runs `docker.io/rhasspy/wyoming-whisper` with `--rm`, binds only
`127.0.0.1:10301` on `ctos-core`, stores model data under `/srv/ctos/models/open-stt`, and creates
no systemd unit. Do not turn that sequence into a daemon until the transcript reaches CTOS and
routes through the planner.

Live manager verification on 2026-07-07: status found the image and paths ready, start launched
`ctos-open-stt-smoke`, logs showed `Ready`, and stop removed the container and freed port `10301`.

Prepare real-voice regression samples outside Git:

```bash
ctos-voice-v2 sample-plan --dir /tmp/ctos-voice-samples --write-manifest
```

Then run each printed `ctos-voice record-once ...` command, speaking the displayed label.
When samples exist, test them:

```bash
ctos-voice-v2 regression --dir /tmp/ctos-voice-samples
ctos-voice-v2 regression --manifest /tmp/ctos-voice-samples/manifest.jsonl
```

For the normal Jarvis loop, use the persistent operator sample store instead of
`/tmp`:

```bash
ctos-jarvis collect --plan
ctos-jarvis status
ctos-jarvis improve
ctos-jarvis collect-next
ctos-jarvis collect
ctos-jarvis corpus
ctos-jarvis triage
ctos-jarvis evaluate
ctos-jarvis evaluate --backend both
ctos-jarvis sample "agenda"
ctos-jarvis samples
ctos-jarvis regression
ctos-jarvis regression --backend open-stt --target-tunnel
```

The `ctos-jarvis regression` wrapper only fills in the default manifest path
under `~/.local/state/ctos/jarvis-samples`; it does not add a daemon or grant
extra action authority.

Show the next manual handoff commands:

```bash
ctos-voice-v2 next-commands
```

Manifest rows may also use a known transcript instead of an audio file for deterministic tests:

```json
{"intent_id":"ctos_agenda","transcript":"a jenda","label":"agenda drift"}
```

## Next Implementation Loop

1. Run `ctos-jarvis run` for several open-STT push-to-talk reports with audio levels, transcript,
   guard state, CTOS route reason, and best route candidate. Use `--strict-preflight` when you want
   the loop to stop before recording if microphone/backend checks warn.
2. If CTOS stages a pending agenda proposal, inspect the printed read-only review; commit still
   requires typed `ctos-jarvis confirm latest --yes`. If staging is refused, keep the refusal reason
   and retest with a simpler phrase.
3. Fix the T480 microphone capture/gain path if live recordings still reach the backend but return
   empty transcripts, low-quality text, or hallucinated silence/noise text.
4. Use the lower-level `ctos-voice-v2 stp-transcribe ...` command only for debugging audio,
   preprocessing, or route payloads.
5. Complete the temporary Home Assistant onboarding/token blocker when the fixed-command rail is worth testing again.
6. Run one localhost-only Speech-to-Phrase loop for fixed commands.
7. Record short French samples for the deterministic rail and keep only temporary debug WAVs.
8. Add Piper TTS after the recognition/action boundary is stable.
9. Expand the agenda parser only after real usage shows the missing French forms.

No daemon should be installed until the install path and service boundary are documented in the decision log.

## Audio Calibration

Use the repo-owned audio helper before open-STT live tests:

```bash
ctos-audio status
ctos-audio doctor
ctos-audio doctor --json
ctos-audio report
ctos-audio panel
ctos-audio mic-status
ctos-audio mic-set 30
ctos-audio mic-up 5
ctos-audio mic-down 5
ctos-audio mixer
ctos-voice-v2 mic-check --record-seconds 3 --keep-wav /tmp/ctos-mic-check.wav
ctos-jarvis calibrate
ctos-jarvis session
```

The microphone commands use WirePlumber through `wpctl` and cap source volume at 100 percent to
avoid making clipping worse. They are intended for push-to-talk calibration only; they do not start
an always-on microphone listener.

`ctos-audio doctor --json` is read-only. It exists so Jarvis can tell the
difference between a real PipeWire/audio problem and a restricted execution
context that cannot read the live desktop DBus/PipeWire session.

Permanent desktop controls:

- Waybar `VOL`: scroll changes speaker volume, left click opens the CTOS audio panel, middle click opens the full mixer, right click toggles mute.
- `SUPER+A`: open the CTOS audio panel.
- `SUPER+PageUp` / `SUPER+PageDown`: speaker volume up/down by 10 percent.
- `SUPER+Shift+PageUp` / `SUPER+Shift+PageDown`: microphone gain up/down by 5 percent.
- `SUPER+BackSpace`: speaker mute.
- `SUPER+Shift+BackSpace`: microphone mute.
- `SUPER+Shift+A`: full mixer.

`ctos-voice-v2 mic-check` records or inspects a WAV and reports duration, RMS level, peak level,
clipping percentage, and a concrete next adjustment. `stp-transcribe` includes the same analysis in
its human and JSON output so a failed transcript can be separated from a bad recording.

`stp-transcribe` also applies a basic transcript guard before CTOS routing. By default, it blocks
empty transcripts, unreadable normalized text, repeated non-speech symbols, high symbol-noise
transcripts, bad audio states, and known Whisper silence/noise hallucinations such as `Sous-titres
réalisés...`. This is intentionally conservative: a suspicious transcript should fail closed
instead of becoming an agenda action or command proposal. Use `--no-transcript-guard` only for
debugging a backend, never for normal Jarvis use.

Before sending audio to STT, `stp-transcribe --preprocess auto` now runs a simple energy-based
voice activity check, trims around the active region, and normalizes only voice-like captures toward
8 percent RMS with a peak ceiling. If the sample has too little voice-like activity, it refuses
before contacting Whisper so silence or room noise is not amplified into hallucinated text.
Use `--preprocess off` only to compare raw backend behavior, and `--preprocess-wav /tmp/file.wav`
when the exact STT input needs to be inspected.
