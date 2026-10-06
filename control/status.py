#!/usr/bin/env python3
from __future__ import annotations

import os
import json
import shutil
import sqlite3
import subprocess
import time
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
KALI_DOMAIN = "ctos-kali"
KALI_DISK = "/var/lib/libvirt/ctos/images/ctos-kali.qcow2"
KALI_SNAPSHOT_DIR = "/var/lib/libvirt/ctos/snapshots"
KALI_AGENT = ROOT / "scripts" / "ctos-kali-agent"
CORE_SCRIPT = ROOT / "scripts" / "ctos-core"
FLEET_SCRIPT = ROOT / "scripts" / "ctos-fleet"
AI_SCRIPT = ROOT / "scripts" / "ctos-ai"
AGENDA_SCRIPT = ROOT / "scripts" / "ctos-agenda"
AUDIO_SCRIPT = ROOT / "scripts" / "ctos-audio"
RUNTIME_PROFILES = ROOT / "ai" / "runtime_profiles.json"
_KALI_HEALTH_CACHE: dict[str, Any] = {"time": 0.0, "state": "", "data": {}}
_CORE_CACHE: dict[str, Any] = {"time": 0.0, "data": {}}
_FLEET_CACHE: dict[str, Any] = {"time": 0.0, "data": {}}


def _read(path: Path, default: str = "") -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return default


def _run(args: list[str], timeout: float = 1.5) -> dict[str, str | int]:
    try:
        proc = subprocess.run(
            args,
            capture_output=True,
            check=False,
            text=True,
            timeout=timeout,
        )
        return {
            "rc": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
        }
    except FileNotFoundError:
        return {"rc": 127, "stdout": "", "stderr": f"{args[0]} not found"}
    except subprocess.TimeoutExpired:
        return {"rc": 124, "stdout": "", "stderr": "timeout"}


def _virsh(args: list[str], readonly: bool = True, timeout: float = 1.5) -> dict[str, str | int]:
    command = ["virsh", "-c", "qemu:///system"]
    if readonly:
        command.append("--readonly")
    command.extend(args)
    return _run(command, timeout=timeout)


def _meminfo() -> dict[str, int]:
    data: dict[str, int] = {}
    for line in _read(Path("/proc/meminfo")).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        parts = value.strip().split()
        if parts and parts[0].isdigit():
            data[key] = int(parts[0]) * 1024
    return data


def _bytes_fmt(value: int) -> str:
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} {unit}"
        size /= 1024
    return f"{value} B"


def _parse_active_disk(stdout: str) -> str:
    for line in stdout.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("-") or stripped.lower().startswith("type "):
            continue
        parts = stripped.split()
        if len(parts) >= 4 and parts[0] == "file" and parts[1] == "disk" and parts[2] == "vda":
            return parts[3]
    return ""


def _snapshot_from_overlay(path: str) -> str:
    name = Path(path).name
    suffix = ".overlay.qcow2"
    if name.endswith(suffix):
        return name[: -len(suffix)]
    return ""


def _domain_state_label(raw: str) -> str:
    lowered = raw.strip().lower()
    if lowered.startswith("running"):
        return "running"
    if lowered.startswith("shut off") or lowered.startswith("shutoff"):
        return "shut off"
    if lowered.startswith("paused"):
        return "paused"
    return lowered or "unknown"


def cpu_stat() -> dict[str, int]:
    line = _read(Path("/proc/stat")).splitlines()[0]
    parts = line.split()[1:]
    values = [int(part) for part in parts]
    idle = values[3] + values[4] if len(values) > 4 else values[3]
    return {"idle": idle, "total": sum(values)}


def temperatures() -> list[dict[str, object]]:
    entries = []
    thermal_root = Path("/sys/class/thermal")
    for item in sorted(thermal_root.glob("thermal_zone*")):
        raw = _read(item / "temp")
        if not raw.lstrip("-").isdigit():
            continue
        temp_c = int(raw) / 1000
        label = _read(item / "type", item.name)
        entries.append({"name": label, "celsius": round(temp_c, 1)})
    return entries[:6]


