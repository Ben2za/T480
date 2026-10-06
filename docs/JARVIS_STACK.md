# CTOS Jarvis Stack

CTOS will not become useful by adding one voice synonym at a time. The current
direction is:

```bash
ctos-jarvis stack
ctos-jarvis mature-plan
ctos-jarvis mature-check
ctos-jarvis status
ctos-jarvis inbox
ctos-jarvis request "ajoute acheter du pain demain 30 min priorite 4"
ctos-jarvis chat --brief "resume la situation et propose une prochaine action"
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
ctos-jarvis reject latest --reason "not useful"
```

The stack is hybrid:

- Home Assistant Assist / Wyoming as the mature local voice ecosystem target;
- Speech-to-Phrase as the deterministic command rail;
- Wyoming Whisper / faster-whisper as the natural STT rail;
- Piper as the current installed local French TTS rail;
- Ollama on `ctos-core` as the current small local model runtime;
- CTOS proposals and approvals as the only action authority.

## EliteBook Voice Console POC

The 2026-07-18 LAN POC keeps Firefox and the microphone on `BXEB`, forwards its
loopback `127.0.0.1:8770` over key-based SSH, and keeps the Voice Console,
Vosk, local structured compiler, validation, Codex CLI, and Piper renderer on
the T480. No HTTP listener is widened and raw audio is deleted by default.

Codex mode is preview-first: local speech/text becomes a closed canonical
read-only task spec, the operator may edit and revalidate it, and a one-use
digest-bound token authorizes only that exact spec. The legacy raw handoff is
disabled. Live Codex execution is also disabled by default because read-only
does not prevent the reviewed spec and permitted repository files from being
sent to OpenAI; `CTOS_VOICE_CODEX_RUN_ENABLED=1` is reserved for an informed
acceptance window.

`Speak` now requests a bounded no-store Piper WAV from the T480 and plays it in
EliteBook Firefox; it does not invoke T480-side playback. Current operator
acceptance steps and the outside-home boundary are recorded in
`context/26_elitebook_voice_codex_test_plan.md`.

`ctos-jarvis mature-plan` is the operator answer to "should we keep tuning
words by hand or adopt a sophisticated open-source local stack now?". It renders
the selected adoption path from `ai/jarvis_stack.json`: Home Assistant
Assist/Wyoming as the voice bus, Wyoming Whisper/faster-whisper as the natural
French STT rail, Speech-to-Phrase as the deterministic command rail, Piper as
the installed T480 TTS default, and Ollama on `ctos-core` as the first local model runtime. It also
marks Open Interpreter/01, OpenVoiceOS, GLM-family models, and AirLLM-style
offload as sandbox/reference work unless they fit behind CTOS proposals and
typed approvals.

2026-07-08 refresh: keep this path. The missed `agenda` recognition is a
benchmarking problem, not a signal to build a custom full voice stack from
scratch. Capture a reusable corpus, compare local fallback versus
Whisper/Wyoming, and let the mature local voice substrate handle speech while
CTOS keeps action authority.

`ctos-jarvis mature-check` is the matching read-only preflight. Default mode
checks the local voice/Jarvis foundation, audio controls, and reusable sample
manifest without touching services or the agenda. Add `--full` to include
`ctos-core` SSH/backend probes, and `--prefer deterministic` when the next
priority is the Home Assistant/Speech-to-Phrase rail instead of open-STT.

`ctos-jarvis status` is the compact mission view. It reads mature readiness,
corpus/improvement state, the next corpus phrase, and pending agenda proposals,
then prints one next operator action. It is read-only.

`ctos-jarvis stack-check` is the read-only integrity gate between the selected
Jarvis stack manifest and the French voice intent catalog. It fails if
`ai/jarvis_stack.json` looks like an intent file or if `ai/voice_intents_fr.json`
looks like the stack manifest.

`ctos-jarvis daily` is the daily text-first cockpit. It aggregates
`stack-check`, `ctos-ai brief`, `ctos-agenda plan-day`, pending proposal review,
and `ctos-jarvis status` into one read-only report. It is meant to become the
stable text surface that voice can feed later.

