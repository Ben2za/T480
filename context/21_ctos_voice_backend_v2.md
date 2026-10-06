# CTOS Voice Backend V2

Date: 2026-07-07

## Summary

The Vosk push-to-talk V1 works, but the user observed the real limitation: command quality will not scale if CTOS keeps adding ad hoc phrase matches. The next direction is to reuse a mature local voice stack for voice I/O and keep CTOS as the action/permission boundary.

## Current Decision Under Test

Primary spike:

- Home Assistant Assist / Wyoming style voice pipeline as the mature ecosystem target.
- Speech-to-Phrase for fixed CTOS command recognition.
- Piper / Wyoming Piper for clearer local TTS after intent recognition is reliable.
- Whisper-class dictation later for open conversation, not for the first command loop.

Keep:

- push-to-talk first;
- no always-on microphone yet;
- no cloud STT by default;
- no direct mutable action from voice;
- `ctos-core` behind the T480 bastion.

## Why Not Keep Extending Vosk V1

Vosk V1 is a good fallback and smoke-test path. It is not enough for the desired Jarvis UX because it transcribes freely and then CTOS guesses an intent. For fixed commands like `agenda`, a phrase/intent recognizer is a better first tool than a free dictation model.

## Why Not Install A Full Assistant Immediately

Home Assistant Assist, OpenVoiceOS, and Leon are larger platforms than the current CTOS voice need. Installing one blindly would add services, package choices, exposed ports, and state before CTOS has a narrow adapter.

The safer next step is to make CTOS's own intent catalog explicit, then connect one backend to it.

## Artifacts Added

- `ai/voice_backends.json`
- `ai/voice_intents_fr.json`
- `ai/voice_intents.py`
- `docs/VOICE_BACKEND_V2.md`
- `scripts/ctos-voice-v2`

`ctos-voice-v2` now exposes:

- `plan`: selected direction and current safe intents.
- `status`: registry/tool/V1 voice readiness.
- `backends`: backend registry.
- `intents`: human-readable intent catalog.
- `match <text>`: deterministic local intent matching for recognized text.
- `export-phrases`: generic phrase export plus Home Assistant/Speech-to-Phrase custom-sentence export.
- `export-backend`: writes an inert backend handoff bundle with custom sentences and a CTOS sidecar intent map.
- `validate-backend`: verifies that an exported bundle still matches the CTOS catalog and Tier 0/1 boundary.
- `backend-commands`: prints safe next handoff commands without installing or starting daemons.
- `sample-plan`: temporary recording plan for real-voice samples outside Git.
- `regression`: WAV/transcript regression against expected CTOS intents.
- `next-commands`: next safe manual checks.

Runtime update 2026-07-07:

- `ctos-voice` now consumes the shared intent matcher before falling back to the old V1 mapping.
- `agenda`, `a jenda`, and `ajenda` are mapped to `ctos_agenda -> ctos-ai plan-day`.
- The helper and runtime now share the same phrase catalog, so future phrase fixes do not need two code changes.

Regression update 2026-07-07:

- `ctos-voice-v2 sample-plan --dir /tmp/ctos-voice-samples --write-manifest` creates a temporary JSONL manifest and prints the exact recording commands.
- `ctos-voice-v2 regression --dir ...` scans WAV files named `intent_id__label.wav`.
- `ctos-voice-v2 regression --manifest ...` accepts JSON/JSONL rows with either `file` or `transcript`.
- Audio samples stay outside Git; only observed phrase drift should be added to `ai/voice_intents_fr.json`.

Backend export update 2026-07-07:

- `ctos-voice-v2 export-phrases --format ha-sentences` renders custom-sentences YAML from the CTOS catalog.
- `ctos-voice-v2 export-phrases --format ha-map` renders the sidecar backend-intent to CTOS-intent map.
- `ctos-voice-v2 export-backend --backend home-assistant --dir /tmp/ctos-voice-backend` writes a complete inert handoff bundle.
- `ctos-voice-v2 export-backend --backend speech-to-phrase --dir /tmp/ctos-voice-backend` writes the same custom-sentence structure for the Speech-to-Phrase path.
- The exported backend intent names are recognition labels only; CTOS remains the command, tier, and approval boundary.

Bundle validation update 2026-07-07:

