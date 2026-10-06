#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import signal
import shutil
import sys
import time

try:
    from .status import snapshot
except ImportError:
    from status import snapshot


WIDTH = 78
TWO_COLUMN_MIN_WIDTH = 132
COLUMN_GAP = "  |  "
GLOBE = ["(-)", "(\\)", "(|)", "(/)"]
ENTER_ALT_SCREEN = "\033[?1049h"
EXIT_ALT_SCREEN = "\033[?1049l"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
CLEAR_SCREEN = "\033[2J\033[H"


def bar(percent: float, width: int = 22) -> str:
    filled = int((max(0, min(100, percent)) / 100) * width)
    return "[" + "#" * filled + "." * (width - filled) + f"] {percent:5.1f}%"


def uptime_text(seconds: int) -> str:
    minutes, _ = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    if days:
        return f"{days}d {hours}h {minutes}m"
    return f"{hours}h {minutes}m"


def line(text: str = "", width: int = WIDTH) -> str:
    clean = str(text).replace("\r", " ").replace("\n", " ").replace("\t", " ")
    return clean[:width].ljust(width)


def fit_rows(rows: list[str], height: int, width: int = WIDTH) -> list[str]:
    usable_height = max(8, height)
    if len(rows) <= usable_height:
        return rows
    hidden = len(rows) - usable_height + 1
    return rows[: usable_height - 1] + [line(f"... {hidden} more lines; open http://127.0.0.1:8765 for full cockpit", width)]


