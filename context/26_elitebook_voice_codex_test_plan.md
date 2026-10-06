# EliteBook-to-T480 Voice-to-Codex Test Plan

Date: 2026-07-18
Status: LAN implementation and local verification complete; one informed
live-Codex approval and human audio checks pending

## Objective

Prove the smallest useful voice path from the operator's Ubuntu EliteBook
(`BXEB`) while the T480 remains at home, then add the missing validated
spec-only Codex boundary without exposing a home service to the public
Internet.

This plan separates four different claims that must not be confused:

1. the current browser/microphone transport works;
2. a synthetic validated spec can reach Codex read-only;
3. real speech can be compiled, reviewed, and sent to Codex without the raw
   transcript;
4. the result can be heard on the EliteBook and reached from outside the home.

## Verified Current Topology

```text
BXEB Firefox microphone
  -> http://127.0.0.1:8770 on BXEB
  -> OpenSSH local forward
  -> 127.0.0.1:8770 Voice Console on T480
  -> ffmpeg conversion and local Vosk STT on T480
  -> local Ollama structured task-spec compiler
  -> deterministic validation plus editable operator preview
  -> disabled-by-default read-only Codex execution gate

T480 Piper render-to-WAV
  -> loopback HTTP audio/wav response
  -> BXEB Firefox playback
```

- `BXEB` currently uses `192.168.1.24`, user `ben`.
- The T480 currently uses `192.168.1.21`, user `operator`.
- Key-only SSH from `BXEB` back to the T480 was verified on the LAN on
  2026-07-18.
- The Voice Console binds to T480 loopback and rejects non-loopback POST
  clients. An SSH local forward preserves that boundary.
- Browser recordings are converted to 16 kHz mono WAV and deleted after the
  request while `CTOS_VOICE_CONSOLE_KEEP_AUDIO` remains disabled.
- The legacy raw `codex-brief` path is disconnected. Codex mode now returns a
  validated canonical spec and digest for review; it never implicitly starts
  Codex or returns the raw STT transcript to the page.
- Live execution is fail-closed unless the Voice Console is deliberately
  started with `CTOS_VOICE_CODEX_RUN_ENABLED=1`. The default remains disabled
  pending informed approval that the reviewed spec and permitted repository
  content may be sent to OpenAI.
- `/api/voice/synthesize` renders Piper to a bounded temporary WAV and returns
  it to the browser with `Cache-Control: no-store`; the server does not play it.
  The older `/api/voice/say` route remains for compatibility but is no longer
  used by the Voice Console UI.

## Implementation Result: 2026-07-18

- Post-reboot key-only SSH passed in both directions between `BXEB/ben` and
  `ctos-node/operator`. The EliteBook owns only a loopback local forward to the
  T480's loopback Voice Console, and Firefox was reopened on that URL.
- The console manager now ignores a stale PID-file entry and falls back to the
  verified matching process. A final `restart` stopped and started the service
  cleanly, then its status passed again through the EliteBook tunnel.
- One real browser microphone request passed through the tunnel with HTTP 200,
  proving the EliteBook capture, SSH, ffmpeg, Vosk, and response path after the
  power interruption.
- The versioned closed schemas, deterministic validators, spec-only runner,
  local structured compiler, editable preview/revalidation flow, one-use
  digest-bound approval token, and browser Piper delivery are implemented.
- A live local Qwen compiler check returned a valid spec. Its first output
  broadened an explicitly named file to directories, so a deterministic
  explicit-path scope ceiling was added and the repeated check restricted
  `allowed_scope` to `ai/voice_task_spec.py` exactly.
- A live preview through the EliteBook tunnel returned the exact workspace,
  read-only class, canonical spec, digest, and ten-minute token without
  exposing the source text. A live Piper response through the same tunnel was
  `audio/wav`, 117292 bytes, had valid RIFF/WAVE headers, and was marked
  `no-store`.
- The focused suite passes 48 tests. Static Python, JavaScript, JSON, and diff
  checks are part of the final verification record.
- The attempted first live `codex exec` smoke did not start. The execution
  approval gate correctly stopped at the external-disclosure boundary: even a
  read-only task can send the normalized spec and allowed repository files to
  OpenAI. The console now also enforces this as a disabled-by-default runtime
  gate. The live acceptance check remains pending explicit informed approval.
- Human confirmation that Piper is audible in EliteBook Firefox and the five
  short French STT/spec samples remain operator checks; transport-level success
  does not prove perceived audio quality or recognition quality.

### Missing-response incident: 2026-07-19