def host_status() -> dict[str, object]:
    mem = _meminfo()
    total = mem.get("MemTotal", 0)
    available = mem.get("MemAvailable", 0)
    used = max(total - available, 0)
    load = os.getloadavg()
    uptime_seconds = int(float(_read(Path("/proc/uptime"), "0").split()[0]))
    root = shutil.disk_usage("/")
    home = shutil.disk_usage(str(Path.home()))
    return {
        "hostname": _read(Path("/proc/sys/kernel/hostname"), "unknown"),
        "uptime_seconds": uptime_seconds,
        "load": [round(item, 2) for item in load],
        "cpu": cpu_stat(),
        "temps": temperatures(),
        "memory": {
            "total": total,
            "used": used,
            "available": available,
            "used_percent": round((used / total) * 100, 1) if total else 0,
            "total_text": _bytes_fmt(total),
            "used_text": _bytes_fmt(used),
        },
        "disk": {
            "root_used_percent": round((root.used / root.total) * 100, 1),
            "root_free_text": _bytes_fmt(root.free),
            "home_used_percent": round((home.used / home.total) * 100, 1),
            "home_free_text": _bytes_fmt(home.free),
        },
    }


def battery_status() -> list[dict[str, str]]:
    entries = []
    for item in sorted(Path("/sys/class/power_supply").glob("BAT*")):
        entries.append(
            {
                "name": item.name,
                "capacity": _read(item / "capacity", "?"),
                "status": _read(item / "status", "unknown"),
            }
        )
    return entries


def network_status() -> list[dict[str, object]]:
    entries = []
    for item in sorted(Path("/sys/class/net").iterdir()):
        if item.name == "lo":
            continue
        rx = int(_read(item / "statistics" / "rx_bytes", "0") or "0")
        tx = int(_read(item / "statistics" / "tx_bytes", "0") or "0")
        entries.append(
            {
                "name": item.name,
                "state": _read(item / "operstate", "unknown"),
                "rx_text": _bytes_fmt(rx),
                "tx_text": _bytes_fmt(tx),
            }
        )
    return entries


def audio_status() -> dict[str, object]:
    data: dict[str, object] = {
        "available": False,
        "output": "VOL unavailable",
        "microphone": "MIC unavailable",
        "output_ok": False,
        "microphone_ok": False,
    }
    if not AUDIO_SCRIPT.exists():
        data["error"] = "ctos-audio helper not found"
        return data

    output = _run([str(AUDIO_SCRIPT), "status"], timeout=1.0)
    mic = _run([str(AUDIO_SCRIPT), "mic-status"], timeout=1.0)
    data.update(
        {
            "available": output["rc"] == 0 or mic["rc"] == 0,
            "output": output["stdout"] if output["rc"] == 0 else output["stderr"] or output["stdout"] or "VOL unavailable",
            "microphone": mic["stdout"] if mic["rc"] == 0 else mic["stderr"] or mic["stdout"] or "MIC unavailable",
            "output_ok": output["rc"] == 0,
            "microphone_ok": mic["rc"] == 0,
        }
    )
    return data


def _parse_virsh_domains(stdout: str, connection: str) -> list[dict[str, str]]:
    domains = []
    for line in stdout.splitlines()[2:]:
        parts = line.split()
        if len(parts) >= 3:
            domains.append(
                {
                    "connection": connection,
                    "id": parts[0],
                    "name": parts[1],
                    "state": " ".join(parts[2:]),
                }
            )
    return domains