`ctos-jarvis inbox` is the compact mutation queue. It is read-only and shows
pending agenda proposals plus generic CTOS approval records in one place. Agenda
items still use `ctos-jarvis review` then `ctos-jarvis confirm latest --yes` or
`ctos-jarvis reject latest`; after a successful agenda decision, the wrapper
returns to the inbox unless `--no-inbox` is explicit. Generic approvals still
use `ctos-ai show`, `ctos-ai approve --dry-run`, then explicit operator
approval.

`ctos-jarvis draft "..."` is the text-first staging rail. It routes natural
text through `ctos-ai route-text`, prints the matched deterministic intent or
agenda proposal, and stops there. With `--save`, it saves only a recognized
agenda proposal as pending approval; it never writes the final agenda task. The
write path stays separate: `ctos-jarvis review`, then
`ctos-jarvis confirm latest --yes` after human review. Reject with
`ctos-jarvis reject latest --reason "..."` when the proposal should leave the
queue without touching the agenda.

`ctos-jarvis request "..."` is the daily text-first shortcut above `draft`.
It routes the text, auto-stages only recognized agenda proposals as pending,
then shows `ctos-jarvis inbox`. It does not execute safe desktop/VM actions and
does not write the final agenda task. Use `--no-save` for route-only behavior,
`--no-inbox` when another surface will show the queue, and `--json` for scripted
callers.

`ctos-jarvis chat "..."` is the local read-only conversation wrapper above
`ctos-ai-chat`. It uses a CTOS system prompt that tells the model to explain,
plan, and propose CTOS commands without claiming execution. `--brief` injects
the current `ctos-ai brief` into that system prompt. `--plan` shows the lower
level command without touching the model runtime, and `--json` wraps the result
for UI callers. This is a conversation surface, not an action authority.

`ctos-jarvis calibrate` is the normal live test loop. It records one push-to-talk
sample or uses a WAV, keeps the raw/preprocessed debug WAVs by default, reports
audio level, transcript guard, CTOS draft route, best route candidate,
agenda-save refusal reason, and any agenda proposal. By default, the STT
transcript is staged through `ctos-jarvis draft --source stt`; it does not write
an agenda proposal unless `--save-agenda` is explicit, and it never writes the
final agenda task.

`ctos-jarvis session` is the repeated operator loop. It runs several calibration
rounds, keeps open-STT running between them, and stops it at the end unless
`--keep-backend` is explicit. It runs a read-only preflight first: microphone
status, open-STT status, and agenda review. The default preflight warns but does
not block; use `--strict-preflight` when the session should stop before
recording if a check fails. Use `ctos-jarvis session --save-agenda` only when the
live transcript shape is already readable enough to stage proposals. With
`--save-agenda`, the session shows `ctos-jarvis inbox` at the end, but typed
`ctos-jarvis confirm latest --yes` is still required to write the agenda.
`--no-inbox --review` keeps the older agenda-only review view available.

`ctos-jarvis run` is the daily shortcut above `session`. It uses the open-STT
session loop, sends transcripts through the `draft` rail, stages agenda
proposals by default, shows the read-only inbox, and prints the typed
confirmation command. It does not approve proposals or add model/voice
authority. Use `ctos-jarvis run --plan` to inspect the lower-level session
command before running it.

`ctos-jarvis improve` is the shortest corpus improvement loop. By default it is
read-only: it runs `triage`, reports the current verdict, and prints the exact
next command. Use `ctos-jarvis improve --run` when you want it to run that next
step. If the corpus is empty or incomplete, the next step is guided microphone
collection with strict audio preflight. If the corpus is ready, the next step is
`evaluate --backend both`. It refuses ambiguous repair states by pointing back
to `samples`/manifest inspection instead of mutating files.

`ctos-jarvis collect-next` captures only the next missing or weak corpus phrase.
Use it when the full guided corpus capture is too much context at once. It is
plan-only by default; `ctos-jarvis collect-next --run` records the selected
phrase and then points back to corpus/next checks.

`ctos-jarvis bootstrap` is the one-step operator loop. It reads `status`, picks
the first next action, and shows it without changing state. With
`ctos-jarvis bootstrap --run`, it executes exactly that one existing CTOS
command and then rechecks status. JSON run mode refuses interactive audio unless
`--yes` is explicit.