The operator's Chat/Codex requests reached the T480 and returned HTTP 200, but
the browser still called legacy `/api/voice/say`; the observed Piper sound on
the T480 independently confirmed that Firefox had retained the obsolete
client. Static responses now use no-store/no-cache headers, versioned asset
URLs, and a shared client/server build identifier. Final build
`2026-07-19.3` was fetched in a new EliteBook Firefox window. The legacy
`/api/voice/say` route now returns HTTP 410 without invoking T480 playback, so
an old page fails visibly instead of playing on the wrong PC.

The UI also captures the selected mode at submission and disables mode changes
until completion, scrolls a Codex preview into view, shows request errors in
the Answer panel, and rejects an empty successful Chat output. Post-fix tunnel
smokes returned Chat `OK`, a local read-only Codex preview, and HTTP 200
`audio/wav` from `/api/voice/synthesize`. The cloud run gate stayed disabled.
The expanded focused suite passes 52 tests.

## Test Levels And Honest Timing

| Level | Acceptance claim | Work remaining | Focused elapsed time |
| --- | --- | --- | --- |
| A | Existing EliteBook microphone reaches the T480 and returns a transcript plus CTOS Brief | Start console, create tunnel, grant browser microphone, run one phrase, clean up | 10-20 min clean; 30-45 min with browser/tunnel/model diagnosis |
| B | A synthetic secret-free task spec reaches real Codex safely | Local implementation and mocks pass; informed live cloud invocation pending | 4-8 h original estimate |
| C | Real voice reaches a reviewed spec without raw transcript | Compiler, clarification/edit preview, endpoints, and privacy tests pass; five human samples remain | 8-16 h original total estimate |
| D | Piper result is audible on the EliteBook | Render/HTTP/browser path passes; human audibility confirmation remains | +2-4 h original estimate |
| E | Same private workflow works outside home | Install and constrain a private overlay, verify SSH tunnel over it, reboot and sleep/recovery behavior | +1.5-3 h after provider approval |

A one- or two-hour estimate for the complete compliant voice-to-Codex chain
would omit the privacy boundary or its tests. A practical rush target is:

- current transport proof in the first 20-45 minutes;
- real synthetic spec-to-Codex proof in roughly half a focused day;
- compliant voice-to-Codex with operator preview in one long day or two normal
  workdays;
- complete local experience including EliteBook Piper playback in about
  10-20 focused engineering hours.

The speech backend benchmark, Kokoro comparison, model bake-off, always-on
wake word, MCP, and workspace-write Codex are not prerequisites for this POC.

## Level A: Existing-Stack LAN Smoke

On the T480:

```bash
cd /home/operator/T480
scripts/ctos-voice tts-probe --json
scripts/ctos-voice-console serve
scripts/ctos-voice-console status
```

On `BXEB`:

```bash
ssh -F /dev/null -N -o ExitOnForwardFailure=yes \
  -L 127.0.0.1:8770:127.0.0.1:8770 operator@192.168.1.21
firefox http://127.0.0.1:8770/voice.html
```

Manual test:

1. Grant microphone permission only to the loopback page.
2. Select `Brief`, record `affiche le statut CTOS`, then stop.
3. Pass only if both Transcript and Answer are non-empty and plausible.
4. Replay may verify the EliteBook recording locally.
5. `Speak` must now play the synthesized Piper result in EliteBook Firefox,
   subject to the browser's normal manual-play/autoplay policy.
6. In `Codex` mode, stop at the canonical preview until the separate informed
   external-disclosure approval has been given. The disabled run button is the
   expected default state.

Cleanup:

```bash
# Stop the foreground SSH process on BXEB with Ctrl-C.
scripts/ctos-voice-console stop
```

No router/firewall change is required. Do not bind the console to `0.0.0.0`.

## Levels B-C: Minimum Compliant Codex Slice

### Versioned boundary

Add a JSON task schema with `additionalProperties: false` and only bounded,
normalized fields:

- schema version;
- goal;
- exact workspace;
- allowed scope;
- constraints;
- requested deliverable;
- acceptance checks;
- `read_only` approval class;
- clarification state.

The deterministic validator must reject unknown keys, transcript/audio fields,
shell/command fields, credentials and secret patterns, excessive sizes,
unresolved ambiguity, and any workspace other than the exact resolved repo.
Canonical JSON plus a digest becomes the reviewable handoff artifact.

### Local compiler

Use the existing local Ollama model only as an untrusted structured-spec
compiler. The raw transcript may exist in memory for local STT/compiler work,
but must not appear in the returned spec, logs, repository, or Codex stdin.
Malformed, ambiguous, or unavailable compiler output stops for operator
correction; it never falls through silently.