def vm_status() -> dict[str, object]:
    connections = []
    domains = []
    for name, uri in {
        "system": "qemu:///system",
        "session": "qemu:///session",
    }.items():
        result = _run(["virsh", "-c", uri, "--readonly", "list", "--all"])
        entry = {
            "name": name,
            "uri": uri,
            "available": result["rc"] == 0,
            "raw": result["stdout"] if result["rc"] == 0 else result["stderr"],
            "return_code": result["rc"],
            "domains": [],
        }
        if result["rc"] == 0:
            entry["domains"] = _parse_virsh_domains(str(result["stdout"]), name)
            domains.extend(entry["domains"])
        connections.append(entry)
    return {
        "available": any(item["available"] for item in connections),
        "blocked": [item for item in connections if not item["available"]],
        "connections": connections,
        "domains": domains,
        "raw": "\n".join(str(item["raw"]) for item in connections if item["raw"]),
        "infra": ctos_infra_status(),
        "kali": kali_status(),
    }


def kali_status() -> dict[str, object]:
    state_result = _virsh(["domstate", KALI_DOMAIN, "--reason"], timeout=2.0)
    if state_result["rc"] != 0:
        return {
            "available": False,
            "name": KALI_DOMAIN,
            "state": "unknown",
            "state_raw": "",
            "error": state_result["stderr"] or state_result["stdout"] or "domstate failed",
        }

    state_raw = str(state_result["stdout"])
    state = _domain_state_label(state_raw)
    blk = _virsh(["domblklist", KALI_DOMAIN, "--details"], timeout=2.0)
    snapshot_tree = _virsh(["snapshot-list", KALI_DOMAIN, "--tree"], timeout=2.0)
    snapshot_names = _virsh(["snapshot-list", KALI_DOMAIN, "--name"], timeout=2.0)

    active_disk = _parse_active_disk(str(blk["stdout"])) if blk["rc"] == 0 else ""
    current_snapshot = _snapshot_from_overlay(active_disk)
    disk_role = "baseline" if active_disk == KALI_DISK else "overlay" if current_snapshot else "unknown"
    names = [
        line.strip()
        for line in str(snapshot_names["stdout"]).splitlines()
        if line.strip() and not line.strip().startswith("-")
    ] if snapshot_names["rc"] == 0 else []

    return {
        "available": True,
        "name": KALI_DOMAIN,
        "state": state,
        "state_raw": state_raw,
        "active_disk": active_disk,
        "disk_role": disk_role,
        "current_snapshot": current_snapshot,
        "snapshots": names,
        "snapshot_tree": str(snapshot_tree["stdout"]) if snapshot_tree["rc"] == 0 else "",
        "snapshot_error": snapshot_tree["stderr"] if snapshot_tree["rc"] != 0 else "",
        "health": kali_guest_health(state),
    }


