# CTOS Voice Console

Local browser UI for slow voice chat with CTOS/OpenJarvis.

## Run

```bash
cd ~/T480
scripts/ctos-voice-console serve
scripts/ctos-voice-console url
```

Open:

```text
http://127.0.0.1:8770
```

Optional:

```bash
scripts/ctos-install-user-bin --force
source ~/.bashrc
ctos-voice-console serve
```

## Modes

- `Chat`: sends transcript/text to `ctos-openjarvis ask`.
- `Brief`: returns a deterministic CTOS status from local scripts.
- `Codex`: creates a `ctos-openjarvis codex-brief` handoff.
- `Action`: previews a deterministic CTOS action and can place it in an
  explicit approval queue.

`Chat` also auto-routes obvious status/config/network requests to the same
read-only CTOS brief path. No mode edits files, writes agenda state, starts VMs,
or opens network listeners beyond `127.0.0.1`.
Long brief answers are shown fully on screen; TTS speaks only a compact summary.

The `Brief` path reads:

```bash
ctos-ai brief
ctos-netwatch status
ctos-openjarvis status --json
```

## Action Queue V0

`Action` mode is not a free-form shell. It only routes a small allowlist:

- Kali: start, shutdown, console, checkpoint.
- Core/tour: sync repo, apply service layout.
- Agenda: save a pending agenda proposal.

Flow:

1. Speak or type a request in `Action`.
2. Review the preview in `Answer` / `Action Queue`.
3. Click `Queue last` only if the preview matches.
4. Select the pending item.
5. Click `Approve` to execute, or `Reject` to drop it.

The queue reuses existing CTOS stores:

```bash
ctos-ai approvals --status pending
ctos-ai agenda-proposals --status pending
```

Execution still goes through:

```bash
ctos-ai approve <id>
ctos-ai agenda-confirm <id> --yes
```

The browser API never accepts arbitrary commands. Unknown speech remains a
preview and is not queued.

Common STT misses for `Kali` are normalized in Action mode before queueing:

```text
cali, callie, kalli, kalie, kelly, khali, qali, quali, ka li, qu a lit -> kali
```

There are also quick buttons for the high-frequency Kali actions:

- `Start Kali`
- `Open Kali`
- `Stop Kali`
- `Checkpoint`

These buttons only create a pending queue item. They still require selecting
the item and clicking `Approve` before anything executes.

## Audio Path

Browser microphone audio is recorded with `MediaRecorder`, sent to the local
server, converted to mono 16 kHz WAV with `ffmpeg`, then transcribed through:

```bash
scripts/ctos-voice transcribe-file /tmp/sample.wav --json
```

Temporary audio is deleted after each request unless:

```bash
CTOS_VOICE_CONSOLE_KEEP_AUDIO=1 scripts/ctos-voice-console restart
```

## Security Boundary

- Bind address: `127.0.0.1`.
- Audio temp path: `/tmp/ctos-voice-console`.
- Max audio body: 20 MiB by default.
- Local answer backend: existing CTOS/OpenJarvis/Ollama tunnel.
- Action authority: localhost-only deterministic queue plus explicit click
  approval; no arbitrary shell endpoint.

## Voice Quality Axis

Current spoken output used to fall back to `espeak-ng`/`espeak`, which is not
good enough for daily Jarvis use.

Piper is now the first local voice trial. It is installed in a user venv and
stores model files outside Git:

```text
~/.local/share/ctos-ai/venvs/piper
~/.local/share/ctos-ai/tts/piper/fr_FR-siwis-medium
```

Commands:

```bash
ctos-voice tts-probe
ctos-voice setup-piper --print-commands
ctos-voice setup-piper --yes
ctos-voice tts-test --engine piper
ctos-voice say --engine piper "Bonjour, test CTOS."
```

The Voice Console and `ctos-voice-ptt` use Piper automatically only when the
Piper binary and voice files are present. To force a different engine for a
debug session:

```bash
CTOS_VOICE_ENGINE=espeak-ng ctos-voice-console restart
CTOS_VOICE_ENGINE=piper ctos-voice say "Test de voix locale."
```

Cloud TTS remains out of scope unless explicitly accepted later.

## Commands

```bash
ctos-voice-console serve
ctos-voice-console status
ctos-voice-console stop
ctos-voice-console restart
ctos-voice-console open
ctos-voice-console url
```