- `ctos-voice-v2 validate-backend --dir ...` checks the generated custom-sentence YAML, sidecar map shape, intent set, phrase lists, CTOS intent IDs, commands, tiers, and Tier 0/1 safety.
- `ctos-voice-v2 backend-commands --backend ...` prints the next safe handoff commands without installing packages, creating a service, or exposing ports.

Speech-to-Phrase preflight update 2026-07-07:

- `ctos-voice-v2 backend-preflight --backend speech-to-phrase --dir ...` checks the exported bundle, local helper tools, Python module imports, and optional `ctos-core` readiness.
- `ctos-voice-v2 backend-preflight --runtime-python <venv>/bin/python` can check a disposable or future service venv without implying that the system Python or CTOS runtime has changed.
- The preflight reports three separate states: CTOS bundle readiness, local runtime/import readiness, and full recognition-test readiness.
- Full Speech-to-Phrase recognition is not marked ready unless a temporary Home Assistant websocket URI and token file are provided.
- `ctos-voice-v2 backend-commands --backend speech-to-phrase --dir ...` now renders a venv smoke-test path and the placeholder arguments required for a later Home Assistant/Wyoming recognition test.
- Token handling rule: use a token file outside Git; do not paste Home Assistant tokens into shell history.

Smoke-test observation 2026-07-07:

- PyPI name probing for `speech-to-phrase` and `speech_to_phrase` returned no installable distribution for the current environment.
- Installing from `git+https://github.com/OHF-Voice/speech-to-phrase.git` into `/tmp/ctos-speech-to-phrase-smoke-venv` succeeded at commit `b4ecef9519e84fefd5dc35c0384c50efa13a0bad`.
- Installed runtime versions: `speech_to_phrase 1.4.3`, `wyoming 1.5.4`.
- The observed invocation is `python -m speech_to_phrase --help`; no dedicated `speech-to-phrase` console script was installed.
- Help output confirms required runtime arguments: `--train-dir`, `--tools-dir`, `--models-dir`, `--custom-sentences-dir`, `--hass-token`, and `--hass-websocket-uri`.
- The normal system preflight remains intentionally false for `speech_to_phrase` because the successful install is only in `/tmp`.
- `hassil.Intents.from_files([.../custom_sentences/fr/ctos.yaml])` parsed the CTOS generated YAML successfully and found the six exported intents: `CTOSAgenda`, `CTOSApprovals`, `CTOSBrief`, `CTOSCapabilities`, `CTOSOpenDesk`, and `CTOSOpenVms`.
- `python -m speech_to_phrase.train --help` exists as a no-Home-Assistant training entry point.
- The standalone trainer is not lightweight enough to run blindly: it needs the French `fr_FR-rhasspy` Kaldi model plus Kaldi, OpenFST, OpenGRM, and Phonetisaurus tools under the selected cache directories.
- `ctos-voice-v2 backend-preflight --runtime-python /tmp/ctos-speech-to-phrase-smoke-venv/bin/python` now separates `backend_runtime_ready=True` from `offline_training_context_ready=False` and `full_recognition_ready=False`.
- `ctos-voice-v2 stp-cache` now inspects the expected Speech-to-Phrase cache layout and recommends `ctos-core` ownership under `/srv/ctos`.
- `ctos-voice-v2 stp-cache --target-probe` reached `ctos-core` over SSH on 2026-07-07 and confirmed the `fr_FR-rhasspy` model and speech-tool cache are not present yet.
- `ctos-voice-v2 stp-container-plan` now renders the official `docker.io/rhasspy/wyoming-speech-to-phrase` container test plan as the preferred first live-backend route before attempting a local Kaldi/OpenFST/OpenGRM/Phonetisaurus toolchain build.
- `ctos-voice-v2 stp-container-plan --target-probe` reached `ctos-core` on 2026-07-07, found `/usr/bin/podman`, and confirmed the CTOS custom-sentence bundle is present under `/srv/ctos/voice/backend/speech-to-phrase`.
- `ctos-voice-v2 stp-container-inspect` pulled and inspected `docker.io/rhasspy/wyoming-speech-to-phrase` on `ctos-core`; the image `--help` passed and the pulled digest was `sha256:9ef75f4a4f21484ebbe7e0c0f81a53bb7670e6b57430c7d8fa632239ba318289`.
- The generated live container command now mounts the Home Assistant token file read-only at `/run/secrets/ctos-ha-token` and lets the container entrypoint read it. The token is not printed or passed as a host shell token argument.
- `ctos-voice-v2 stp-container status|start|stop|logs` now manages the temporary Speech-to-Phrase container on `ctos-core` without creating a service. `start` first checks Home Assistant token/API readiness and refuses before launching if the token is missing or invalid.
- Image inspection found `ENTRYPOINT=["bash","/run.sh"]`; `/run.sh` already passes `--tools-dir ./tools` from `/usr/src`, so CTOS must not mount or override `/tools` for the first container test.

