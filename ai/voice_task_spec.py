"""Fail-closed boundary for transcript-free Voice-to-Codex task specs.

This module performs no writes, logging, model calls, network access, or Codex
execution.  A caller gets either a normalized, bounded object or a validation
error which never includes the rejected value.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any


WORKSPACE = Path("/home/operator/T480")
WORKSPACE_TEXT = str(WORKSPACE)
SCHEMA_VERSION = "ctos.voice_task.v1"
RESULT_SCHEMA_VERSION = "ctos.codex_readonly_result.v1"

MAX_INPUT_BYTES = 16_384
MAX_CANONICAL_BYTES = 8_192
MAX_RAW_CHARACTERS = 32_768
MAX_CONTAINER_NODES = 128

_FIELDS = (
    "schema_version",
    "goal",
    "workspace",
    "allowed_scope",
    "constraints",
    "deliverable",
    "acceptance_checks",
    "approval_class",
    "clarification_state",
)
_RESULT_FIELDS = (
    "schema_version",
    "summary",
    "findings",
    "checks",
    "clarifications",
)
_BANNED_NAME_TOKENS = {
    "transcript",
    "audio",
    "raw",
    "shell",
    "command",
    "token",
    "key",
    "password",
    "credential",
}

_SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE),
    re.compile(r"\b(?:sk-(?:proj-)?|gh[pousr]_|github_pat_|glpat-|xox[baprs]-)[A-Za-z0-9_-]{8,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]{8,}=*", re.IGNORECASE),
    re.compile(
        r"\b(?:api[ _-]?key|access[ _-]?token|auth[ _-]?token|token|password|passwd|"
        r"credential|client[ _-]?secret|secret)\s*[:=]\s*[^\s,;]{4,}",
        re.IGNORECASE,
    ),
    re.compile(r"\b[a-z][a-z0-9+.-]*://[^\s/:@]+:[^\s/@]+@", re.IGNORECASE),
)


class VoiceTaskSpecError(ValueError):
    """Raised when a task spec or bounded Codex result fails validation."""


def _fail(message: str) -> None:
    raise VoiceTaskSpecError(message)


def _name_tokens(name: str) -> set[str]:
    camel_split = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name)
    return {item for item in re.split(r"[^a-z0-9]+", camel_split.casefold()) if item}


def _guard_shape_and_names(value: object) -> None:
    """Bound arbitrary Python objects before field-specific processing."""

    stack: list[tuple[object, int]] = [(value, 0)]
    seen: set[int] = set()
    characters = 0
    nodes = 0
    while stack:
        current, depth = stack.pop()
        if depth > 4:
            _fail("input nesting exceeds the boundary")
        if isinstance(current, dict):
            identity = id(current)
            if identity in seen:
                _fail("repeated or cyclic containers are not accepted")
            seen.add(identity)
            nodes += 1
            for key, child in current.items():
                if not isinstance(key, str):
                    _fail("all field names must be strings")
                characters += len(key)
                banned = _name_tokens(key) & _BANNED_NAME_TOKENS
                if banned:
                    _fail("a banned field name is present")
                stack.append((child, depth + 1))
        elif isinstance(current, list):
            identity = id(current)
            if identity in seen:
                _fail("repeated or cyclic containers are not accepted")
            seen.add(identity)
            nodes += 1
            stack.extend((child, depth + 1) for child in current)
        elif isinstance(current, str):
            characters += len(current)
        elif current is not None and not isinstance(current, (bool, int, float)):
            _fail("input contains a non-JSON value")
        if nodes > MAX_CONTAINER_NODES or characters > MAX_RAW_CHARACTERS:
            _fail("input exceeds the total boundary")


def _contains_secret(text: str) -> bool:
    return any(pattern.search(text) is not None for pattern in _SECRET_PATTERNS)


def _normalize_string(value: object, field: str, *, minimum: int, maximum: int) -> str:
    if not isinstance(value, str):
        _fail(f"{field} must be a string")
    if any(unicodedata.category(char) in {"Cc", "Cf", "Cs"} and not char.isspace() for char in value):
        _fail(f"{field} contains a forbidden control character")
    normalized = unicodedata.normalize("NFC", " ".join(value.split()))
    if len(normalized) < minimum:
        _fail(f"{field} is empty or too short")
    if len(normalized) > maximum:
        _fail(f"{field} exceeds its length limit")
    if _contains_secret(normalized):
        _fail(f"{field} contains secret-like content")
    return normalized


def _normalize_string_list(
    value: object,
    field: str,
    *,
    minimum: int,
    maximum: int,
    item_maximum: int,
) -> list[str]:
    if not isinstance(value, list):
        _fail(f"{field} must be a list")
    if not minimum <= len(value) <= maximum:
        _fail(f"{field} violates its list limit")
    normalized = [
        _normalize_string(item, f"{field} item", minimum=1, maximum=item_maximum)
        for item in value
    ]
    if len(set(normalized)) != len(normalized):
        _fail(f"{field} contains duplicate normalized items")
    return normalized


def _validate_scope_item(item: str) -> None:
    if item.startswith("/") or item.endswith("/") or "//" in item or "\\" in item:
        _fail("allowed_scope contains a non-canonical path")
    parts = item.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        _fail("allowed_scope contains traversal or a non-canonical path")
    resolved = (WORKSPACE / item).resolve(strict=False)
    try:
        resolved.relative_to(WORKSPACE)
    except ValueError:
        _fail("allowed_scope resolves outside the workspace")


def validate_spec(spec: dict[str, Any]) -> dict[str, Any]:
    """Return a normalized copy of a valid V1 read-only task spec."""

    _guard_shape_and_names(spec)
    if not isinstance(spec, dict):
        _fail("task spec must be a JSON object")
    unknown = set(spec) - set(_FIELDS)
    missing = set(_FIELDS) - set(spec)
    if unknown:
        _fail("task spec contains unknown fields")
    if missing:
        _fail("task spec is missing required fields")

    if spec["schema_version"] != SCHEMA_VERSION:
        _fail("unsupported schema_version")
    if spec["workspace"] != WORKSPACE_TEXT:
        _fail("workspace must be the exact resolved repository path")
    if spec["approval_class"] != "read_only":
        _fail("approval_class must be read_only")
    if spec["clarification_state"] != "resolved":
        _fail("clarification_state must be resolved")

    allowed_scope = _normalize_string_list(
        spec["allowed_scope"], "allowed_scope", minimum=1, maximum=16, item_maximum=160
    )
    for item in allowed_scope:
        _validate_scope_item(item)

    normalized: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "goal": _normalize_string(spec["goal"], "goal", minimum=1, maximum=400),
        "workspace": WORKSPACE_TEXT,
        "allowed_scope": allowed_scope,
        "constraints": _normalize_string_list(
            spec["constraints"], "constraints", minimum=0, maximum=12, item_maximum=240
        ),
        "deliverable": _normalize_string(
            spec["deliverable"], "deliverable", minimum=1, maximum=400
        ),
        "acceptance_checks": _normalize_string_list(
            spec["acceptance_checks"],
            "acceptance_checks",
            minimum=1,
            maximum=12,
            item_maximum=240,
        ),
        "approval_class": "read_only",
        "clarification_state": "resolved",
    }
    encoded = json.dumps(
        normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    if len(encoded) > MAX_CANONICAL_BYTES:
        _fail("canonical task spec exceeds the total byte limit")
    return normalized


def _reject_duplicate_fields(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _fail("duplicate JSON field name rejected")
        result[key] = value
    return result


def load_and_validate(path: Path | str) -> dict[str, Any]:
    """Read one bounded UTF-8 JSON file and validate it without persisting data."""

    try:
        with Path(path).open("rb") as stream:
            payload = stream.read(MAX_INPUT_BYTES + 1)
    except OSError as error:
        raise VoiceTaskSpecError("cannot read task spec") from error
    if len(payload) > MAX_INPUT_BYTES:
        _fail("task spec file exceeds the input byte limit")
    try:
        text = payload.decode("utf-8")
        data = json.loads(text, object_pairs_hook=_reject_duplicate_fields)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise VoiceTaskSpecError("task spec must be one valid UTF-8 JSON object") from error
    return validate_spec(data)


def canonical_json(spec: dict[str, Any]) -> str:
    """Return deterministic compact UTF-8 JSON after full revalidation."""

    normalized = validate_spec(spec)
    return json.dumps(
        normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )


def spec_digest(spec: dict[str, Any]) -> str:
    """Return the lowercase SHA-256 hex digest of canonical_json(spec)."""

    return hashlib.sha256(canonical_json(spec).encode("utf-8")).hexdigest()


def validate_codex_result(result: object) -> dict[str, Any]:
    """Validate and normalize one bounded read-only Codex result object."""

    _guard_shape_and_names(result)
    if not isinstance(result, dict):
        _fail("Codex result must be a JSON object")
    unknown = set(result) - set(_RESULT_FIELDS)
    missing = set(_RESULT_FIELDS) - set(result)
    if unknown:
        _fail("Codex result contains unknown fields")
    if missing:
        _fail("Codex result is missing required fields")
    if result["schema_version"] != RESULT_SCHEMA_VERSION:
        _fail("unsupported Codex result schema_version")
    normalized: dict[str, Any] = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "summary": _normalize_string(result["summary"], "summary", minimum=1, maximum=2_000),
        "findings": _normalize_string_list(
            result["findings"], "findings", minimum=0, maximum=24, item_maximum=800
        ),
        "checks": _normalize_string_list(
            result["checks"], "checks", minimum=0, maximum=24, item_maximum=800
        ),
        "clarifications": _normalize_string_list(
            result["clarifications"], "clarifications", minimum=0, maximum=12, item_maximum=500
        ),
    }
    encoded = json.dumps(
        normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    if len(encoded) > MAX_CANONICAL_BYTES:
        _fail("Codex result exceeds the total byte limit")
    return normalized