def kali_guest_health(state: str) -> dict[str, object]:
    if state != "running":
        return {
            "checked": False,
            "agent": "offline",
            "internet": "not_checked",
            "dns": "not_checked",
            "voice": "not_checked",
            "summary": "guest not running",
            "errors": [],
        }

    now = time.time()
    if (
        _KALI_HEALTH_CACHE["state"] == state
        and now - float(_KALI_HEALTH_CACHE["time"]) < 15
        and _KALI_HEALTH_CACHE["data"]
    ):
        return dict(_KALI_HEALTH_CACHE["data"])

    health: dict[str, object] = {
        "checked": True,
        "checked_at": int(now),
        "agent": "unknown",
        "internet": "unknown",
        "dns": "unknown",
        "voice": "unknown",
        "summary": "checking",
        "errors": [],
    }
    errors: list[str] = []

    if not KALI_AGENT.exists():
        health.update({"agent": "missing", "summary": "guest-agent helper missing"})
        _KALI_HEALTH_CACHE.update({"time": now, "state": state, "data": health})
        return health

    agent = _run([str(KALI_AGENT), "ping"], timeout=2.0)
    if agent["rc"] != 0:
        errors.append(str(agent["stderr"] or agent["stdout"] or "guest-agent ping failed"))
        health.update({"agent": "blocked", "summary": "guest-agent blocked", "errors": errors})
        _KALI_HEALTH_CACHE.update({"time": now, "state": state, "data": health})
        return health
    health["agent"] = "ok"

    internet = _run([str(KALI_AGENT), "run", "/usr/bin/ping", "-c", "1", "-W", "1", "1.1.1.1"], timeout=3.0)
    health["internet"] = "ok" if internet["rc"] == 0 and "0% packet loss" in str(internet["stdout"]) else "bad"
    if health["internet"] != "ok":
        errors.append(str(internet["stderr"] or internet["stdout"] or "internet check failed"))

    dns = _run([str(KALI_AGENT), "run", "/usr/bin/getent", "hosts", "deb.debian.org"], timeout=3.0)
    health["dns"] = "ok" if dns["rc"] == 0 and str(dns["stdout"]).strip() else "bad"
    if health["dns"] != "ok":
        errors.append(str(dns["stderr"] or dns["stdout"] or "DNS check failed"))

    voice_command = (
        "ps -eo stat=,comm= | awk '$1 !~ /^Z/ && "
        "($2==\"orca\" || $2==\"speech-dispatcher\" || $2==\"sd_espeak-ng\" || $2==\"sd_dummy\") {print}'"
    )
    voice = _run([str(KALI_AGENT), "run", "/bin/sh", "-lc", voice_command], timeout=3.0)
    health["voice"] = "quiet" if voice["rc"] == 0 and not str(voice["stdout"]).strip() else "active"
    if health["voice"] != "quiet":
        errors.append(str(voice["stderr"] or voice["stdout"] or "voice process check failed"))

    health["errors"] = errors
    health["summary"] = "healthy" if not errors else "attention"
    _KALI_HEALTH_CACHE.update({"time": now, "state": state, "data": health})
    return health


def ctos_infra_status() -> dict[str, object]:
    script = ROOT / "scripts" / "ctos-libvirt-infra"
    if not script.exists():
        return {"available": False, "ok": False, "error": "ctos-libvirt-infra not found"}
    result = _run([str(script), "--json", "status"], timeout=3.0)
    if result["rc"] != 0:
        return {
            "available": False,
            "ok": False,
            "error": result["stderr"] or result["stdout"] or "ctos infra status failed",
        }
    try:
        data = json.loads(str(result["stdout"]))
    except json.JSONDecodeError as error:
        return {"available": False, "ok": False, "error": f"invalid ctos infra JSON: {error}"}
    data["available"] = True
    return data


def core_status() -> dict[str, object]:
    now = time.time()
    if _CORE_CACHE["data"] and now - float(_CORE_CACHE["time"]) < 20:
        return dict(_CORE_CACHE["data"])

    if not CORE_SCRIPT.exists():
        data = {"available": False, "error": "ctos-core helper not found"}
        _CORE_CACHE.update({"time": now, "data": data})
        return data

    result = _run([str(CORE_SCRIPT), "status", "--json"], timeout=8.0)
    try:
        data = json.loads(str(result["stdout"]))
    except json.JSONDecodeError as error:
        data = {
            "available": False,
            "error": result["stderr"] or result["stdout"] or f"invalid ctos-core JSON: {error}",
        }

    if result["rc"] != 0 and isinstance(data, dict):
        data.setdefault("available", False)
        data.setdefault("error", result["stderr"] or "ctos-core status failed")

    _CORE_CACHE.update({"time": now, "data": data})
    return dict(data)


def fleet_status() -> dict[str, object]:
    now = time.time()
    if _FLEET_CACHE["data"] and now - float(_FLEET_CACHE["time"]) < 30:
        return dict(_FLEET_CACHE["data"])

    if not FLEET_SCRIPT.exists():
        data = {"available": False, "error": "ctos-fleet helper not found", "nodes": [], "features": []}
        _FLEET_CACHE.update({"time": now, "data": data})
        return data

    result = _run([str(FLEET_SCRIPT), "status", "--json"], timeout=12.0)
    try:
        data = json.loads(str(result["stdout"]))
    except json.JSONDecodeError as error:
        data = {
            "available": False,
            "error": result["stderr"] or result["stdout"] or f"invalid ctos-fleet JSON: {error}",
            "nodes": [],
            "features": [],
        }

    if result["rc"] != 0 and isinstance(data, dict):
        data.setdefault("available", False)
        data.setdefault("error", result["stderr"] or "ctos-fleet status failed")
    else:
        data["available"] = True

    _FLEET_CACHE.update({"time": now, "data": data})
    return dict(data)


