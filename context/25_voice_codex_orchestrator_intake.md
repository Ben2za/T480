# Voice-to-Codex Orchestrator Intake

Date: 2026-07-18

Status: requirements and live-state audit complete; implementation not started

Operator clarification 2026-07-18: authenticated paid Codex access may be
used as the primary coding/reasoning executor. Do not infer unlimited quota or
a particular subscription entitlement from that authorization. Usage-limit,
authentication, and service errors must remain visible; there is no silent
fallback to a weaker local model.

## Scope

Compare the operator's proposed voice-to-Codex build sequence with the actual
T480, `ctos-core`, `BXEB`, and repository state. Identify the smallest useful
delta without installing packages, pulling models, starting persistent
services, or promoting `BXEB` to a CTOS runtime role.

The requirements were entered in an existing Zenity multiline dialog on the
active `BXEB` GNOME/Wayland session and returned over the already-authorized
key-only SSH connection. No payload file was created on `BXEB`. The raw entry
is not copied into the repository; only the normalized requirements and audit
result below are retained. The operator was warned not to include secrets.

## Normalized Requirements

1. Make a voice orchestrator whose priority target is Codex.
2. Audit OS, Python, CUDA/GPU, Ollama, microphone, FFmpeg, Git, and Node before
   changing a node.
3. Install only missing dependencies, with `uv`, FFmpeg, Cargo, tmux, and
   ripgrep named as candidates.
4. Evaluate Ollama with Qwen3, Gemma 3, and Llama 3.3 only where hardware fits.
5. Compare local faster-whisper and whisper.cpp on real audio.
6. Use Silero VAD to detect speech boundaries.
7. Compare local Kokoro and Piper TTS.
8. Integrate Codex through its supported CLI, not Selenium or pixel control.
9. Target a pipeline of microphone -> VAD -> STT -> local reasoning -> clean
   task specification -> Codex -> TTS.
10. Keep simple Markdown project memory; do not add a vector database yet.
11. Never send the raw STT transcript to Codex; send a validated task spec.
12. Integrate with VS Code and MCP without UI automation.
13. Keep configuration explicit and logs systematic.
14. Research every new component before adopting it.
15. Maintain an architecture plan, reproducible install scripts, a clear repo
   structure, and minimal operator documentation.

## Live Node Inventory

### T480 operator node

- EndeavourOS, Linux `6.18.38-4-lts`.
- Intel i7-8550U, 4 cores / 8 threads, 15 GiB RAM, Intel UHD 620; no CUDA
  device or toolkit.
- Python `3.14.6`, FFmpeg `8.1.2`, Git `2.55.0`, Node `26.4.0`, npm `12.0.1`,
  uv `0.11.28`, tmux `3.7b`, ripgrep `15.2.0`; Cargo is absent.
- Codex CLI `0.133.0` is installed and authenticated with ChatGPT.
- VS Code `1.121.0` and `openai.chatgpt` extension `26.715.31925` are present.
  `codex mcp list` reports no configured MCP servers.
- Vosk French push-to-talk and Piper `fr_FR-siwis-medium` are installed and
  ready. Live desktop audio was readable at output 115% and microphone 20%.
- Voice Console code is installed but the localhost service on `8770` is
  currently stopped.

### `ctos-core` service/model node

- EndeavourOS, Linux `7.0.12-arch1-1`.
- Ryzen 5 2400G, 4 cores / 8 threads, 5.7 GiB RAM plus 512 MiB swap.
- GTX 1650 4 GiB, NVIDIA driver `610.43.02`, compute capability 7.5. The live
  Ollama package has only CPU backends: no `ollama-cuda`, CUDA toolkit, or
  `libggml-cuda.so` is installed. The GPU must not be counted as model capacity
  until that separate package/runtime decision is made and verified.
- Python `3.14.5`, FFmpeg `8.1.1`, Git `2.54.0`, Node `26.2.0`, and ripgrep
  `15.1.0` are present. uv and tmux are absent; the Rustup Cargo shim exists but
  has no selected toolchain and is not usable.
- Ollama `0.30.8` is active on localhost. `qwen2.5-coder:0.5b` and `:1.5b` are
  cached. The Ollama/OpenJarvis tunnel works on demand.
- Home Assistant, Speech-to-Phrase, and Wyoming Whisper images/data paths are
  present, but their temporary containers are stopped. The Home Assistant
  token is absent.
- No reusable human French voice corpus exists yet.

### `BXEB` / `ctos-zlitebook` candidate

- Ubuntu `24.04.4`, Linux `6.17.0-40-generic`.
- Intel i5-8365U, 4 cores / 8 threads, 7.6 GiB RAM plus 7.5 GiB swap, Intel
  UHD 620; no CUDA.
