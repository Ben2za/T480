from __future__ import annotations

import difflib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
INTENTS_PATH = ROOT / "ai" / "voice_intents_fr.json"


class IntentCatalogError(ValueError):
    pass


def load_intent_catalog(path: Path = INTENTS_PATH) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise IntentCatalogError(f"cannot read {path}: {error}") from error
    except json.JSONDecodeError as error:
        raise IntentCatalogError(f"invalid JSON in {path}: {error}") from error
    if not isinstance(data, dict):
        raise IntentCatalogError(f"{path} must contain a JSON object")
    return data


def intent_entries(path: Path = INTENTS_PATH) -> list[dict[str, Any]]:
    intents = load_intent_catalog(path).get("intents", [])
    return [item for item in intents if isinstance(item, dict)]


def normalize_text(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.casefold())
    stripped = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    cleaned = re.sub(r"[^a-z0-9]+", " ", stripped)
    return " ".join(cleaned.split())


def score_phrase(text: str, phrase: str) -> float:
    normalized_text = normalize_text(text)
    normalized_phrase = normalize_text(phrase)
    if not normalized_text or not normalized_phrase:
        return 0.0
    if normalized_text == normalized_phrase:
        return 1.0
    if normalized_phrase in normalized_text or normalized_text in normalized_phrase:
        return 0.94
    text_tokens = set(normalized_text.split())
    phrase_tokens = set(normalized_phrase.split())
    overlap = 0.0
    if text_tokens and phrase_tokens:
        overlap = len(text_tokens & phrase_tokens) / max(len(text_tokens), len(phrase_tokens))
    ratio = difflib.SequenceMatcher(None, normalized_text, normalized_phrase).ratio()
    return round(max(ratio, overlap), 4)


def phrase_rows(path: Path = INTENTS_PATH) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for intent in intent_entries(path):
        for phrase in intent.get("phrases", []):
            if not isinstance(phrase, str):
                continue
            command = intent.get("command")
            rows.append({
                "intent_id": intent.get("id"),
                "tier": intent.get("tier"),
                "phrase": phrase,
                "normalized": normalize_text(phrase),
                "command": command if isinstance(command, list) else [],
                "spoken_reply": intent.get("spoken_reply"),
            })
    return rows


def match_intent(text: str, threshold: float = 0.72, path: Path = INTENTS_PATH) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    for intent in intent_entries(path):
        command = intent.get("command")
        phrases = intent.get("phrases", [])
        if not isinstance(command, list) or not isinstance(phrases, list):
            continue
        for phrase in phrases:
            if not isinstance(phrase, str):
                continue
            score = score_phrase(text, phrase)
            candidates.append({
                "intent_id": intent.get("id"),
                "tier": intent.get("tier"),
                "command": command,
                "phrase": phrase,
                "score": score,
                "spoken_reply": intent.get("spoken_reply"),
            })
    candidates.sort(key=lambda item: float(item.get("score") or 0), reverse=True)
    best = candidates[0] if candidates else None
    return {
        "text": text,
        "normalized": normalize_text(text),
        "threshold": threshold,
        "matched": bool(best and float(best.get("score") or 0) >= threshold),
        "best": best,
        "candidates": candidates,
    }


def validate_intent_catalog(path: Path = INTENTS_PATH) -> list[str]:
    errors: list[str] = []
    try:
        items = load_intent_catalog(path).get("intents")
    except IntentCatalogError as error:
        return [str(error)]
    if not isinstance(items, list) or not items:
        return ["voice_intents_fr.json needs a non-empty intents list"]
    seen: set[str] = set()
    for intent in items:
        if not isinstance(intent, dict):
            errors.append("each intent entry must be an object")
            continue
        intent_id = str(intent.get("id") or "")
        phrases = intent.get("phrases")
        command = intent.get("command")
        if not intent_id:
            errors.append("intent without id")
        if intent_id in seen:
            errors.append(f"duplicate intent id: {intent_id}")
        seen.add(intent_id)
        if not isinstance(phrases, list) or not all(isinstance(item, str) and item for item in phrases):
            errors.append(f"{intent_id or 'unknown intent'} needs non-empty string phrases")
        if not isinstance(command, list) or not all(isinstance(item, str) and item for item in command):
            errors.append(f"{intent_id or 'unknown intent'} needs a command string list")
    return errors
