#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import time
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

from ai.voice_task_spec import (
    VoiceTaskSpecError,
    canonical_json,
    spec_digest,
    validate_spec,
)


ROOT = Path(__file__).resolve().parents[1]
TASK_SCHEMA_PATH = ROOT / "ai" / "voice_task_spec.schema.json"
DEFAULT_OLLAMA_URL = os.environ.get("CTOS_OPENJARVIS_OLLAMA", "http://127.0.0.1:11435")
DEFAULT_MODEL = os.environ.get("CTOS_OPENJARVIS_MODEL", "qwen2.5-coder:1.5b")
MAX_TRANSCRIPT_CHARS = 4000
MAX_RESPONSE_BYTES = 64 * 1024
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}

SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z0-9 ]*(?:PRIVATE KEY|OPENSSH KEY)-----", re.IGNORECASE),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{12,}\b", re.IGNORECASE),
    re.compile(
        r"\b(?:api[_ -]?key|password|mot\s+de\s+passe|secret|token|credential)\s*[:=]\s*\S{6,}",
        re.IGNORECASE,
    ),
)
EXPLICIT_PATH_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_.-])((?:[A-Za-z0-9_.-]+/)+(?:[A-Za-z0-9_.-]+)?)(?![A-Za-z0-9_.-])"
)


class VoiceTaskCompilerError(RuntimeError):
    pass


def normalize_transcript(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    return " ".join(normalized.split())


def validate_transcript(text: str) -> str:
    cleaned = normalize_transcript(text)
    if not cleaned:
        raise VoiceTaskCompilerError("voice input is empty")
    if len(cleaned) > MAX_TRANSCRIPT_CHARS:
        raise VoiceTaskCompilerError("voice input exceeds the bounded compiler limit")
    if any(pattern.search(cleaned) for pattern in SECRET_PATTERNS):
        raise VoiceTaskCompilerError("voice input was rejected by the local secret guard")
    return cleaned


def explicit_workspace_paths(text: str) -> list[str]:
    """Extract canonical relative paths that the operator named explicitly."""

    paths: list[str] = []
    for match in EXPLICIT_PATH_PATTERN.finditer(text):
        candidate = match.group(1).rstrip("/")
        parts = candidate.split("/")
        if not candidate or any(part in {"", ".", ".."} for part in parts):
            continue
        resolved = (ROOT / candidate).resolve(strict=False)
        try:
            resolved.relative_to(ROOT)
        except ValueError:
            continue
        if candidate not in paths:
            paths.append(candidate)
    return paths


def validate_local_ollama_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme != "http" or parsed.hostname not in LOOPBACK_HOSTS:
        raise VoiceTaskCompilerError("the voice compiler requires a loopback Ollama endpoint")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise VoiceTaskCompilerError("the voice compiler Ollama URL contains unsupported fields")
    if parsed.path not in {"", "/"}:
        raise VoiceTaskCompilerError("the voice compiler Ollama URL must not contain an API path")
    return value.rstrip("/")


def load_task_schema(path: Path = TASK_SCHEMA_PATH) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VoiceTaskCompilerError("the versioned voice task schema is unavailable") from exc
    if not isinstance(payload, dict):
        raise VoiceTaskCompilerError("the versioned voice task schema is invalid")
    return payload


def compiler_system_prompt(schema: dict[str, Any]) -> str:
    schema_json = json.dumps(schema, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return (
        "You are an untrusted local compiler from French or English voice requests to one bounded "
        "CTOS read-only task specification. Return exactly one JSON object matching the supplied "
        "schema. Never copy or mention the source transcript. Never add transcript, audio, raw, "
        "shell, command, token, key, password, credential, or secret fields. The workspace must be "
        f"exactly {ROOT}. The approval_class must be read_only. Every allowed_scope item must "
        "be a canonical relative repository path such as context, ai, scripts, or tests; put natural "
        "language restrictions in constraints, not allowed_scope. Use clarification_state resolved only "
        "when the goal, scope, deliverable, and checks are unambiguous; otherwise use "
        "needs_clarification. Do not infer credentials, destructive actions, public exposure, or "
        "workspace-write authority. Keep every field concise.\n\nJSON schema:\n"
        f"{schema_json}"
    )


def _post_generate(
    endpoint: str,
    payload: dict[str, Any],
    *,
    timeout: float,
    opener: Callable[..., Any],
) -> dict[str, Any]:
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with opener(request, timeout=timeout) as response:
            body = response.read(MAX_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as exc:
        raise VoiceTaskCompilerError(f"local compiler API failed with HTTP {exc.code}") from exc
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        raise VoiceTaskCompilerError("local compiler API is unavailable") from exc
    if len(body) > MAX_RESPONSE_BYTES:
        raise VoiceTaskCompilerError("local compiler response exceeds the bounded limit")
    try:
        parsed = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VoiceTaskCompilerError("local compiler API returned invalid JSON") from exc
    if not isinstance(parsed, dict):
        raise VoiceTaskCompilerError("local compiler API returned a non-object response")
    return parsed


def compile_transcript(
    text: str,
    *,
    model: str = DEFAULT_MODEL,
    ollama_url: str = DEFAULT_OLLAMA_URL,
    timeout: float = 120.0,
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> dict[str, Any]:
    transcript = validate_transcript(text)
    endpoint = f"{validate_local_ollama_url(ollama_url)}/api/generate"
    schema = load_task_schema()
    request_payload: dict[str, Any] = {
        "model": model,
        "prompt": transcript,
        "system": compiler_system_prompt(schema),
        "format": schema,
        "stream": False,
        "keep_alive": "2m",
        "options": {
            "temperature": 0,
            "num_ctx": 4096,
            "num_predict": 768,
        },
    }
    started = time.monotonic()
    response = _post_generate(endpoint, request_payload, timeout=timeout, opener=opener)
    compiled_text = response.get("response")
    if not isinstance(compiled_text, str) or not compiled_text.strip():
        raise VoiceTaskCompilerError("local compiler returned no task specification")
    if len(compiled_text.encode("utf-8")) > MAX_RESPONSE_BYTES:
        raise VoiceTaskCompilerError("local compiler task specification exceeds the bounded limit")
    try:
        compiled = json.loads(compiled_text)
    except json.JSONDecodeError as exc:
        raise VoiceTaskCompilerError("local compiler returned malformed task JSON") from exc
    if not isinstance(compiled, dict):
        raise VoiceTaskCompilerError("local compiler returned a non-object task specification")
    explicit_paths = explicit_workspace_paths(transcript)
    if explicit_paths:
        # The local model is untrusted and may broaden a named file into a
        # whole directory. Explicit operator paths are therefore an upper
        # bound, not merely a hint.
        compiled["allowed_scope"] = explicit_paths
    try:
        spec = validate_spec(compiled)
    except VoiceTaskSpecError as exc:
        raise VoiceTaskCompilerError(f"local compiler task rejected: {exc}") from exc
    canonical = canonical_json(spec)
    return {
        "ok": True,
        "spec": spec,
        "canonical": canonical,
        "digest": spec_digest(spec),
        "model": model,
        "elapsed_ms": round((time.monotonic() - started) * 1000),
        "scope_restricted_to_explicit_paths": bool(explicit_paths),
    }