Temporary Home Assistant context update 2026-07-07:

- `ctos-voice-v2 hass-context-plan` renders the smallest temporary Home Assistant container/tunnel/token plan for the first Speech-to-Phrase recognition loop.
- `ctos-voice-v2 hass-context status|start|logs|token-status|readiness|tunnel-command|tunnel-status|tunnel-start|onboarding-status|token-command|token-save|stop` manages that temporary container lifecycle and readiness without creating a systemd service.
- The temporary context uses `ghcr.io/home-assistant/home-assistant:stable`, rootless `podman`, config at `/srv/ctos/voice/home-assistant-test/config`, bind `127.0.0.1:8123:8123`, and token file `/run/user/$UID/ctos-ha-token`.
- This is only a websocket/token context. It is not Home Assistant OS/Supervisor, not a permanent daemon, and not a LAN-exposed service.
- No Home Assistant token should be pasted into shell history or stored in Git. `hass-context token-save` reads the token with hidden input on the T480, sends it over SSH stdin, strips newlines, writes it to `/run/user/$UID/ctos-ha-token` on `ctos-core`, and sets mode `600` without printing the token. Token readiness checks print only file metadata and API status, never token content. `token-status` and `readiness` exit non-zero until the token is valid, so they can be used as real gates.

Strategy update 2026-07-07:

- A missed spoken `agenda` command should not push CTOS into months of manual synonym tuning.
- Keep Speech-to-Phrase as the deterministic rail for fixed, safe commands.
- Add a local open-ended STT rail next, likely through a Wyoming/Whisper-compatible backend, for natural requests such as agenda planning and conversational work.
- Keep Home Assistant Assist/Wyoming as the first mature local voice bus because it matches the current Speech-to-Phrase/Piper/Wyoming direction.
- Keep OpenVoiceOS and Open Interpreter/01 as inspiration or sandboxed research targets only; they should not become the unsupervised authority layer on the T480 or `ctos-core`.
- Model runtimes such as Ollama, AirLLM-style offload, or GLM-family checkpoints are a later model-serving decision. They should plug into CTOS tools after the voice/action boundary is stable.
- `ctos-voice-v2 open-stt-plan` now renders the non-destructive plan/preflight for that open-ended STT rail. It checks local tools, can probe `ctos-core` paths, and records the policy that open STT returns transcript text only; CTOS still owns intent/action approval.
- `ctos-voice-v2 open-stt-plan --target-prepare --target-probe` can create only the planned `/srv/ctos` directories on `ctos-core`; it still does not download a model, install packages, start a service, or enable an always-on microphone.
- The first runnable open-STT path is now the official `docker.io/rhasspy/wyoming-whisper` container on `ctos-core`, not the direct upstream venv. The venv path failed under Python 3.14 while building `pysilero-vad`; the container `--help` passed and started as a temporary localhost-only Wyoming backend on port `10301`.
- A synthetic French WAV reached CTOS through the Wyoming client and route path. Live T480 microphone samples reached the backend but returned empty transcripts, so audio capture/gain cleanup is the current blocker before daemon/service work.
- Follow-up live tests with the T480 mic calibrated below clipping showed that the Wyoming route and backend still work, but the current live capture is not yet a reliable Jarvis input: unnormalized samples can return empty transcripts, while aggressively normalized low-speech/noise samples can trigger classic Whisper hallucinations such as `Sous-titres réalisés...`. The next implementation should add a silence/hallucination guard plus controlled pre-STT normalization/VAD before trying to tune phrases.
- `ctos-voice-v2 stp-transcribe` now has a basic transcript guard. It blocks empty transcripts, bad audio states, and known Whisper silence/noise hallucinations before CTOS routing; `--no-transcript-guard` exists only as a debug bypass.
- `ctos-voice-v2 stp-transcribe --preprocess auto` now runs a simple energy-based voice activity check, trims around active audio, and normalizes only voice-like samples before STT. It refuses low-activity samples before contacting Whisper, so silence/room noise is not amplified into hallucinated text. `--preprocess off` is retained for raw backend debugging.
- `ctos-voice-v2 open-stt status|start|logs|stop` now manages the temporary `docker.io/rhasspy/wyoming-whisper` smoke backend on `ctos-core` without creating a service. It keeps the Wyoming port bound to `127.0.0.1:10301`, stores model data under `/srv/ctos/models/open-stt`, and prints the matching `stp-transcribe --preprocess auto --route` test command.
- Live manager verification on 2026-07-07: `open-stt status --json` found image and paths ready, no container, and port `10301` free; `open-stt start --json` started `ctos-open-stt-smoke`; `open-stt logs` showed `Ready`; `open-stt stop --json` removed the container and freed the port. No open-STT container was left running.
- Readiness fix 2026-07-07: `open-stt start` now waits for the container logs to report `Ready` before returning success. The first synthetic `ctos-jarvis listen --from-wav` test hit a `Broken pipe` when the socket was open but the backend was not actually ready. After the fix, the same synthetic WAV returned a transcript through Wyoming and CTOS refused agenda staging because the synthetic transcript was too degraded to parse safely. This verifies transport/readiness, not human recognition quality.
- `ctos-jarvis listen` is now the operator shortcut for the open-ended STT rail. It checks/starts the temporary open-STT backend, records one T480 push-to-talk sample, opens the localhost SSH tunnel to `ctos-core`, routes the transcript through CTOS, and stops the backend again if this command started it. `--keep-backend` keeps it warm for repeated prompts, and `--save-agenda` stages recognized agenda requests as pending proposals rather than writing agenda state directly.
- `ctos-jarvis calibrate` is now the preferred live test loop. It wraps the open-STT listen path, keeps the raw and preprocessed WAVs by default, and prints a readable report with mic/STT audio levels, transcript, transcript guard, CTOS route, and any agenda proposal. It does not save an agenda proposal unless `--save-agenda` is explicit.
- Transcript guarding now also blocks unreadable normalized text, repeated non-speech symbol runs, and high symbol-noise transcripts before CTOS routing. This was added after a synthetic French TTS sample produced degraded text with repeated non-speech symbols; the correct behavior is fail-closed until a human sample proves the path.
- `ctos-audio` now includes microphone source controls (`mic-status`, `mic-set`, `mic-up`, `mic-down`, `mic-mute`) so capture gain can be adjusted without ad hoc `wpctl` commands.
- `ctos-voice-v2 doctor` is now the preferred read-only resume check. It summarizes local readiness, `ctos-core` reachability, temporary Home Assistant status, token readiness, Speech-to-Phrase runtime status, and open-STT directory readiness, then prints one next action.
- `ctos-voice-v2 stp-transcribe` is the first end-to-end operator test command for the mature deterministic rail. It can record a temporary WAV on the T480, open a temporary SSH tunnel to the Speech-to-Phrase Wyoming port on `ctos-core`, send the WAV, and route the returned transcript through CTOS with either plan-only `--route` or Tier 0/1 `--execute-safe`.
- `ctos-voice-v2 wyoming-selftest` is a local mock transport test. It starts a one-shot Wyoming-compatible mock server, sends a temporary WAV through the same client code, returns a fixed transcript such as `agenda`, and routes it through CTOS. It proves event framing and planner handoff only; it does not prove real speech recognition quality.
- `ctos-voice assistant` and `ctos-voice assistant-once` are the temporary usable Jarvis surface while Home Assistant onboarding/token creation remains blocked. They try CTOS safe actions first, stage agenda proposals only when requested, and otherwise fall back to the local model with no tool authority.
- `ctos-jarvis stack` now renders the selected mature local/open-source Jarvis stack from `ai/jarvis_stack.json`. This records that Home Assistant Assist/Wyoming is the primary voice ecosystem target, Speech-to-Phrase is the deterministic rail, Wyoming Whisper/faster-whisper is the open-STT rail, Piper is planned TTS, Ollama on `ctos-core` is the current model runtime, and CTOS remains the only action authority.

## Sources Checked