- Python `3.12.3`, Git `2.43.0`, Node `18.19.1`, npm `9.2.0`, Cargo `1.94.0`,
  VS Code `1.128.1`. FFmpeg, uv, tmux, ripgrep, and Codex CLI are absent.
- Ollama `0.16.0` is active and enabled. It has `qwen3:8b` Q4_K_M (5.2 GB),
  `glm-4.7-flash` 29.9B Q4_K_M (19 GB), and two cloud tags cached.
- Root storage is already 89% used, with about 11 GiB free. The 19 GB GLM
  artifact is larger than RAM plus swap before runtime overhead and is not a
  realistic local runtime on this machine. It is a future explicit cleanup or
  move candidate, not something to delete silently.
- `BXEB` remains a status-only Ubuntu worker candidate. Cache presence is not
  proof that Qwen3 8B is responsive enough for interactive voice work.

## Requirement Gap Matrix

| # | Requirement | Actual state | Verdict / required delta |
| --- | --- | --- | --- |
| 1 | Voice orchestrator for Codex | CTOS has voice, planning, approval, OpenJarvis, and a text handoff, but no direct Codex runner. | Partial. Keep CTOS; add a bounded spec compiler and direct Codex adapter rather than another assistant platform. |
| 2 | Machine audit | Fleet, Jarvis, audio, backend, and Ollama probes already cover most facts, but no single command covers all requested tools and node roles. | Partial. Extend an existing doctor/status surface; do not add another unrelated bootstrap framework. |
| 3 | Install missing tools | Tools differ by node; several named tools are not required by the selected runtime. | Reject blanket installation. Cargo is not needed for the current Python/container path; tmux is not required for managed services; install only a dependency selected by a tested backend. |
| 4 | Qwen3, Gemma 3, Llama 3.3 | Ollama and small Qwen2.5 models already work. Core is CPU-only with 5.7 GiB RAM. | Benchmark exact `qwen3:1.7b-q4_K_M`, then `gemma3:1b-it-qat`, only after the adapter is model-aware. Defer 4B. Reject Llama 3.3 because the official family is 70B only. Do not use bare model aliases. |
| 5 | faster-whisper vs whisper.cpp | Wyoming/faster-whisper image/path exists and has passed transport smoke; it is stopped. whisper.cpp is not installed. | Keep faster-whisper as integration baseline, add a reproducible whisper.cpp challenger, and select on French WER/intent success, latency, memory, and failure rate—not speed alone. Blocked on the missing human corpus. |
| 6 | Silero VAD | CTOS already applies an energy/activity gate, trim/normalization, and a hallucination guard. It does not have streaming Silero endpointing. | Partial. Test native Silero VAD in faster-whisper and whisper.cpp; do not add a separate VAD daemon. Keep the CTOS guards until measurements justify removal. |
| 7 | Kokoro vs Piper | Piper `1.4.2` and French `siwis-medium` are ready. Kokoro is absent. | Piper remains the working default. Benchmark Kokoro only as a quality challenger on `ctos-core`; it is heavier and its official French coverage is thin. Review Piper `1.5.0`, licensing, and attribution before any upgrade. |
| 8 | Direct Codex CLI | Codex CLI and auth are ready. Current `codex-brief` only prints a handoff and never invokes Codex. | Missing adapter. Use stable `codex exec`, initially `--ephemeral` and `--sandbox read-only`; reject Selenium, pixel control, and the experimental app-server as the V1 bridge. |
| 9 | Minimal end-to-end pipeline | Capture, STT, local model, CTOS planner, and TTS pieces exist independently. | Partial. Missing pieces are native endpointing, a strict spec compiler/validator, operator preview, and the Codex runner. |
| 10 | Markdown memory, no vector DB | Repo context is already Markdown and no vector DB is part of the selected V1. Runtime transcript/memory retention remains unresolved. | Keep Markdown for durable sanitized decisions/spec summaries. Do not persist raw audio/transcripts or add vector storage. |
| 11 | No raw transcript to Codex | `scripts/ctos-openjarvis:codex_handoff()` currently repeats the supplied text under both `User said` and `Compact request`. | Non-compliant with the new requirement. Direct Codex execution must remain blocked until the raw handoff is replaced by a validated spec-only boundary. |
| 12 | VS Code and MCP, no pixels | VS Code and the Codex extension exist; no MCP server is configured. No current CTOS voice path uses pixel automation. | Partial. The CLI and IDE already share Codex configuration. Add MCP only for a concrete tool/context need; it is not required for the first voice-to-Codex path. |
| 13 | Explicit config and systematic logs | CTOS uses JSON registries, Codex TOML, component environment variables, `/tmp`, and local state. Logging is fragmented. | Do not impose YAML or `.env` globally. Keep versioned non-secret JSON/TOML, runtime env only where needed, and add bounded structured stage events with no raw transcript/audio/token content. |
| 14 | Research before adoption | Repo policy already requires current targeted research and primary sources. | Keep it. GitHub issue data, Reddit, and blogs are secondary evidence, not mandatory decision authorities when official docs/releases exist. |
| 15 | Architecture/scripts/repo/docs | The repo already contains all four categories. | Mostly ready. Missing deliverables are the spec schema/compiler, direct Codex adapter, benchmark manifest/results, and a short operator runbook. |