def combine_columns(left: list[str], right: list[str], width: int) -> list[str]:
    col_width = max(40, min(WIDTH, (width - len(COLUMN_GAP)) // 2))
    rows: list[str] = []
    for idx in range(max(len(left), len(right))):
        left_text = left[idx] if idx < len(left) else ""
        right_text = right[idx] if idx < len(right) else ""
        rows.append(line(left_text, col_width) + COLUMN_GAP + line(right_text, col_width))
    return rows


def compact_path(path: str) -> str:
    marker = "/var/lib/libvirt/ctos/"
    if path.startswith(marker):
        return path.replace(marker, "", 1)
    return path or "unknown"


def render_kali(rows: list[str], kali: dict[str, object]) -> None:
    rows.append(line())
    rows.append(line("KALI CONTROL"))
    if not kali or not kali.get("available"):
        rows.append(line(f"  ctos-kali unavailable: {kali.get('error', 'unknown') if kali else 'missing'}"))
        return

    health = kali.get("health", {})
    if not isinstance(health, dict):
        health = {}
    snapshot_name = str(kali.get("current_snapshot") or "none")
    active_disk = compact_path(str(kali.get("active_disk") or ""))
    snapshot_tree = " -> ".join(
        part.strip(" +-|\t")
        for part in str(kali.get("snapshot_tree") or "").splitlines()
        if part.strip(" +-|\t")
    )
    if not snapshot_tree:
        snapshot_tree = snapshot_name

    rows.append(line(f"  STATE    {kali.get('state_raw') or kali.get('state')}"))
    rows.append(line(f"  SNAP     {snapshot_name}"))
    rows.append(line(f"  CHAIN    {snapshot_tree}"))
    rows.append(line(f"  DISK     {kali.get('disk_role', 'unknown')}  {active_disk}"))
    rows.append(
        line(
            "  HEALTH   "
            f"agent {health.get('agent', '--')}  "
            f"net {health.get('internet', '--')}  "
            f"dns {health.get('dns', '--')}  "
            f"voice {health.get('voice', '--')}"
        )
    )
    rows.append(line(f"  SUMMARY  {health.get('summary', 'unknown')}"))
    rows.append(line("  ACTIONS  web buttons: Start / Shutdown / Console / Checkpoint"))
    rows.append(line("           ./scripts/ctos-control open  or  http://127.0.0.1:8765"))


def render_core(rows: list[str], core: dict[str, object]) -> None:
    rows.append(line())
    rows.append(line("CTOS CORE"))
    if not core or not core.get("available"):
        rows.append(line(f"  ctos-core unavailable: {core.get('error', 'unknown') if core else 'missing'}"))
        rows.append(line("  helper: ./scripts/ctos-core status"))
        return

    role = core.get("role", {})
    if not isinstance(role, dict):
        role = {}
    memory = core.get("memory", {})
    if not isinstance(memory, dict):
        memory = {}
    storage = core.get("storage", {})
    if not isinstance(storage, dict):
        storage = {}
    srv = storage.get("srv", {})
    if not isinstance(srv, dict):
        srv = {}
    layout = core.get("layout", {})
    if not isinstance(layout, dict):
        layout = {}
    network = core.get("network", {})
    if not isinstance(network, dict):
        network = {}
    checks = network.get("checks", [])
    if not isinstance(checks, list):
        checks = []
    service_text = " ".join(
        f"{item.get('name')}={item.get('active')}"
        for item in core.get("services", [])
        if isinstance(item, dict)
    )
    check_text = " ".join(
        f"{item.get('name')}={'ok' if item.get('ok') else 'bad'}"
        for item in checks
        if isinstance(item, dict)
    )

    rows.append(line(f"  HOST     {core.get('hostname')}  role {role.get('role', 'unknown')}"))
    rows.append(line(f"  KERNEL   {core.get('kernel')}  uptime {uptime_text(int(core.get('uptime_seconds', 0)))}"))
    rows.append(line(f"  RAM      {memory.get('used_text')} / {memory.get('total_text')} ({memory.get('used_percent')}%)"))
    rows.append(
        line(
            "  SRV      "
            f"{srv.get('source', '--')} {srv.get('fstype', '--')}  "
            f"free {srv.get('free_text', '--')}  writable {srv.get('writable')}"
        )
    )
    rows.append(line(f"  LAYOUT   complete {layout.get('complete')}  marker {layout.get('marker_exists')}"))
    rows.append(line(f"  NET      {check_text or 'not checked'}"))
    rows.append(line(f"  SERVICES {service_text[:68] or 'not checked'}"))
    rows.append(line(f"  SUDO     passwordless {'closed' if core.get('sudo_password_required') else 'present'}"))


def render_fleet(rows: list[str], fleet: dict[str, object]) -> None:
    rows.append(line())
    rows.append(line("FLEET"))
    if not fleet or not fleet.get("available", True):
        rows.append(line(f"  unavailable: {fleet.get('error', 'unknown') if fleet else 'missing'}"))
        return
    for node in (fleet.get("nodes", []) or [])[:6]:
        if not isinstance(node, dict):
            continue
        live = node.get("live", {})
        if not isinstance(live, dict):
            live = {}
        state = "online" if live.get("available") else node.get("status", "unknown")
        rows.append(line(f"  {node.get('id', '--'):<16} {node.get('role', '--'):<10} {state:<10} {node.get('os', '--')}"))


def render(frame: int, height: int | None = None, columns: int | None = None) -> str:
    data = snapshot()
    host = data["host"]
    mem = host["memory"]
    disk = host["disk"]
    battery = data["battery"]
    network = data["network"]
    audio = data.get("audio", {})
    vms = data["vms"]
    core = data.get("core", {})
    fleet = data.get("fleet", {})
    kali = vms.get("kali", {}) if isinstance(vms, dict) else {}
    ai = data["ai"]
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if height is None or columns is None:
        size = shutil.get_terminal_size((WIDTH, 40))
        height = height if height is not None else size.lines
        columns = columns if columns is not None else size.columns

    two_columns = columns >= TWO_COLUMN_MIN_WIDTH
    screen_width = min(columns, (WIDTH * 2) + len(COLUMN_GAP)) if two_columns else min(columns, WIDTH)

    left: list[str] = []
    right: list[str] = []

    left.append(line("SYSTEM"))
    left.append(line(f"  LOAD     {host['load'][0]:>4} {host['load'][1]:>4} {host['load'][2]:>4}"))
    if host["temps"]:
        temp_text = "  ".join(f"{item['name']} {item['celsius']}C" for item in host["temps"][:2])
        left.append(line(f"  TEMP     {temp_text}"))
    left.append(line(f"  RAM      {bar(mem['used_percent'])}  {mem['used_text']} / {mem['total_text']}"))
    if isinstance(audio, dict):
        left.append(line(f"  AUDIO    {audio.get('output', 'VOL unavailable')}  {audio.get('microphone', 'MIC unavailable')}"))
    left.append(line(f"  ROOT     {bar(disk['root_used_percent'])}  free {disk['root_free_text']}"))
    left.append(line(f"  HOME     {bar(disk['home_used_percent'])}  free {disk['home_free_text']}"))
    left.append(line())
    left.append(line("POWER / NETWORK"))
    if battery:
        for item in battery:
            left.append(line(f"  {item['name']:<8} {item['capacity']:>3}%  {item['status']}"))
    else:
        left.append(line("  battery not detected"))
    for item in network:
        left.append(line(f"  {item['name']:<8} {item['state']:<9} rx {item['rx_text']:<12} tx {item['tx_text']}"))
    render_core(left, core if isinstance(core, dict) else {})
    render_fleet(left, fleet if isinstance(fleet, dict) else {})

    right.append(line("VIRTUALIZATION"))
    if vms["available"]:
        for connection in vms.get("connections", []):
            state = "ready" if connection.get("available") else "blocked"
            right.append(line(f"  {connection['name']:<8} {state:<8} {connection['uri']}"))
            for domain in connection.get("domains", [])[:3]:
                right.append(line(f"    {domain['name']:<24} {domain['state']}"))
        if not vms["domains"]:
            right.append(line("  no domains defined"))
    else:
        reason = " ".join(str(vms["raw"] or "unknown").split())
        right.append(line(f"  virsh unavailable: {reason}"))
    render_kali(right, kali)
    right.append(line())
    right.append(line("CTOS AI"))
    agenda = ai.get("agenda", {}) if isinstance(ai, dict) else {}
    counts = agenda.get("counts", {}) if isinstance(agenda, dict) else {}
    tools = ai.get("tools", {}) if isinstance(ai, dict) else {}
    ctos_ai = tools.get("ctos_ai", {}) if isinstance(tools, dict) else {}
    ctos_agenda = tools.get("ctos_agenda", {}) if isinstance(tools, dict) else {}
    runtime = ai.get("model_runtime", {}) if isinstance(ai, dict) else {}
    runtime_profiles = ai.get("runtime_profiles", {}) if isinstance(ai, dict) else {}
    runtime_profile_rows = runtime_profiles.get("profiles", []) if isinstance(runtime_profiles, dict) else []
    approvals = ai.get("approvals", {}) if isinstance(ai, dict) else {}
    approval_counts = approvals.get("counts", {}) if isinstance(approvals, dict) else {}
    pending_approvals = approvals.get("pending", []) if isinstance(approvals, dict) else []
    right.append(line(f"  MODEL    configured {runtime.get('configured', False)}  active {runtime.get('active', False)}"))
    right.append(
        line(
            "  RUNTIME  "
            f"profiles {runtime_profiles.get('count', 0) if isinstance(runtime_profiles, dict) else 0}  "
            f"active {runtime_profiles.get('active_profile') or 'none' if isinstance(runtime_profiles, dict) else 'none'}"
        )
    )
    if isinstance(runtime_profile_rows, list):
        for profile in runtime_profile_rows[:2]:
            if not isinstance(profile, dict):
                continue
            right.append(line(f"           {profile.get('id')}  {profile.get('status')}"))
    if isinstance(runtime_profiles, dict) and runtime_profiles.get("error"):
        right.append(line(f"  RUN-ERR  {runtime_profiles.get('error')}"))
    if isinstance(runtime_profiles, dict):
        contract = runtime_profiles.get("adapter_contract", {})
        if isinstance(contract, dict):
            right.append(line(f"  CHECK    {contract.get('command', 'ctos-ai runtime-check <id>')}"))
    right.append(line(f"  TOOLS    ctos-ai {ctos_ai.get('available', False)}  agenda {ctos_agenda.get('available', False)}"))
    right.append(
        line(
            "  AGENDA   "
            f"db {agenda.get('db_exists', False)}  "
            f"open {counts.get('open', 0)}  "
            f"due {counts.get('due_today', 0)}  "
            f"done {counts.get('done', 0)}"
        )
    )
    if agenda.get("error"):
        right.append(line(f"  ERROR    {agenda.get('error')}"))
    right.append(
        line(
            "  APPROVE  "
            f"pending {approval_counts.get('pending', 0)}  "
            f"failed {approval_counts.get('failed', 0)}  "
            f"total {approval_counts.get('total', 0)}"
        )
    )
    if isinstance(pending_approvals, list):
        for approval in pending_approvals[:3]:
            if not isinstance(approval, dict):
                continue
            right.append(line(f"           #{approval.get('id')} T{approval.get('tier')} {approval.get('action')}"))
    if isinstance(approvals, dict) and approvals.get("error"):
        right.append(line(f"  APPR-ERR {approvals.get('error')}"))
    right.append(line(f"  OLLAMA   installed {ai['ollama_installed']}  running {ai['ollama_running']}"))
    right.append(line("  NEXT     runtime adapter dry-run; no model daemon yet"))
    right.append(line())
    right.append(line("SERVICES"))
    for service in data["services"][:4]:
        right.append(line(f"  {service['name']:<16} active {service['active']:<8} enabled {service['enabled']}"))
    right.append(line())
    right.append(line("GLOBAL FEEDS"))
    right.append(line(f"  {GLOBE[frame % len(GLOBE)]} local telemetry only for now; live feeds need a later data decision"))
    right.append(line())
    right.append(line("KEY MAP"))
    right.append(line("  SUPER+1 CTRL   SUPER+2 DESK   SUPER+4 VMS   SUPER+8 GAME"))
    right.append(line("  SUPER+A audio panel   SUPER+PgUp/PgDn volume   SUPER+Shift+A mixer"))
    right.append(line("  Ctrl+C exits this cockpit view; service/dashboard files live in ~/T480/control"))

    rows = [
        line("CTOS CONTROL // HOST COCKPIT".center(screen_width), screen_width),
        line("=" * screen_width, screen_width),
        line(f"TIME {now}   HOST {host['hostname']}   UPTIME {uptime_text(host['uptime_seconds'])}", screen_width),
        line("", screen_width),
    ]
    if two_columns:
        rows.extend(combine_columns(left, right, screen_width))
    else:
        rows.extend(line(item, screen_width) for item in [*left, line(), *right])
    return CLEAR_SCREEN + "\n".join(fit_rows(rows, height, screen_width))


def main() -> None:
    def restore_terminal(*_: object) -> None:
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, restore_terminal)
    signal.signal(signal.SIGHUP, restore_terminal)
    frame = 0
    sys.stdout.write(ENTER_ALT_SCREEN + HIDE_CURSOR + CLEAR_SCREEN)
    sys.stdout.flush()
    try:
        while True:
            size = shutil.get_terminal_size((WIDTH, 40))
            sys.stdout.write(render(frame, size.lines, size.columns))
            sys.stdout.flush()
            frame += 1
            time.sleep(2)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(SHOW_CURSOR + CLEAR_SCREEN + EXIT_ALT_SCREEN)
        sys.stdout.flush()


if __name__ == "__main__":
    main()