- Home Assistant local voice assistant docs: https://www.home-assistant.io/voice_control/voice_remote_local_assistant/
- Home Assistant voice control docs: https://www.home-assistant.io/voice_control/
- Home Assistant custom sentences docs: https://www.home-assistant.io/voice_control/custom_sentences/
- Home Assistant custom sentence YAML docs: https://www.home-assistant.io/voice_control/custom_sentences_yaml/
- Home Assistant Linux/Container installation docs: https://www.home-assistant.io/installation/linux
- Home Assistant WebSocket API docs: https://developers.home-assistant.io/docs/api/websocket/
- Speech-to-Phrase repo: https://github.com/OHF-Voice/speech-to-phrase
- Wyoming protocol repo: https://github.com/rhasspy/wyoming
- Wyoming Piper repo: https://github.com/rhasspy/wyoming-piper
- Wyoming Whisper image: https://hub.docker.com/r/rhasspy/wyoming-whisper
- OpenVoiceOS repo: https://github.com/OpenVoiceOS/OpenVoiceOS
- Open Interpreter repo: https://github.com/OpenInterpreter/open-interpreter
- GLM repo lookup: https://github.com/zai-org/GLM-5
- AirLLM reference implementation: https://github.com/lyogavin/Anima/tree/main/air_llm
- Leon repo: https://github.com/leon-ai/leon

## Next Loop

1. Run `ctos-jarvis calibrate` with a real human push-to-talk agenda phrase.
2. If the report is readable and the proposal is correct, rerun `ctos-jarvis calibrate --save-agenda`, then use typed `ctos-jarvis review` and `ctos-jarvis confirm latest --yes`.
3. If the transcript is still weak, adjust capture/preprocessing with `ctos-audio` and `ctos-voice-v2 mic-check` before adding phrase synonyms.
4. Complete the temporary Home Assistant onboarding/token blocker only when the deterministic Speech-to-Phrase rail is worth testing again.
5. Only after the deterministic rail and open-ended rail both pass, consider persistent voice services or always-on wake-word work.

## Verification

Completed on 2026-07-07:

- `python3 -m json.tool ai/voice_backends.json`
- `python3 -m json.tool ai/voice_intents_fr.json`
- `python3 -m py_compile scripts/ctos-voice-v2 scripts/ctos-voice scripts/ctos-ai`
- `ctos-voice-v2 plan`
- `ctos-voice-v2 status`
- `ctos-voice-v2 intents`
- `ctos-voice-v2 next-commands`
- `ctos-voice-v2 match agenda`: matched `ctos_agenda -> ctos-ai plan-day`
- `ctos-voice-v2 match "ouvre vms"`: matched `ctos_open_vms -> ctos-ai open-vms`
- `ctos-voice-v2 export-phrases --format jsonl`: emitted phrase rows for backend handoff
- `scripts/ctos-install-user-bin`: linked `ctos-voice-v2` under `~/.local/bin`
- `ctos-voice command --no-speak agenda`: matched the catalog and opened the day plan
- `ctos-voice command --no-speak "a jenda"`: matched the catalog and opened the day plan
- `ctos-voice-v2 sample-plan --dir /tmp/ctos-voice-samples-test --write-manifest`: generated a temporary manifest
- `ctos-voice-v2 regression --manifest /tmp/ctos-voice-regression.jsonl`: passed deterministic transcript fixtures
- `ctos-voice-v2 export-phrases --format ha-sentences`: emitted Home Assistant custom-sentence YAML
- `ctos-voice-v2 export-phrases --format ha-map`: emitted the CTOS sidecar intent map
- `ctos-voice-v2 export-backend --backend home-assistant --dir /tmp/ctos-voice-backend-test`: wrote a complete inert backend bundle
- `ctos-voice-v2 export-backend --backend speech-to-phrase --dir /tmp/ctos-voice-backend-stp-test`: wrote the same bundle shape for Speech-to-Phrase
- `python3 -m json.tool /tmp/ctos-voice-backend-test/ctos_intent_map.json`: validated the generated map
- `ctos-voice-v2 validate-backend --dir /tmp/ctos-voice-backend-test`: verified 6 backend intents and all CTOS phrases/commands/tiers
- `ctos-voice-v2 validate-backend --dir /tmp/ctos-voice-backend-test --json`: emitted machine-readable validation results
- `ctos-voice-v2 backend-commands --backend speech-to-phrase --dir /tmp/ctos-voice-backend-test`: printed the non-mutating backend handoff commands
- `ctos-voice-v2 backend-preflight --backend speech-to-phrase --dir /tmp/ctos-voice-backend-preflight-test`: verified bundle readiness and reported the missing runtime/Home Assistant context as blockers rather than silently pretending a full backend test had run
- `ctos-voice-v2 backend-preflight --backend speech-to-phrase --dir /tmp/ctos-voice-backend-preflight-test --runtime-python /tmp/ctos-speech-to-phrase-smoke-venv/bin/python`: verified import/help and `hassil` YAML parsing, identified `fr_FR-rhasspy`, and reported missing Speech-to-Phrase model/tools cache plus missing Home Assistant context as the remaining blockers
- `ctos-voice-v2 stp-cache --runtime-python /tmp/ctos-speech-to-phrase-smoke-venv/bin/python`: rendered the expected local `/srv/ctos` cache paths and confirmed they are absent
- `ctos-voice-v2 stp-cache --runtime-python /tmp/ctos-speech-to-phrase-smoke-venv/bin/python --target-probe`: reached `ctos-core` over SSH outside the sandbox and confirmed the same cache paths are absent there
- `ctos-voice-v2 stp-container-plan`: rendered the official container-first test plan without starting a container
- `ctos-voice-v2 stp-container-plan --target-probe`: reached `ctos-core`, found `/usr/bin/podman`, and confirmed `/srv/ctos/voice/backend/speech-to-phrase/custom_sentences` is present while training/model caches are still absent
- `ctos-voice-v2 stp-container-inspect`: pulled the fully qualified `docker.io/rhasspy/wyoming-speech-to-phrase` image on `ctos-core`, verified `--help`, and recorded digest `sha256:9ef75f4a4f21484ebbe7e0c0f81a53bb7670e6b57430c7d8fa632239ba318289`
- Image filesystem inspection: `ENTRYPOINT=["bash","/run.sh"]`; `/run.sh` uses `--models-dir /models`, `--train-dir /train`, and image-internal `--tools-dir ./tools`
- `mkdir -p /srv/ctos/cache/speech-to-phrase/train /srv/ctos/models/speech-to-phrase`: created cache directories on `ctos-core` as `ctos:ctos` with setgid permissions
- `ctos-voice-v2 export-backend --backend speech-to-phrase --dir /tmp/ctos-voice-backend`: regenerated the inert CTOS bundle
- `ctos-voice-v2 validate-backend --dir /tmp/ctos-voice-backend`: verified 6 Tier 0/1 intents
- `tar -C /tmp/ctos-voice-backend -cf - . | ssh ... 'tar -C /srv/ctos/voice/backend/speech-to-phrase -xf -'`: copied the validated bundle to `ctos-core`
- local and remote `sha256sum` values matched for `README.md`, `ctos_intent_map.json`, and `custom_sentences/fr/ctos.yaml`
- `ctos-voice-v2 hass-context-plan`: rendered the temporary Home Assistant context plan without starting a service
- `ctos-voice-v2 hass-context-plan --json`: emitted the same plan as JSON
- `ctos-voice-v2 hass-context start`: pulled `ghcr.io/home-assistant/home-assistant:stable`, started `ctos-ha-test`, and kept the UI/API bound to `127.0.0.1:8123`
- `ctos-voice-v2 hass-context status --json`: verified image present, container running, port busy, and HTTP `302`
- Home Assistant image inspection on `ctos-core`: image id `ceb81d836a0b125a4ec14a754231a5dd1cc5f2feb2594107320c3cea345dd9d1`, digest `sha256:21e0d1bae299819d8cf4ef8aa197593205a5fae51c69031c13bfd1eac8c56204`, size `2486193643`
- `ctos-voice-v2 hass-context logs --logs-tail 20`: confirmed first startup; rootless DHCP watcher warning is visible but not blocking for the websocket/token test
- `ctos-voice-v2 wyoming-selftest --json`: verified local mock Wyoming transport and CTOS route handoff without Home Assistant, Speech-to-Phrase, microphone input, token storage, or network service exposure.
- `ctos-voice-v2 hass-context tunnel-start`: idempotently verifies or starts the T480 localhost-only SSH tunnel to the temporary Home Assistant API before browserless onboarding.