def approval_status(approval_db: Path) -> dict[str, object]:
    approvals: dict[str, object] = {
        "db_path": str(approval_db),
        "db_exists": approval_db.is_file(),
        "counts": {"pending": 0, "rejected": 0, "executed": 0, "failed": 0, "total": 0},
        "pending": [],
        "error": "",
    }
    if not approval_db.is_file():
        return approvals

    try:
        uri = f"{approval_db.resolve().as_uri()}?mode=ro"
        with sqlite3.connect(uri, uri=True, timeout=0.5) as conn:
            conn.row_factory = sqlite3.Row
            for status, count in conn.execute("SELECT status, COUNT(*) FROM approvals GROUP BY status"):
                count_int = int(count)
                approvals["counts"][str(status)] = count_int
                approvals["counts"]["total"] += count_int
            rows = conn.execute(
                """
                SELECT id, action, title, tier, target, risk, rollback, note, created_at
                FROM approvals
                WHERE status = 'pending'
                ORDER BY id DESC
                LIMIT 5
                """
            ).fetchall()
            approvals["pending"] = [{key: row[key] for key in row.keys()} for row in rows]
    except (OSError, sqlite3.Error) as error:
        approvals["error"] = str(error)
    return approvals


def runtime_profiles_status() -> dict[str, object]:
    status: dict[str, object] = {
        "path": str(RUNTIME_PROFILES),
        "available": RUNTIME_PROFILES.is_file(),
        "schema_version": None,
        "updated": "",
        "active_profile": None,
        "count": 0,
        "profiles": [],
        "first_local_probe": None,
        "first_external_probe": None,
        "adapter_contract": {
            "command": "ctos-ai runtime-check <id>",
            "network_default": False,
            "model_contact_default": False,
            "target_probe_optional": True,
        },
        "error": "",
    }
    if not RUNTIME_PROFILES.is_file():
        return status

    try:
        data = json.loads(RUNTIME_PROFILES.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("runtime profile file must contain an object")
        profiles = data.get("profiles", [])
        if not isinstance(profiles, list):
            raise ValueError("runtime profile file must contain a profiles list")
        summaries = []
        for profile in profiles:
            if not isinstance(profile, dict):
                continue
            summary = {
                "id": profile.get("id"),
                "label": profile.get("label"),
                "kind": profile.get("kind"),
                "target_node": profile.get("target_node"),
                "status": profile.get("status"),
                "readiness": profile.get("readiness"),
                "next_probe": profile.get("next_probe"),
            }
            summaries.append(summary)
            if profile.get("id") == "ollama-core-local":
                status["first_local_probe"] = summary
            if profile.get("id") == "openai-responses-api":
                status["first_external_probe"] = summary
        status.update(
            {
                "schema_version": data.get("schema_version"),
                "updated": data.get("updated", ""),
                "active_profile": data.get("active_profile"),
                "count": len(summaries),
                "profiles": summaries,
            }
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        status["error"] = str(error)
    return status


def ai_status() -> dict[str, object]:
    ollama = shutil.which("ollama")
    pgrep = _run(["pgrep", "-x", "ollama"], timeout=0.5)
    ai_home = Path(os.environ.get("CTOS_AI_HOME", str(Path.home() / ".local/share/ctos-ai"))).expanduser()
    agenda_db = Path(os.environ.get("CTOS_AI_DB", str(ai_home / "agenda.sqlite3"))).expanduser()
    approval_db = Path(os.environ.get("CTOS_AI_APPROVAL_DB", str(ai_home / "approvals.sqlite3"))).expanduser()
    probe_path = ai_home if ai_home.exists() else ai_home.parent
    agenda = {
        "state_root": str(ai_home),
        "db_path": str(agenda_db),
        "db_exists": agenda_db.is_file(),
        "state_root_writable": os.access(probe_path, os.W_OK),
        "counts": {"open": 0, "done": 0, "blocked": 0, "dropped": 0, "total": 0, "due_today": 0},
        "error": "",
    }

    if agenda_db.is_file():
        try:
            uri = f"{agenda_db.resolve().as_uri()}?mode=ro"
            with sqlite3.connect(uri, uri=True, timeout=0.5) as conn:
                for status, count in conn.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status"):
                    agenda["counts"][str(status)] = int(count)
                    agenda["counts"]["total"] += int(count)
                due_today = conn.execute(
                    "SELECT COUNT(*) FROM tasks WHERE status = 'open' AND due_date <= ?",
                    (date.today().isoformat(),),
                ).fetchone()
                agenda["counts"]["due_today"] = int(due_today[0]) if due_today else 0
        except (OSError, sqlite3.Error) as error:
            agenda["error"] = str(error)

    tools = {
        "ctos_ai": {"path": str(AI_SCRIPT), "available": AI_SCRIPT.is_file() and os.access(AI_SCRIPT, os.X_OK)},
        "ctos_agenda": {
            "path": str(AGENDA_SCRIPT),
            "available": AGENDA_SCRIPT.is_file() and os.access(AGENDA_SCRIPT, os.X_OK),
        },
    }
    runtimes = runtime_profiles_status()
    active_profile = runtimes.get("active_profile")

    return {
        "model_runtime": {
            "configured": bool(active_profile),
            "active": False,
            "profile": active_profile,
            "note": "runtime profiles registered; no model backend active yet",
        },
        "runtime_profiles": runtimes,
        "ollama_installed": bool(ollama),
        "ollama_running": pgrep["rc"] == 0,
        "tools": tools,
        "agenda": agenda,
        "approvals": approval_status(approval_db),
        "permissions": {
            "tier_0": ["status", "search-context"],
            "tier_1": ["agenda", "plan-day", "open-desk", "open-vms"],
            "tier_2": "approval queue required before mutable CTOS actions",
        },
        "workers": [],
    }


def services_status() -> list[dict[str, object]]:
    services = [
        "NetworkManager.service",
        "nftables.service",
        "firewalld.service",
        "libvirtd.service",
        "proton.VPN.service",
        "sshd.service",
    ]
    entries = []
    for service in services:
        active = _run(["systemctl", "is-active", service], timeout=0.8)
        enabled = _run(["systemctl", "is-enabled", service], timeout=0.8)
        entries.append(
            {
                "name": service.replace(".service", ""),
                "active": active["stdout"] if active["rc"] == 0 else "unknown",
                "enabled": enabled["stdout"] if enabled["rc"] == 0 else "unknown",
                "active_error": active["stderr"],
                "enabled_error": enabled["stderr"],
            }
        )
    return entries


def snapshot() -> dict[str, object]:
    return {
        "time": int(time.time()),
        "host": host_status(),
        "battery": battery_status(),
        "network": network_status(),
        "audio": audio_status(),
        "vms": vm_status(),
        "core": core_status(),
        "fleet": fleet_status(),
        "ai": ai_status(),
        "services": services_status(),
        "modes": {
            "active": "CTRL",
            "planned": [
                {"name": "KALI", "state": "planned", "ram": "6 GiB target"},
                {"name": "DEV-VM", "state": "planned", "ram": "6 GiB target"},
                {"name": "AI", "state": "planned", "ram": "mode budget"},
                {"name": "GAME", "state": "planned", "ram": "host performance"},
            ],
        },
    }