`ctos-jarvis sample "..."` records or registers a labeled voice sample under
`~/.local/state/ctos/jarvis-samples`, outside the repo. Use it when a word like
`agenda` fails in a live test: capture once, then replay the same WAV through
`ctos-jarvis calibrate --from-wav ...` while swapping STT backends or tuning
audio. The manifest is JSONL so future regression tests can compare the same
audio against Whisper, Speech-to-Phrase, or another local backend. Fixed
commands may set `intent_id`; open-ended samples use `expected_text` so the
transcript itself can be scored even when no CTOS command should match.

`ctos-jarvis collect` is the shortcut for building a small reusable voice corpus
instead of tuning one missed word at a time. The default `core` preset records
the current critical surface: `agenda`, `brief`, `ouvre desk`, `ouvre vms`, and
one natural agenda request. It waits before each phrase, stores samples in the
same manifest as `sample`, adds fixed `intent_id` values for known CTOS commands,
then prints the sample inventory and regression commands. It runs a read-only
audio preflight first (`ctos-audio status`, `ctos-audio mic-status`, and
`ctos-audio doctor --json`) so bad volume/microphone state is visible before
recording the suite. The doctor output also flags restricted contexts that
cannot read the live desktop DBus/PipeWire session. The default only warns; use
`--strict-preflight` to stop before recording, or `--no-preflight` when
intentionally debugging the capture path. Use `--plan` first to see the exact
phrase list, and `--run-regression` only when you want it to test the captured
corpus immediately.

`ctos-jarvis corpus` is the read-only gate after collection. It checks the
default manifest, verifies the expected preset coverage, flags missing WAV files
or weak audio states, and prints the next command. The normal progression is:
`collect` when empty, `corpus` when samples exist, then `regression` when the
corpus is ready.

`ctos-jarvis triage` is the read-only operator verdict above `corpus` and
`samples`. It does not record audio, transcribe, start open-STT, or mutate
agenda state. It reads the reusable sample manifest, reports a concrete verdict
such as `capture_corpus`, `complete_corpus`, `recapture_weak_audio`, or
`benchmark_backends`, then prints the smallest next command.

`ctos-jarvis evaluate` is the one-button measurable path after `collect`. It
first runs the same corpus gate, refuses to run recognition tests on an empty or
broken corpus, then launches sample regression only when the corpus is ready.
Use `--backend both` when the local fallback and the open-STT/Wyoming rail should
be compared from the same samples.

Run the same sample manifest against the current fallback recognizer or the
open-STT/Wyoming rail:

```bash
ctos-jarvis collect --plan
ctos-jarvis stack-check
ctos-jarvis daily
ctos-jarvis inbox
ctos-jarvis request "ajoute acheter du pain demain 30 min priorite 4"
ctos-jarvis chat --brief "resume la situation et propose une prochaine action"
ctos-jarvis draft "ajoute acheter du pain demain 30 min priorite 4"
ctos-jarvis draft "ajoute acheter du pain demain 30 min priorite 4" --save
ctos-jarvis bootstrap
ctos-jarvis bootstrap --run
ctos-jarvis collect
ctos-jarvis corpus
ctos-jarvis triage
ctos-jarvis evaluate
ctos-jarvis evaluate --backend both
ctos-jarvis samples
ctos-jarvis regression
ctos-jarvis regression --backend open-stt --target-tunnel
ctos-voice-v2 regression --manifest ~/.local/state/ctos/jarvis-samples/manifest.jsonl
ctos-voice-v2 regression --manifest ~/.local/state/ctos/jarvis-samples/manifest.jsonl --backend open-stt --target-tunnel
```

`ctos-jarvis regression` is only a wrapper around `ctos-voice-v2 regression`
with the default Jarvis manifest path filled in. The open-STT regression expects
the temporary Wyoming backend to be reachable; it does not install a daemon or
grant any extra action authority.

See `context/22_jarvis_stack_selection.md` and `ai/jarvis_stack.json` for the
full current selection.
