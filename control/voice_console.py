#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unicodedata
import uuid
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "control" / "static"
TMP_DIR = Path(os.environ.get("CTOS_VOICE_CONSOLE_TMP", "/tmp/ctos-voice-console"))
KEEP_AUDIO = os.environ.get("CTOS_VOICE_CONSOLE_KEEP_AUDIO", "0") == "1"
MAX_AUDIO_BYTES = int(os.environ.get("CTOS_VOICE_CONSOLE_MAX_AUDIO_BYTES", str(20 * 1024 * 1024)))
MAX_JSON_BYTES = 64 * 1024
MAX_CODEX_CANONICAL_BYTES = 32 * 1024
MAX_CODEX_RESULT_BYTES = 64 * 1024
MAX_BROWSER_TTS_CHARS = 1200
MAX_BROWSER_TTS_WAV_BYTES = 8 * 1024 * 1024
CODEX_PREVIEW_TTL_SECONDS = 10 * 60
CODEX_PREVIEW_MAX_ENTRIES = 32
CODEX_RUN_ENABLED = os.environ.get("CTOS_VOICE_CODEX_RUN_ENABLED", "0") == "1"
VOICE_CONSOLE_BUILD = "2026-07-19.3"
CODEX_PREVIEWS: dict[str, tuple[str, float, str]] = {}
CODEX_PREVIEW_LOCK = threading.Lock()
CODEX_RUN_LOCK = threading.Lock()

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai.voice_task_compiler import VoiceTaskCompilerError, compile_transcript  # noqa: E402
from ai.voice_task_spec import (  # noqa: E402
    VoiceTaskSpecError,
    canonical_json,
    spec_digest,
    validate_spec,
)
KALI_ALIASES = {
    "cali",
    "callie",
    "cally",
    "carly",
    "kali",
    "kalie",
    "kalli",
    "kaly",
    "kelly",
    "khali",
    "qali",
    "quali",
}
KALI_PHRASE_ALIASES = (
    "c a li",
    "ca lit",
    "ka li",
    "k a li",
    "k a l i",
    "qua lit",
    "qu a lit",
)


def repo_command(name: str) -> str:
    path = ROOT / "scripts" / name
    if path.exists():
        return str(path)
    return shutil.which(name) or name


def command_available(command: str) -> bool:
    return Path(command).exists() or shutil.which(command) is not None


def now_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{uuid.uuid4().hex[:8]}"


def run_capture(
    cmd: list[str],
    *,
    timeout: float = 90.0,
    input_text: str | None = None,
) -> dict[str, object]:
    try:
        proc = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            input=input_text,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "ok": False,
            "rc": 124,
            "stdout": exc.stdout or "",
            "stderr": f"timeout after {timeout:.0f}s",
            "cmd": cmd[:2],
        }
    except OSError as exc:
        return {
            "ok": False,
            "rc": 127,
            "stdout": "",
            "stderr": str(exc),
            "cmd": cmd[:2],
        }
    return {
        "ok": proc.returncode == 0,
        "rc": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "cmd": cmd[:2],
    }


class BrowserTtsError(RuntimeError):
    pass


def synthesize_browser_wav(text: str) -> bytes:
    cleaned = " ".join(text.split())
    if not cleaned:
        raise BrowserTtsError("speech text is empty")
    if len(cleaned) > MAX_BROWSER_TTS_CHARS:
        raise BrowserTtsError("speech text exceeds the browser TTS limit")

    handle = tempfile.NamedTemporaryFile(
        prefix="ctos-browser-tts-",
        suffix=".wav",
        delete=False,
        dir="/tmp",
    )
    handle.close()
    wav_path = Path(handle.name)
    try:
        rendered = run_capture(
            [
                repo_command("ctos-voice"),
                "render-wav",
                "--engine",
                "piper",
                "--output",
                str(wav_path),
                "--stdin",
            ],
            input_text=f"{cleaned}\n",
            timeout=130.0,
        )
        if not rendered.get("ok"):
            rc = int(rendered.get("rc") or 1)
            detail = " ".join(str(rendered.get("stderr") or "Piper render failed").split())[:800]
            raise BrowserTtsError(f"Piper render failed with status {rc}: {detail}")
        if wav_path.is_symlink() or not wav_path.is_file():
            raise BrowserTtsError("Piper output is not a regular WAV file")
        with wav_path.open("rb") as stream:
            audio = stream.read(MAX_BROWSER_TTS_WAV_BYTES + 1)
        if len(audio) > MAX_BROWSER_TTS_WAV_BYTES:
            raise BrowserTtsError("Piper WAV exceeds the browser response limit")
        if len(audio) < 44 or audio[:4] != b"RIFF" or audio[8:12] != b"WAVE":
            raise BrowserTtsError("Piper output has an invalid WAV header")
        return audio
    finally:
        wav_path.unlink(missing_ok=True)


class CodexPreviewError(RuntimeError):
    pass


def _purge_codex_previews(now: float) -> None:
    expired = [preview_id for preview_id, (_, deadline, _) in CODEX_PREVIEWS.items() if deadline <= now]
    for preview_id in expired:
        CODEX_PREVIEWS.pop(preview_id, None)


