from __future__ import annotations

import re
from typing import Any

from ai.agenda_parser import parse_natural_agenda
from ai.voice_intents import match_intent, normalize_text


SAFE_COMMAND_ROOT = "ctos-ai"
SAFE_DIRECT_TIERS = {0, 1}


def _top_candidates(match: dict[str, Any], limit: int = 5) -> list[dict[str, Any]]:
    candidates = match.get("candidates", [])
    if not isinstance(candidates, list):
        return []
    rows: list[dict[str, Any]] = []
    for item in candidates[:limit]:
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                "intent_id": item.get("intent_id"),
                "score": item.get("score"),
                "phrase": item.get("phrase"),
                "tier": item.get("tier"),
            }
        )
    return rows


def _unmatched_category(normalized: str) -> tuple[str, str]:
    tokens = set(normalized.split())
    agenda_verbs = {"ajoute", "ajouter", "cree", "creer", "note", "noter", "mets", "mettre"}
    agenda_terms = {"agenda", "tache", "task", "rendez", "rdv", "calendrier"}
    date_terms = {
        "demain",
        "apres",
        "aujourd",
        "hui",
        "lundi",
        "mardi",
        "mercredi",
        "jeudi",
        "vendredi",
        "samedi",
        "dimanche",
    }
    looks_scheduled = bool(date_terms & tokens) or bool(re.search(r"\b([0-9]+)\s*(h|min|minute|minutes)\b", normalized))
    if agenda_verbs & tokens and (agenda_terms & tokens or looks_scheduled):
        return (
            "agenda_candidate",
            "agenda mutation needs a structured task title/date or an approval-aware parser before execution",
        )
    if {"demarre", "lance", "ouvre", "eteins", "stop", "arrete"} & tokens and {"kali", "vm", "vms", "machine"} & tokens:
        return (
            "vm_candidate",
            "VM lifecycle requests are Tier 2 when they mutate state and must go through CTOS approval",
        )
    if {"organise", "planifie", "resume", "explique", "aide"} & tokens:
        return (
            "assistant_candidate",
            "natural-language assistant request; route to the open STT/LLM rail once the runtime is selected",
        )
    return (
        "unclassified",
        "no deterministic CTOS intent matched; keep as transcript text until the natural-language rail is active",
    )


def plan_text_action(text: str, *, source: str = "typed", threshold: float = 0.72) -> dict[str, Any]:
    cleaned = " ".join(text.split())
    match = match_intent(cleaned, threshold=threshold)
    normalized = str(match.get("normalized") or normalize_text(cleaned))
    best = match.get("best") if isinstance(match.get("best"), dict) else None

    plan: dict[str, Any] = {
        "schema": 1,
        "source": source,
        "input": cleaned,
        "normalized": normalized,
        "threshold": threshold,
        "matched": bool(match.get("matched")),
        "mode": "deterministic_intent" if match.get("matched") else "natural_language_pending",
        "intent_id": None,
        "score": None,
        "matched_phrase": None,
        "tier": None,
        "command": [],
        "spoken_reply": None,
        "safe_to_execute": False,
        "requires_approval": False,
        "reason": "",
        "next": "",
        "top_candidates": _top_candidates(match),
    }

    if not plan["matched"] or best is None:
        category, reason = _unmatched_category(normalized)
        plan.update(
            {
                "category": category,
                "reason": reason,
                "next": "do not execute automatically; pass transcript to the future open-ended Jarvis parser or ask for clarification",
            }
        )
        if category == "agenda_candidate":
            agenda_proposal = parse_natural_agenda(cleaned)
            plan["agenda_proposal"] = agenda_proposal
            if agenda_proposal.get("recognized"):
                plan["next"] = "review the agenda_proposal, then run ctos-ai agenda-propose --commit --yes if it is correct"
        return plan

    command = best.get("command") if isinstance(best.get("command"), list) else []
    tier = best.get("tier")
    safe = (
        isinstance(tier, int)
        and tier in SAFE_DIRECT_TIERS
        and bool(command)
        and command[0] == SAFE_COMMAND_ROOT
    )
    requires_approval = isinstance(tier, int) and tier > max(SAFE_DIRECT_TIERS)
    reason = "safe CTOS read/reversible command" if safe else "intent matched but is not directly executable"
    if requires_approval:
        reason = "matched intent is above the safe direct-execution tier"
    elif command and command[0] != SAFE_COMMAND_ROOT:
        reason = "matched command is not owned by ctos-ai"

    plan.update(
        {
            "intent_id": best.get("intent_id"),
            "score": best.get("score"),
            "matched_phrase": best.get("phrase"),
            "tier": tier,
            "command": command,
            "spoken_reply": best.get("spoken_reply"),
            "safe_to_execute": safe,
            "requires_approval": requires_approval,
            "reason": reason,
            "next": "execute through ctos-ai" if safe else "create a CTOS approval or ask for clarification",
        }
    )
    return plan


def format_plan(plan: dict[str, Any]) -> str:
    lines = [
        "CTOS action plan",
        "================",
        f"source    {plan.get('source')}",
        f"input     {plan.get('input')}",
        f"mode      {plan.get('mode')}",
        f"matched   {plan.get('matched')}",
    ]
    if plan.get("matched"):
        command = plan.get("command") if isinstance(plan.get("command"), list) else []
        lines.extend(
            [
                f"intent    {plan.get('intent_id')}",
                f"score     {plan.get('score')} via {plan.get('matched_phrase')}",
                f"tier      {plan.get('tier')}",
                f"command   {' '.join(command)}",
                f"safe      {plan.get('safe_to_execute')}",
            ]
        )
    else:
        lines.append(f"category  {plan.get('category')}")
        proposal = plan.get("agenda_proposal")
        if isinstance(proposal, dict):
            lines.extend(
                [
                    f"agenda    {proposal.get('title') or '-'}",
                    f"due       {proposal.get('due_date') or '-'}",
                    f"priority  {proposal.get('priority')}",
                    f"estimate  {proposal.get('estimate_minutes')} min",
                    f"proposal  {proposal.get('command_text')}",
                ]
            )
    lines.extend(
        [
            f"reason    {plan.get('reason')}",
            f"next      {plan.get('next')}",
        ]
    )
    return "\n".join(lines)