### Codex adapter

The first supported runner is equivalent to:

```bash
codex exec --ephemeral --ignore-user-config \
  -c project_doc_max_bytes=0 \
  -c 'web_search="disabled"' \
  --sandbox read-only \
  -C /home/operator/T480 \
  --output-schema /home/operator/T480/ai/codex_readonly_result.schema.json -
```

Only a fixed instruction and the revalidated canonical spec are sent over
stdin. User configuration is ignored, automatic project-instruction loading is
disabled, and web search is disabled for this runner. The fixed instruction
permits only declared `allowed_scope` reads and requires clarification instead
of widening scope. This is a model instruction, not an OS-enforced per-file
read jail: the read-only workspace remains technically readable. Plan mode
shows the exact arguments, spec, and digest without running. Run mode requires
a distinct visible confirmation. Authentication, quota, network, validation,
timeout, and non-zero exit errors remain visible; Ollama must never become a
hidden substitute for Codex.

### Verification gates

- valid synthetic, unknown-key, banned-field, oversize, secret-sentinel,
  unresolved-clarification, and path-traversal tests;
- stable canonical form and digest;
- mocked process test proving exact Codex flags and exact stdin, including
  absence of a raw-transcript sentinel;
- console test proving audio/STT returns a spec preview first and cannot run
  Codex implicitly;
- separate run endpoint rejects transcript/audio/raw fields and revalidates
  the preview;
- one secret-free live invocation with a before/after workspace fingerprint
  proving read-only behavior and valid structured output;
- no persistent raw audio, transcript, complete prompt/output, or token/auth
  data in default logs.

## EliteBook-Audible Piper Delta

Refactor Piper generation from local playback:

1. add a render-to-WAV path that fails visibly and does not fall back to a
   different voice engine;
2. add a bounded loopback-only TTS endpoint that returns `audio/wav`, uses an
   unpredictable temporary file, sends `Cache-Control: no-store`, and unlinks
   the file in all cases;
3. make the browser play the returned blob, initially behind the manual
   `Speak` action because browser autoplay may be blocked;
4. test content type, text/body bounds, renderer failure, cleanup, and absence
   of server-side playback.

## Outside-Home Access Boundary

Do not create a public access point. Do not forward Livebox TCP `22`, `8770`,
VNC, or the current `8080` service, and do not publish the Voice Console.

The recommended V1 candidate is a private Tailscale tailnet used only as the
network transport between `BXEB` and the T480. Keep the already-proven
key-based OpenSSH service and run the same loopback SSH forward over the
private tailnet. Do not enable Tailscale SSH or Funnel in V1. Before adoption,
the operator must accept the hosted control-plane/identity-provider tradeoff.

Implementation gates:

- MFA-protected personal tailnet and device approval;
- replace the initial broad policy with a tested minimum grant from `BXEB` to
  T480 TCP `22`;
- keep key expiry initially; any headless T480 exception is a separate
  documented choice;
- verify router/firewall state, key-only non-root SSH, and no public forwards;
- test from a phone hotspot, then after reboot and sleep/resume.

Tailscale crosses NAT and can relay encrypted traffic when a direct path is
unavailable, but it cannot wake the T480. If the T480 is off, suspended,
hibernated, disconnected, or its SSH/Tailscale services are stopped, it is
unreachable. AC power, lid/sleep policy, boot services, and optionally later
wake-on-LAN through the always-on `ctos-core` are separate availability work.

Direct self-hosted WireGuard remains a later option when avoiding the hosted
control plane matters more than setup time. It adds public endpoint/DDNS or
CGNAT discovery, UDP forwarding, firewall and peer lifecycle work; the
best-case estimate is 2-4 hours and can extend beyond a half-day.

## Exact Next Order

1. Obtain informed approval for one synthetic read-only Codex smoke, then
   enable the runtime gate only for that acceptance window and verify the
   before/after file fingerprints.
2. On the EliteBook, press `Speak` once and confirm audible Piper output.
3. Run five short human French phrases in Codex mode, inspect/edit/revalidate
   each local spec, and record recognition/compiler failures. Do not run Codex
   for those samples unless each reviewed task is separately intended.
4. Keep workspace-write unavailable until open question 49 is resolved.
5. Implement outside-home private transport separately after open questions 50
   and 51; it does not block the LAN POC.

No VPN, router/firewall change, power-policy change, public listener, raw-audio
retention, transcript persistence, or workspace-write Codex path was added.