## Selected Architecture Delta

The smallest reliable next path uses Codex as the primary work engine and
keeps the local model in the narrower, untrusted spec-compilation role:

```text
explicit capture window
  -> native backend VAD plus existing CTOS audio guard
  -> local STT
  -> local spec compiler
  -> deterministic schema validation and redaction
  -> operator preview
  -> codex exec --ephemeral --sandbox read-only
  -> reviewed result
  -> local Piper summary
```

The Codex input schema should contain only normalized task fields such as:

- goal;
- repository/workspace target;
- allowed scope;
- constraints;
- requested deliverable;
- acceptance checks;
- risk/approval class;
- clarification state.

It must not contain a `transcript`, `audio`, credential, arbitrary shell, or
unbounded context field. A local model may propose the spec, but deterministic
code must validate field types, sizes, allowed workspace, approval class, and
redaction before Codex sees it. The operator must be able to inspect the exact
canonical spec. Mutable Codex work remains behind an explicit later transition
from read-only to workspace-write.

## Model And Speech Benchmark Gate

Do not pull every named model or install every backend. First capture a small
reusable French corpus outside Git with clean speech, actual short commands,
natural task requests, room noise, silence, quiet/clipped input, and relevant
names/accents.

Use identical 16 kHz mono samples and record:

- normalized WER/CER and CTOS intent/spec success;
- silence/noise hallucination and empty-result rate;
- cold and warm p50/p95 latency plus real-time factor;
- peak RAM/VRAM, CPU load, thermals, and swap;
- Ollama/STT/TTS contention;
- startup/update complexity and reproducible failure behavior;
- blinded French intelligibility/pronunciation for TTS.

STT baseline/challenger:

- current Wyoming/faster-whisper multilingual `base-int8`;
- whisper.cpp current multilingual base quantized;
- native Silero VAD on/off while retaining the CTOS pre/post guards.

TTS baseline/challenger:

- current Piper `fr_FR-siwis-medium` on CPU;
- only licence-acceptable Piper alternatives if pronunciation is weak;
- Kokoro `ff_siwis` as an optional `ctos-core` quality comparison, not a
  presumed replacement.

Local spec-compilation candidates, not Codex replacements:

- current `qwen2.5-coder:1.5b` baseline;
- exact `qwen3:1.7b-q4_K_M` with explicit non-thinking/short-context settings;
- exact `gemma3:1b-it-qat` challenger;
- later, conditional `qwen3:4b-instruct-2507-q4_K_M` only after RAM/CUDA work.

Qwen3 is not a tag-only swap. Its thinking and sampling behavior differs from
the current adapter. The adapter must explicitly control thinking, sampling,
context, timeouts, and output schema before a voice-path benchmark.

## Rejected Shortcuts

- Rebuilding the existing voice stack from zero.
- Pulling Qwen3, Gemma 3, and Llama 3.3 indiscriminately.
- Treating a cached model as proof of usable latency.
- Installing full CUDA, Cargo, tmux, uv, or FFmpeg on every node without a
  selected consumer and reproducible package plan.
- Promoting `BXEB` while its role, 89%-full root, old Ollama deployment, and
  data-retention boundary remain unresolved.
- Forwarding the current raw `codex-brief` text into `codex exec`.
- Logging every transcript, prompt, audio file, command output, or secret.
- Adding a vector database, wake word, always-on microphone, Selenium, or
  pixel-level desktop control to the first path.

## Next Implementation Slice

1. Correct live-state drift in the voice registries and task board.
2. Capture the five-sample core human corpus already requested by
   `ctos-jarvis collect-next --run`.
3. Add a versioned voice task-spec schema and deterministic validator with
   synthetic tests; keep it inert and local first.
4. Replace raw `codex-brief` output with spec-only preview generation.
5. Add a plan-only `codex exec` command renderer; then test one synthetic,
   secret-free, read-only, ephemeral run after explicit implementation scope.
6. Add the STT/VAD benchmark challenger and select a backend from measured
   results.
7. Add bounded redacted stage telemetry before any daily/persistent service.

No package, model, service, Codex execution, or raw-transcript persistence was
authorized or performed during this intake.
