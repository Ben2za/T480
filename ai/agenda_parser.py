from __future__ import annotations

import re
import shlex
import unicodedata
from datetime import date, timedelta
from typing import Any


WEEKDAYS = {
    "lundi": 0,
    "mardi": 1,
    "mercredi": 2,
    "jeudi": 3,
    "vendredi": 4,
    "samedi": 5,
    "dimanche": 6,
}

LEADING_PATTERNS = [
    r"^(ajoute|ajouter|cree|creer|crée|créer|note|noter|mets|mettre)\b",
    r"^(une|un|la|le|ma|mon|mes|des)\s+(tache|tâche|task)\b",
    r"^(une|un|la|le)\s+(rendez vous|rendez-vous|rdv)\b",
]


def normalize_text(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.casefold())
    stripped = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    cleaned = re.sub(r"[^a-z0-9:/.-]+", " ", stripped)
    return " ".join(cleaned.split())


def next_weekday(today: date, weekday: int) -> date:
    days = (weekday - today.weekday()) % 7
    if days == 0:
        days = 7
    return today + timedelta(days=days)


def parse_due_date(normalized: str, *, today: date) -> tuple[str | None, str | None, list[str]]:
    warnings: list[str] = []
    if "apres demain" in normalized or "apres-demain" in normalized:
        return (today + timedelta(days=2)).isoformat(), "apres-demain", warnings
    if "demain" in normalized:
        return (today + timedelta(days=1)).isoformat(), "demain", warnings
    if "aujourd hui" in normalized or "aujourd-hui" in normalized:
        return today.isoformat(), "aujourd'hui", warnings

    iso_match = re.search(r"\b(20[0-9]{2}-[01][0-9]-[0-3][0-9])\b", normalized)
    if iso_match:
        try:
            return date.fromisoformat(iso_match.group(1)).isoformat(), iso_match.group(1), warnings
        except ValueError:
            warnings.append(f"ignored invalid ISO date: {iso_match.group(1)}")

    day_month = re.search(r"\b([0-3]?[0-9])[/-]([01]?[0-9])(?:[/-](20[0-9]{2}))?\b", normalized)
    if day_month:
        day = int(day_month.group(1))
        month = int(day_month.group(2))
        year = int(day_month.group(3) or today.year)
        try:
            parsed = date(year, month, day)
        except ValueError:
            warnings.append(f"ignored invalid date: {day_month.group(0)}")
        else:
            if day_month.group(3) is None and parsed < today:
                parsed = date(year + 1, month, day)
            return parsed.isoformat(), day_month.group(0), warnings

    for name, weekday in WEEKDAYS.items():
        if re.search(rf"\b{name}\b", normalized):
            return next_weekday(today, weekday).isoformat(), name, warnings

    warnings.append("no due date found; task will be unscheduled")
    return None, None, warnings


def parse_estimate(normalized: str) -> tuple[int, str | None]:
    hour_match = re.search(r"\b([0-9]+)\s*(h|heure|heures)\b", normalized)
    if hour_match:
        return max(5, int(hour_match.group(1)) * 60), hour_match.group(0)
    minute_match = re.search(r"\b([0-9]+)\s*(m|min|minute|minutes)\b", normalized)
    if minute_match:
        return max(5, int(minute_match.group(1))), minute_match.group(0)
    if "une heure" in normalized:
        return 60, "une heure"
    if "demi heure" in normalized or "demi-heure" in normalized:
        return 30, "demi-heure"
    return 30, None


def parse_priority(normalized: str) -> tuple[int, str | None]:
    priority_match = re.search(r"\bpriorite\s*([1-5])\b", normalized)
    if priority_match:
        return int(priority_match.group(1)), priority_match.group(0)
    if {"urgent", "urgence"} & set(normalized.split()):
        return 5, "urgent"
    if {"important", "importante"} & set(normalized.split()):
        return 4, "important"
    if {"tranquille", "faible", "plus tard"} & set(normalized.split()):
        return 2, "low"
    return 3, None


def strip_known_parts(text: str, normalized: str, due_label: str | None, estimate_label: str | None, priority_label: str | None) -> str:
    title = text.strip()
    replacements = [
        r"\bdans l[' ]agenda\b",
        r"\ba l[' ]agenda\b",
        r"\bà l[' ]agenda\b",
        r"\bpour mon agenda\b",
        r"\bpour l[' ]agenda\b",
        r"\bpriorit[ée]\s*[1-5]\b",
        r"\b(urgent|urgence|important|importante)\b",
        r"\btache\b",
        r"\btâche\b",
    ]
    labels = [due_label, estimate_label, priority_label]
    for label in labels:
        if label:
            replacements.append(re.escape(label))
    for pattern in replacements:
        title = re.sub(pattern, " ", title, flags=re.IGNORECASE)
    for pattern in LEADING_PATTERNS:
        title = re.sub(pattern, " ", title, flags=re.IGNORECASE).strip()
    title = re.sub(r"\b(une|un|la|le)\s+(rendez vous|rendez-vous|rdv)\b", "rendez-vous", title, flags=re.IGNORECASE)
    title = re.sub(r"\s+", " ", title).strip(" .,;:-")
    if not title:
        if "rdv" in normalized or "rendez" in normalized:
            title = "rendez-vous"
    return title


def agenda_command(proposal: dict[str, Any], agenda_bin: str = "ctos-agenda") -> list[str]:
    command = [
        agenda_bin,
        "add",
        str(proposal["title"]),
        "--priority",
        str(proposal["priority"]),
        "--estimate",
        str(proposal["estimate_minutes"]),
    ]
    if proposal.get("due_date"):
        command.extend(["--due", str(proposal["due_date"])])
    if proposal.get("notes"):
        command.extend(["--notes", str(proposal["notes"])])
    return command


def parse_natural_agenda(text: str, *, today: date | None = None) -> dict[str, Any]:
    today = today or date.today()
    cleaned = " ".join(text.split())
    normalized = normalize_text(cleaned)
    due_date, due_label, warnings = parse_due_date(normalized, today=today)
    estimate, estimate_label = parse_estimate(normalized)
    priority, priority_label = parse_priority(normalized)
    title = strip_known_parts(cleaned, normalized, due_label, estimate_label, priority_label)

    recognized = bool(title)
    if title.lower() in {"agenda", "tache", "tâche", "task"}:
        recognized = False
        warnings.append("task title is too generic")
    if not title:
        warnings.append("missing task title")

    proposal = {
        "schema": 1,
        "input": cleaned,
        "normalized": normalized,
        "recognized": recognized,
        "title": title,
        "due_date": due_date,
        "due_label": due_label,
        "priority": priority,
        "estimate_minutes": estimate,
        "notes": "",
        "warnings": warnings,
    }
    proposal["command"] = agenda_command(proposal)
    proposal["command_text"] = shlex.join(proposal["command"])
    return proposal


def format_agenda_proposal(proposal: dict[str, Any]) -> str:
    lines = [
        "CTOS agenda proposal",
        "====================",
        f"input     {proposal.get('input')}",
        f"recognized {proposal.get('recognized')}",
        f"title     {proposal.get('title') or '-'}",
        f"due       {proposal.get('due_date') or '-'}",
        f"priority  {proposal.get('priority')}",
        f"estimate  {proposal.get('estimate_minutes')} min",
        f"command   {proposal.get('command_text')}",
    ]
    warnings = proposal.get("warnings")
    if isinstance(warnings, list) and warnings:
        lines.append("warnings")
        for warning in warnings:
            lines.append(f"  - {warning}")
    lines.append("next      run with --commit --yes to write this agenda task")
    return "\n".join(lines)