def _reject_duplicate_json_fields(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise CodexPreviewError("duplicate JSON field name rejected")
        result[key] = value
    return result


def register_codex_preview(
    spec: dict[str, object],
    canonical: str,
    digest: str,
    *,
    compiler_metadata: dict[str, object] | None = None,
) -> dict[str, object]:
    if len(canonical.encode("utf-8")) > MAX_CODEX_CANONICAL_BYTES:
        raise CodexPreviewError("validated preview exceeds the bounded console limit")

    preview_id = secrets.token_urlsafe(24)
    now = time.monotonic()
    deadline = now + CODEX_PREVIEW_TTL_SECONDS
    expires_at = (datetime.now(timezone.utc) + timedelta(seconds=CODEX_PREVIEW_TTL_SECONDS)).isoformat()
    with CODEX_PREVIEW_LOCK:
        _purge_codex_previews(now)
        while len(CODEX_PREVIEWS) >= CODEX_PREVIEW_MAX_ENTRIES:
            oldest = min(CODEX_PREVIEWS, key=lambda item: CODEX_PREVIEWS[item][1])
            CODEX_PREVIEWS.pop(oldest, None)
        # Store authorization metadata only. The transcript and spec stay out
        # of the preview registry.
        CODEX_PREVIEWS[preview_id] = (digest, deadline, expires_at)

    preview: dict[str, object] = {
        "ok": True,
        "mode": "codex",
        "runnable": CODEX_RUN_ENABLED,
        "preview_id": preview_id,
        "expires_at": expires_at,
        "spec_sha256": digest,
        "canonical_spec": canonical,
        "workspace": str(spec["workspace"]),
        "approval_class": str(spec["approval_class"]),
    }
    if compiler_metadata is not None:
        preview["compiler"] = compiler_metadata
    return preview


def create_codex_preview(text: str) -> dict[str, object]:
    try:
        compiled = compile_transcript(text)
    except VoiceTaskCompilerError as exc:
        raise CodexPreviewError(str(exc)) from exc

    spec = compiled.get("spec")
    canonical = compiled.get("canonical")
    digest = compiled.get("digest")
    if not isinstance(spec, dict) or not isinstance(canonical, str) or not isinstance(digest, str):
        raise CodexPreviewError("local compiler returned an incomplete validated preview")
    return register_codex_preview(
        spec,
        canonical,
        digest,
        compiler_metadata={
            "model": str(compiled.get("model") or "unknown"),
            "elapsed_ms": int(compiled.get("elapsed_ms") or 0),
            "scope_restricted_to_explicit_paths": bool(
                compiled.get("scope_restricted_to_explicit_paths")
            ),
        },
    )


def revalidate_canonical_spec(
    canonical: str,
    *,
    require_exact_canonical: bool = True,
) -> tuple[dict[str, object], str, str]:
    if not canonical or len(canonical.encode("utf-8")) > MAX_CODEX_CANONICAL_BYTES:
        raise CodexPreviewError("canonical spec is missing or exceeds the bounded limit")
    try:
        parsed = json.loads(canonical, object_pairs_hook=_reject_duplicate_json_fields)
    except (json.JSONDecodeError, CodexPreviewError) as exc:
        raise CodexPreviewError("canonical spec is not valid JSON") from exc
    try:
        spec = validate_spec(parsed)
    except VoiceTaskSpecError as exc:
        raise CodexPreviewError(f"canonical spec was rejected: {exc}") from exc
    rebuilt = canonical_json(spec)
    if require_exact_canonical and canonical != rebuilt:
        raise CodexPreviewError("canonical spec does not match the deterministic rendering")
    return spec, rebuilt, spec_digest(spec)


def review_edited_codex_spec(value: str) -> dict[str, object]:
    spec, canonical, digest = revalidate_canonical_spec(
        value,
        require_exact_canonical=False,
    )
    return register_codex_preview(spec, canonical, digest)


def run_codex_preview(
    *,
    preview_id: str,
    supplied_digest: str,
    canonical: str,
    confirmed: bool,
) -> dict[str, object]:
    if not confirmed:
        raise CodexPreviewError("explicit review confirmation is required")
    if not CODEX_RUN_ENABLED:
        raise CodexPreviewError(
            "live Codex run is disabled pending informed external-disclosure approval"
        )
    if not re.fullmatch(r"[A-Za-z0-9_-]{24,64}", preview_id):
        raise CodexPreviewError("preview id is invalid")
    if not re.fullmatch(r"[0-9a-f]{64}", supplied_digest):
        raise CodexPreviewError("spec digest is invalid")

    spec, rebuilt, calculated_digest = revalidate_canonical_spec(canonical)
    if supplied_digest != calculated_digest:
        raise CodexPreviewError("spec digest does not match the reviewed canonical spec")
    if spec.get("approval_class") != "read_only":
        raise CodexPreviewError("only read-only Codex previews may run")

    if not CODEX_RUN_LOCK.acquire(blocking=False):
        raise CodexPreviewError("another read-only Codex task is already running")
    try:
        now = time.monotonic()
        with CODEX_PREVIEW_LOCK:
            _purge_codex_previews(now)
            stored = CODEX_PREVIEWS.get(preview_id)
            if stored is None:
                raise CodexPreviewError("preview is unknown, expired, or already consumed")
            stored_digest, deadline, _ = stored
            if deadline <= now:
                CODEX_PREVIEWS.pop(preview_id, None)
                raise CodexPreviewError("preview has expired")
            if stored_digest != calculated_digest:
                raise CodexPreviewError("preview token does not authorize this spec")
            CODEX_PREVIEWS.pop(preview_id, None)

        result = run_capture(
            [repo_command("ctos-codex-voice"), "run", "-", "--yes"],
            input_text=f"{rebuilt}\n",
            timeout=620.0,
        )
        if not result.get("ok"):
            rc = int(result.get("rc") or 1)
            detail = " ".join(str(result.get("stderr") or "Codex runner failed").split())[:2000]
            raise CodexPreviewError(f"Codex runner failed with status {rc}: {detail}")
        stdout = str(result.get("stdout") or "")
        if not stdout.strip() or len(stdout.encode("utf-8")) > MAX_CODEX_RESULT_BYTES:
            raise CodexPreviewError("Codex result is empty or exceeds the bounded console limit")
        try:
            parsed_result = json.loads(stdout)
        except json.JSONDecodeError as exc:
            raise CodexPreviewError("Codex runner returned invalid structured JSON") from exc
        if not isinstance(parsed_result, dict):
            raise CodexPreviewError("Codex runner returned a non-object result")
        return {
            "ok": True,
            "mode": "codex",
            "spec_sha256": calculated_digest,
            "result": parsed_result,
            "answer": json.dumps(parsed_result, ensure_ascii=False, indent=2, sort_keys=True),
        }
    finally:
        CODEX_RUN_LOCK.release()


def clamp_tokens(value: str | int | None) -> int:
    try:
        tokens = int(value or 180)
    except (TypeError, ValueError):
        tokens = 180
    return max(32, min(tokens, 512))


def clean_mode(value: str | None) -> str:
    if value in {"brief", "codex", "action"}:
        return value
    return "chat"


def normalize_action_text(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.casefold())
    stripped = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    cleaned = re.sub(r"[^a-z0-9]+", " ", stripped)
    return " ".join(cleaned.split())


def canonical_action_text(text: str) -> tuple[str, list[dict[str, str]]]:
    normalized = normalize_action_text(text)
    replacements: list[dict[str, str]] = []
    for phrase in KALI_PHRASE_ALIASES:
        if phrase in normalized:
            normalized = re.sub(rf"\b{re.escape(phrase)}\b", "kali", normalized)
            replacements.append({"from": phrase, "to": "kali"})

    tokens: list[str] = []
    for token in normalized.split():
        if token in KALI_ALIASES and token != "kali":
            tokens.append("kali")
            replacements.append({"from": token, "to": "kali"})
        else:
            tokens.append(token)
    return " ".join(tokens), replacements


def action_words(text: str) -> set[str]:
    canonical, _ = canonical_action_text(text)
    return set(canonical.split())


def looks_like_agenda_request(text: str) -> bool:
    normalized = normalize_action_text(text)
    words = set(normalized.split())
    agenda_terms = {"agenda", "tache", "task", "rdv", "rendez", "calendrier"}
    agenda_verbs = {"ajoute", "ajouter", "cree", "creer", "note", "noter", "mets", "mettre"}
    date_terms = {"demain", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"}
    timed = bool(re.search(r"\b[0-9]+\s*(h|min|minute|minutes)\b", normalized))
    return bool((agenda_terms & words) or ((agenda_verbs & words) and ((date_terms & words) or timed)))


def detect_approval_action(text: str) -> dict[str, str] | None:
    words = action_words(text)
    normalized, _ = canonical_action_text(text)
    kali = "kali" in words or ("vm" in words and "ctos" in words)
    core = bool({"core", "tour", "server", "serveur", "desktop"} & words)

    if kali and {"snapshot", "checkpoint", "sauvegarde", "save", "baseline"} & words:
        return {"action": "kali-checkpoint", "label": "Kali checkpoint"}
    if kali and {"eteins", "eteindre", "arrete", "arreter", "stop", "shutdown", "coupe"} & words:
        return {"action": "kali-shutdown", "label": "Shutdown Kali"}
    if kali and {"demarre", "demarrer", "lance", "lancer", "start", "allume"} & words:
        return {"action": "kali-start", "label": "Start Kali"}
    if kali and ({"console", "affiche", "ouvre", "ouvrir"} & words or "kali" in normalized):
        return {"action": "kali-console", "label": "Open Kali console"}
    if core and {"sync", "synchronise", "synchroniser", "copie", "update", "maj"} & words:
        return {"action": "core-sync-repo", "label": "Sync core repo"}
    if core and {"layout", "structure", "srv", "dossier", "dossiers", "apply", "applique"} & words:
        return {"action": "core-apply-layout", "label": "Apply core layout"}
    return None


def wants_ctos_brief(text: str) -> bool:
    normalized = text.lower()
    tokens = (
        "etat",
        "état",
        "status",
        "statut",
        "config",
        "configuration",
        "lieux",
        "capacite",
        "capacité",
        "connecte",
        "connecté",
        "connexion",
        "reseau",
        "réseau",
        "machine",
        "machines",
    )
    return any(token in normalized for token in tokens)


def first_value(lines: list[str], prefix: str) -> str:
    for line in lines:
        if line.startswith(prefix):
            return " ".join(line.split()[1:])
    return "unknown"


def brief_network_lines(text: str) -> list[str]:
    interesting = []
    for raw in text.splitlines():
        line = " ".join(raw.split())
        if line.startswith(("enp", "wlan", "virbr")):
            interesting.append(line)
    return interesting[:8]


def build_ctos_brief(user_text: str) -> dict[str, object]:
    ai = run_capture([repo_command("ctos-ai"), "brief"], timeout=45.0)
    net = run_capture([repo_command("ctos-netwatch"), "status"], timeout=12.0)
    oj = run_capture([repo_command("ctos-openjarvis"), "status", "--json"], timeout=20.0)

    ai_lines = str(ai.get("stdout") or "").splitlines()
    net_lines = brief_network_lines(str(net.get("stdout") or ""))
    oj_payload: dict[str, object] = {}
    if oj.get("ok") and oj.get("stdout"):
        try:
            parsed = json.loads(str(oj["stdout"]))
            if isinstance(parsed, dict):
                oj_payload = parsed
        except json.JSONDecodeError:
            oj_payload = {}

    host = first_value(ai_lines, "host")
    load = first_value(ai_lines, "load")
    ram = first_value(ai_lines, "ram")
    battery = first_value(ai_lines, "battery")
    core = first_value(ai_lines, "core")
    kali = first_value(ai_lines, "kali")
    agenda = first_value(ai_lines, "agenda")
    runtime = first_value(ai_lines, "runtime")
    next_step = first_value(ai_lines, "next")
    ollama_version = str(oj_payload.get("ollama_version") or "unknown")
    model = str(oj_payload.get("model") or "unknown")
    model_ok = str(oj_payload.get("model_available") or "unknown")
    tunnel_ok = str(oj_payload.get("tunnel_ok") or "unknown")

    answer_lines = [
        "Etat CTOS reel:",
        f"- Host: {host}",
        f"- Charge: {load}",
        f"- RAM: {ram}",
        f"- Batterie: {battery}",
        f"- Tour/core: {core}",
        f"- Kali: {kali}",
        f"- Agenda: {agenda}",
        f"- Runtime IA: {runtime}",
        f"- OpenJarvis/Ollama: tunnel={tunnel_ok} ollama={ollama_version} model={model} available={model_ok}",
    ]
    if net_lines:
        answer_lines.append("- Reseau visible:")
        answer_lines.extend(f"  {line}" for line in net_lines)
    answer_lines.extend(
        [
            f"- Prochaine action: {next_step}",
            "",
            "Ce que je peux voir maintenant: repo CTOS, etat host, services locaux, ports, interfaces, tunnels, agenda, Kali via scripts si disponible, tour si SSH joignable.",
            "Ce que je ne vois pas tout seul: secrets, mots de passe, contenu ecran sans screenshot/browser, paquets reseau profonds sans capture explicite.",
        ]
    )
    if user_text:
        answer_lines.append(f"Demande traitee: {user_text}")
    return {
        "ok": bool(ai.get("ok")),
        "rc": ai.get("rc", 0),
        "stdout": "\n".join(answer_lines),
        "stderr": "\n".join(
            part
            for part in [
                str(ai.get("stderr") or "").strip(),
                str(net.get("stderr") or "").strip(),
                str(oj.get("stderr") or "").strip(),
            ]
            if part
        ),
        "answer": "\n".join(answer_lines),
    }


def run_json(cmd: list[str], *, timeout: float = 30.0) -> tuple[dict[str, object], object | None]:
    result = run_capture(cmd, timeout=timeout)
    payload: object | None = None
    if result.get("stdout"):
        try:
            payload = json.loads(str(result["stdout"]))
        except json.JSONDecodeError as error:
            result["ok"] = False
            result["stderr"] = f"json decode error: {error}"
            result["rc"] = result.get("rc") or 1
    return result, payload


def route_action_text(text: str) -> dict[str, object]:
    canonical_text, replacements = canonical_action_text(text)
    routed_text = canonical_text if replacements else text
    route, route_payload = run_json(
        [repo_command("ctos-ai"), "route-text", routed_text, "--source", "voice", "--json"],
        timeout=15.0,
    )
    plan = route_payload if isinstance(route_payload, dict) else {}
    detected = detect_approval_action(routed_text)
    agenda_probe: dict[str, object] = {}
    if looks_like_agenda_request(routed_text):
        agenda, agenda_payload = run_json(
            [repo_command("ctos-ai"), "agenda-propose", routed_text, "--source", "voice", "--json"],
            timeout=15.0,
        )
        if isinstance(agenda_payload, dict):
            agenda_probe = agenda_payload
            agenda_probe["probe_ok"] = bool(agenda.get("ok"))

    lines = ["CTOS action preview", "==================="]
    lines.append(f"input     {text}")
    if replacements and routed_text != text:
        lines.append(f"canonical {routed_text}")
    if detected:
        lines.append(f"queue     approval:{detected['action']}")
    elif agenda_probe.get("recognized"):
        lines.append("queue     agenda-proposal")
        lines.append(f"title     {agenda_probe.get('title') or '-'}")
        lines.append(f"due       {agenda_probe.get('due_date') or '-'}")
        lines.append(f"estimate  {agenda_probe.get('estimate_minutes')} min")
    elif plan.get("safe_to_execute"):
        command = plan.get("command") if isinstance(plan.get("command"), list) else []
        lines.append(f"safe      {' '.join(str(item) for item in command)}")
        lines.append("queue     not needed; direct safe command, use normal mode for now")
    else:
        lines.append("queue     no deterministic action")
    if plan:
        lines.append(f"matched   {plan.get('matched')} {plan.get('intent_id') or plan.get('category') or ''}".rstrip())
        lines.append(f"reason    {plan.get('reason') or '-'}")
    lines.append("next      click Queue last only if this matches your intent")

    ok = bool(route.get("ok")) or bool(detected) or bool(agenda_probe.get("recognized"))
    return {
        "ok": ok,
        "rc": 0 if ok else route.get("rc", 1),
        "answer": "\n".join(lines),
        "plan": plan,
        "detected": detected or {},
        "agenda_probe": agenda_probe,
        "canonical_text": routed_text,
        "replacements": replacements,
        "stderr": str(route.get("stderr") or "").strip(),
    }


def action_queue_payload() -> dict[str, object]:
    approvals_result, approvals_payload = run_json(
        [repo_command("ctos-ai"), "approvals", "--status", "pending", "--limit", "20", "--json"],
        timeout=15.0,
    )
    agenda_result, agenda_payload = run_json(
        [repo_command("ctos-ai"), "agenda-proposals", "--status", "pending", "--limit", "20", "--json"],
        timeout=15.0,
    )
    approvals = approvals_payload if isinstance(approvals_payload, list) else []
    agenda = agenda_payload if isinstance(agenda_payload, list) else []
    return {
        "ok": bool(approvals_result.get("ok")) and bool(agenda_result.get("ok")),
        "approvals": approvals,
        "agenda": agenda,
        "errors": {
            "approvals": str(approvals_result.get("stderr") or "").strip(),
            "agenda": str(agenda_result.get("stderr") or "").strip(),
        },
        "total": len(approvals) + len(agenda),
    }


def queue_action_text(text: str) -> dict[str, object]:
    route = route_action_text(text)
    routed_text = str(route.get("canonical_text") or text)
    detected = route.get("detected") if isinstance(route.get("detected"), dict) else {}
    agenda_probe = route.get("agenda_probe") if isinstance(route.get("agenda_probe"), dict) else {}

    if agenda_probe.get("recognized"):
        queued, payload = run_json(
            [repo_command("ctos-ai"), "agenda-propose", routed_text, "--save", "--source", "voice", "--json"],
            timeout=20.0,
        )
        pending = payload.get("pending") if isinstance(payload, dict) else None
        return {
            "ok": bool(queued.get("ok")),
            "queued": bool(queued.get("ok")),
            "kind": "agenda",
            "item": pending if isinstance(pending, dict) else payload,
            "route": route,
            "answer": "Agenda proposal queued. Review, then approve or reject.",
            "stderr": str(queued.get("stderr") or "").strip(),
            "rc": queued.get("rc", 0),
        }

    action = str(detected.get("action") or "")
    if action:
        note = f"voice: {text}"
        if routed_text != text:
            note = f"{note} -> {routed_text}"
        note = note[:240]
        queued, payload = run_json(
            [repo_command("ctos-ai"), "propose", action, "--note", note, "--json"],
            timeout=20.0,
        )
        return {
            "ok": bool(queued.get("ok")),
            "queued": bool(queued.get("ok")),
            "kind": "approval",
            "item": payload if isinstance(payload, dict) else {},
            "route": route,
            "answer": f"Approval queued for {action}. Review, then approve or reject.",
            "stderr": str(queued.get("stderr") or "").strip(),
            "rc": queued.get("rc", 0),
        }

    return {
        "ok": True,
        "queued": False,
        "kind": "none",
        "route": route,
        "answer": "No queueable action detected. Rephrase or keep it as chat.",
        "stderr": str(route.get("stderr") or "").strip(),
        "rc": 0,
    }


def audio_suffix(content_type: str) -> str:
    ctype = content_type.split(";", 1)[0].strip().lower()
    return {
        "audio/webm": ".webm",
        "audio/ogg": ".ogg",
        "audio/wav": ".wav",
        "audio/x-wav": ".wav",
        "audio/mpeg": ".mp3",
        "audio/mp4": ".m4a",
    }.get(ctype, ".audio")


def convert_to_wav(raw_path: Path, wav_path: Path) -> dict[str, object]:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return {"ok": False, "rc": 127, "stderr": "ffmpeg is required for browser audio conversion"}
    return run_capture(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(raw_path),
            "-ac",
            "1",
            "-ar",
            "16000",
            "-sample_fmt",
            "s16",
            str(wav_path),
        ],
        timeout=45.0,
    )


def transcribe_wav(wav_path: Path) -> dict[str, object]:
    result = run_capture([repo_command("ctos-voice"), "transcribe-file", str(wav_path), "--json"], timeout=90.0)
    text = ""
    payload: dict[str, object] = {}
    if result["stdout"]:
        try:
            parsed = json.loads(str(result["stdout"]))
            if isinstance(parsed, dict):
                payload = parsed
                text = str(parsed.get("text") or "").strip()
        except json.JSONDecodeError:
            text = str(result["stdout"]).strip()
    result["payload"] = payload
    result["text"] = text
    return result


def ask_brain(text: str, *, mode: str, max_tokens: int) -> dict[str, object]:
    command = repo_command("ctos-openjarvis")
    if mode == "action":
        return route_action_text(text)
    if mode == "codex":
        return {
            "ok": False,
            "rc": 2,
            "answer": "",
            "stderr": "Codex mode requires a validated preview; the legacy raw handoff is disabled.",
        }
    if mode == "brief" or (mode == "chat" and wants_ctos_brief(text)):
        return build_ctos_brief(text)
    result = run_capture([command, "ask", text, "--max-tokens", str(max_tokens)], timeout=180.0)
    result["answer"] = str(result.get("stdout") or "").strip()
    if result.get("ok") and not result["answer"]:
        result["ok"] = False
        result["rc"] = 1
        result["stderr"] = "local Chat returned an empty response"
    return result


class VoiceConsoleHandler(SimpleHTTPRequestHandler):
    server_version = "CTOSVoiceConsole/0.1"

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def log_message(self, format: str, *args: object) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), format % args))

    def end_headers(self) -> None:
        # The console is served only through loopback and changes frequently.
        # Never let the remote browser silently keep an obsolete control UI.
        self.send_header("Cache-Control", "no-store")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/voice/status":
            self.send_json(self.status_payload())
            return
        if parsed.path == "/api/voice/action/queue":
            self.send_json(action_queue_payload())
            return
        if parsed.path in ("", "/"):
            self.path = "/voice.html"
        return super().do_GET()

    def do_POST(self) -> None:
        if not self.client_address[0].startswith("127."):
            self.send_json({"ok": False, "error": "loopback clients only"}, status=HTTPStatus.FORBIDDEN)
            return
        parsed = urlparse(self.path)
        if parsed.path == "/api/voice/codex/preview":
            self.handle_codex_preview()
            return
        if parsed.path == "/api/voice/codex/review":
            self.handle_codex_review()
            return
        if parsed.path == "/api/voice/codex/run":
            self.handle_codex_run()
            return
        if parsed.path == "/api/voice/ask-text":
            self.handle_ask_text()
            return
        if parsed.path == "/api/voice/audio":
            self.handle_audio(parsed.query)
            return
        if parsed.path == "/api/voice/synthesize":
            self.handle_synthesize()
            return
        if parsed.path == "/api/voice/say":
            self.handle_say()
            return
        if parsed.path == "/api/voice/action/route":
            self.handle_action_route()
            return
        if parsed.path == "/api/voice/action/queue":
            self.handle_action_queue()
            return
        if parsed.path == "/api/voice/action/approve":
            self.handle_action_approve()
            return
        if parsed.path == "/api/voice/action/reject":
            self.handle_action_reject()
            return
        self.send_json({"ok": False, "error": "not found"}, status=HTTPStatus.NOT_FOUND)

    def status_payload(self) -> dict[str, object]:
        openjarvis = repo_command("ctos-openjarvis")
        voice = repo_command("ctos-voice")
        codex_voice = repo_command("ctos-codex-voice")
        status: dict[str, object] = {
            "ok": True,
            "build": VOICE_CONSOLE_BUILD,
            "bind": f"{self.server.server_address[0]}:{self.server.server_address[1]}",
            "audio_tmp": str(TMP_DIR),
            "keep_audio": KEEP_AUDIO,
            "commands": {
                "ctos-openjarvis": command_available(openjarvis),
                "ctos-voice": command_available(voice),
                "ctos-codex-voice": command_available(codex_voice),
                "ffmpeg": shutil.which("ffmpeg") is not None,
            },
            "codex": {
                "legacy_raw_handoff_enabled": False,
                "run_enabled": CODEX_RUN_ENABLED,
                "preview_ttl_seconds": CODEX_PREVIEW_TTL_SECONDS,
                "task_schema_ready": (ROOT / "ai" / "voice_task_spec.schema.json").is_file(),
                "result_schema_ready": (ROOT / "ai" / "codex_readonly_result.schema.json").is_file(),
            },
            "browser_tts": {
                "endpoint": "/api/voice/synthesize",
                "engine": "piper",
                "max_text_chars": MAX_BROWSER_TTS_CHARS,
                "server_side_playback": False,
                "legacy_say_endpoint_enabled": False,
            },
        }
        probe = run_capture([openjarvis, "status", "--json"], timeout=20.0)
        if probe["ok"] and probe["stdout"]:
            try:
                status["openjarvis"] = json.loads(str(probe["stdout"]))
            except json.JSONDecodeError:
                status["openjarvis"] = {"raw": str(probe["stdout"]).strip()}
        else:
            status["openjarvis"] = {
                "ok": False,
                "rc": probe["rc"],
                "stderr": str(probe["stderr"]).strip(),
            }
        tts_probe = run_capture([voice, "tts-probe", "--json"], timeout=10.0)
        if tts_probe["ok"] and tts_probe["stdout"]:
            try:
                status["tts"] = json.loads(str(tts_probe["stdout"]))
            except json.JSONDecodeError:
                status["tts"] = {"raw": str(tts_probe["stdout"]).strip()}
        else:
            status["tts"] = {
                "ok": False,
                "rc": tts_probe["rc"],
                "stderr": str(tts_probe["stderr"]).strip(),
            }
        return status

    def read_body(self, limit: int) -> bytes:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0:
            return b""
        if length > limit:
            raise ValueError(f"request too large: {length} > {limit}")
        return self.rfile.read(length)

    def read_json(self) -> dict[str, object]:
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        if content_type != "application/json":
            raise ValueError("Content-Type application/json required")
        body = self.read_body(MAX_JSON_BYTES)
        if not body:
            return {}
        parsed = json.loads(body.decode("utf-8"))
        if not isinstance(parsed, dict):
            raise ValueError("json object required")
        return parsed

    def handle_codex_preview(self) -> None:
        try:
            payload = self.read_json()
            text = str(payload.get("text") or "").strip()
            if not text:
                raise ValueError("text required")
            preview = create_codex_preview(text)
        except (json.JSONDecodeError, ValueError, CodexPreviewError) as exc:
            self.send_json(
                {"ok": False, "stage": "codex_preview", "error": str(exc)},
                status=HTTPStatus.BAD_REQUEST,
            )
            return
        self.send_json(preview)

    def handle_codex_review(self) -> None:
        try:
            payload = self.read_json()
            canonical = str(payload.get("canonical_spec") or "")
            preview = review_edited_codex_spec(canonical)
        except (json.JSONDecodeError, ValueError, CodexPreviewError) as exc:
            self.send_json(
                {"ok": False, "stage": "codex_review", "error": str(exc)},
                status=HTTPStatus.BAD_REQUEST,
            )
            return
        self.send_json(preview)

    def handle_codex_run(self) -> None:
        try:
            payload = self.read_json()
            preview_id = str(payload.get("preview_id") or "")
            supplied_digest = str(payload.get("spec_sha256") or "")
            canonical = str(payload.get("canonical_spec") or "")
            confirmed = payload.get("confirmed") is True
            result = run_codex_preview(
                preview_id=preview_id,
                supplied_digest=supplied_digest,
                canonical=canonical,
                confirmed=confirmed,
            )
        except (json.JSONDecodeError, ValueError, CodexPreviewError) as exc:
            self.send_json(
                {"ok": False, "stage": "codex_run", "error": str(exc)},
                status=HTTPStatus.BAD_REQUEST,
            )
            return
        self.send_json(result)

    def handle_ask_text(self) -> None:
        try:
            payload = self.read_json()
            text = str(payload.get("text") or "").strip()
            mode = clean_mode(str(payload.get("mode") or "chat"))
            max_tokens = clamp_tokens(payload.get("max_tokens"))
        except (json.JSONDecodeError, ValueError) as exc:
            self.send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        if not text:
            self.send_json({"ok": False, "error": "text required"}, status=HTTPStatus.BAD_REQUEST)
            return
        if mode == "codex":
            try:
                preview = create_codex_preview(text)
            except CodexPreviewError as exc:
                self.send_json(
                    {"ok": False, "stage": "codex_preview", "error": str(exc)},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            self.send_json(preview)
            return
        answer = ask_brain(text, mode=mode, max_tokens=max_tokens)
        self.send_json(
            {
                "ok": bool(answer["ok"]),
                "mode": mode,
                "text": text,
                "answer": answer.get("answer", ""),
                "stderr": str(answer.get("stderr") or "").strip(),
                "rc": answer["rc"],
            },
            status=HTTPStatus.OK if answer["ok"] else HTTPStatus.BAD_GATEWAY,
        )

    def handle_audio(self, query: str) -> None:
        params = parse_qs(query)
        mode = clean_mode((params.get("mode") or ["chat"])[0])
        max_tokens = clamp_tokens((params.get("max_tokens") or ["180"])[0])
        content_type = self.headers.get("Content-Type", "application/octet-stream")
        TMP_DIR.mkdir(parents=True, exist_ok=True)
        stem = now_id()
        raw_path = TMP_DIR / f"{stem}{audio_suffix(content_type)}"
        wav_path = TMP_DIR / f"{stem}.wav"
        try:
            body = self.read_body(MAX_AUDIO_BYTES)
            if not body:
                self.send_json({"ok": False, "error": "audio body required"}, status=HTTPStatus.BAD_REQUEST)
                return
            raw_path.write_bytes(body)
            converted = convert_to_wav(raw_path, wav_path)
            if not converted["ok"]:
                self.send_json(
                    {
                        "ok": False,
                        "stage": "convert",
                        "stderr": str(converted.get("stderr") or "").strip(),
                        "rc": converted.get("rc"),
                    },
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            transcribed = transcribe_wav(wav_path)
            text = str(transcribed.get("text") or "").strip()
            if not transcribed["ok"] or not text:
                self.send_json(
                    {
                        "ok": False,
                        "stage": "transcribe",
                        "text": text,
                        "stderr": str(transcribed.get("stderr") or "").strip(),
                        "rc": transcribed.get("rc"),
                    },
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            if mode == "codex":
                try:
                    preview = create_codex_preview(text)
                except CodexPreviewError as exc:
                    self.send_json(
                        {"ok": False, "stage": "codex_preview", "error": str(exc)},
                        status=HTTPStatus.BAD_REQUEST,
                    )
                    return
                # The raw STT result stays inside this request. Codex mode
                # returns only the validated canonical spec and authorization
                # metadata.
                self.send_json(preview)
                return
            answer = ask_brain(text, mode=mode, max_tokens=max_tokens)
            self.send_json(
                {
                    "ok": bool(answer["ok"]),
                    "mode": mode,
                    "transcript": text,
                    "answer": answer.get("answer", ""),
                    "stderr": str(answer.get("stderr") or "").strip(),
                    "rc": answer["rc"],
                },
                status=HTTPStatus.OK if answer["ok"] else HTTPStatus.BAD_GATEWAY,
            )
        except ValueError as exc:
            self.send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
        finally:
            if not KEEP_AUDIO:
                raw_path.unlink(missing_ok=True)
                wav_path.unlink(missing_ok=True)

    def handle_say(self) -> None:
        self.send_json(
            {
                "ok": False,
                "error": (
                    "legacy server-side browser playback is disabled; "
                    "reload the current Voice Console"
                ),
            },
            status=HTTPStatus.GONE,
        )

    def handle_synthesize(self) -> None:
        try:
            payload = self.read_json()
            text = str(payload.get("text") or "").strip()
            audio = synthesize_browser_wav(text)
        except (json.JSONDecodeError, ValueError, BrowserTtsError) as exc:
            self.send_json(
                {"ok": False, "stage": "synthesize", "error": str(exc)},
                status=HTTPStatus.BAD_REQUEST,
            )
            return
        self.send_wav(audio)

    def handle_action_route(self) -> None:
        try:
            payload = self.read_json()
            text = str(payload.get("text") or "").strip()
        except (json.JSONDecodeError, ValueError) as exc:
            self.send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        if not text:
            self.send_json({"ok": False, "error": "text required"}, status=HTTPStatus.BAD_REQUEST)
            return
        route = route_action_text(text)
        self.send_json(route, status=HTTPStatus.OK if route.get("ok") else HTTPStatus.BAD_GATEWAY)

    def handle_action_queue(self) -> None:
        try:
            payload = self.read_json()
            text = str(payload.get("text") or "").strip()
        except (json.JSONDecodeError, ValueError) as exc:
            self.send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        if not text:
            self.send_json({"ok": False, "error": "text required"}, status=HTTPStatus.BAD_REQUEST)
            return
        queued = queue_action_text(text)
        status = HTTPStatus.OK if queued.get("ok") else HTTPStatus.BAD_GATEWAY
        self.send_json({**queued, "queue": action_queue_payload()}, status=status)

    def handle_action_approve(self) -> None:
        try:
            payload = self.read_json()
            kind = str(payload.get("kind") or "")
            item_id = int(payload.get("id") or 0)
        except (json.JSONDecodeError, ValueError, TypeError) as exc:
            self.send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        if item_id <= 0 or kind not in {"approval", "agenda"}:
            self.send_json({"ok": False, "error": "kind approval|agenda and positive id required"}, status=HTTPStatus.BAD_REQUEST)
            return
        if kind == "agenda":
            result, parsed = run_json(
                [repo_command("ctos-ai"), "agenda-confirm", str(item_id), "--yes", "--json"],
                timeout=20.0,
            )
            payload_out = parsed if isinstance(parsed, dict) else {}
        else:
            result = run_capture([repo_command("ctos-ai"), "approve", str(item_id)], timeout=120.0)
            payload_out = {}
        self.send_json(
            {
                "ok": bool(result.get("ok")),
                "kind": kind,
                "id": item_id,
                "result": payload_out,
                "stdout": str(result.get("stdout") or "").strip(),
                "stderr": str(result.get("stderr") or "").strip(),
                "rc": result.get("rc", 0),
                "queue": action_queue_payload(),
            },
            status=HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_GATEWAY,
        )

    def handle_action_reject(self) -> None:
        try:
            payload = self.read_json()
            kind = str(payload.get("kind") or "")
            item_id = int(payload.get("id") or 0)
            reason = str(payload.get("reason") or "rejected from Voice Console")
        except (json.JSONDecodeError, ValueError, TypeError) as exc:
            self.send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        if item_id <= 0 or kind not in {"approval", "agenda"}:
            self.send_json({"ok": False, "error": "kind approval|agenda and positive id required"}, status=HTTPStatus.BAD_REQUEST)
            return
        if kind == "agenda":
            result, parsed = run_json(
                [repo_command("ctos-ai"), "agenda-reject", str(item_id), "--reason", reason, "--json"],
                timeout=20.0,
            )
            payload_out = parsed if isinstance(parsed, dict) else {}
        else:
            result = run_capture([repo_command("ctos-ai"), "reject", str(item_id), "--reason", reason], timeout=20.0)
            payload_out = {}
        self.send_json(
            {
                "ok": bool(result.get("ok")),
                "kind": kind,
                "id": item_id,
                "result": payload_out,
                "stdout": str(result.get("stdout") or "").strip(),
                "stderr": str(result.get("stderr") or "").strip(),
                "rc": result.get("rc", 0),
                "queue": action_queue_payload(),
            },
            status=HTTPStatus.OK if result.get("ok") else HTTPStatus.BAD_GATEWAY,
        )

    def send_json(self, payload: dict[str, object], *, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_wav(self, body: bytes) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "audio/wav")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class VoiceConsoleServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main() -> int:
    parser = argparse.ArgumentParser(description="CTOS localhost browser voice console")
    parser.add_argument("--host", default=os.environ.get("CTOS_VOICE_CONSOLE_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("CTOS_VOICE_CONSOLE_PORT", "8770")))
    args = parser.parse_args()

    if not STATIC.exists():
        print(f"static directory not found: {STATIC}", file=sys.stderr)
        return 2
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    server = VoiceConsoleServer((args.host, args.port), VoiceConsoleHandler)
    print(f"CTOS voice console listening on http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("stopping voice console", file=sys.stderr)
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
