#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from status import snapshot


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
STATIC = ROOT / "static"
KALI_DOMAIN = "ctos-kali"
KALI_SCRIPT = REPO_ROOT / "scripts" / "ctos-kali"
SNAPSHOT_LABEL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,80}$")


def run(args: list[str], timeout: float = 20.0) -> dict[str, object]:
    try:
        proc = subprocess.run(
            args,
            capture_output=True,
            check=False,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return {"ok": False, "rc": 127, "stdout": "", "stderr": f"{args[0]} not found"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "rc": 124, "stdout": "", "stderr": "timeout"}
    return {
        "ok": proc.returncode == 0,
        "rc": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def virsh(args: list[str], readonly: bool = False, timeout: float = 20.0) -> dict[str, object]:
    command = ["virsh", "-c", "qemu:///system"]
    if readonly:
        command.append("--readonly")
    command.extend(args)
    return run(command, timeout=timeout)


def kali_state() -> str:
    result = virsh(["domstate", KALI_DOMAIN], readonly=True, timeout=4.0)
    if not result["ok"]:
        raise RuntimeError(str(result["stderr"] or result["stdout"] or "domstate failed"))
    return str(result["stdout"]).strip().lower()


def action_start() -> dict[str, object]:
    state = kali_state()
    if state == "running":
        return {"ok": True, "message": f"{KALI_DOMAIN} already running"}
    if state not in {"shut off", "shutoff"}:
        raise RuntimeError(f"{KALI_DOMAIN} state is {state!r}; refusing start")
    result = virsh(["start", KALI_DOMAIN], timeout=20.0)
    if not result["ok"]:
        raise RuntimeError(str(result["stderr"] or result["stdout"] or "virsh start failed"))
    return {"ok": True, "message": result["stdout"] or f"{KALI_DOMAIN} started"}


def action_shutdown() -> dict[str, object]:
    state = kali_state()
    if state in {"shut off", "shutoff"}:
        return {"ok": True, "message": f"{KALI_DOMAIN} already shut off"}
    if state != "running":
        raise RuntimeError(f"{KALI_DOMAIN} state is {state!r}; refusing shutdown")
    result = virsh(["shutdown", KALI_DOMAIN, "--mode", "agent"], timeout=20.0)
    if not result["ok"]:
        raise RuntimeError(str(result["stderr"] or result["stdout"] or "virsh shutdown failed"))
    return {"ok": True, "message": result["stdout"] or f"{KALI_DOMAIN} shutdown requested"}


def action_console() -> dict[str, object]:
    virt_manager = shutil.which("virt-manager")
    hyprctl = shutil.which("hyprctl")
    if not virt_manager:
        raise RuntimeError("virt-manager not found")
    if not hyprctl:
        raise RuntimeError("hyprctl not found")
    result = run(
        [
            hyprctl,
            "dispatch",
            "exec",
            f"{virt_manager} -c qemu:///system --show-domain-console {KALI_DOMAIN}",
        ],
        timeout=8.0,
    )
    if not result["ok"]:
        raise RuntimeError(str(result["stderr"] or result["stdout"] or "console launch failed"))
    return {"ok": True, "message": f"console launch requested for {KALI_DOMAIN}"}


def action_checkpoint(label: str | None) -> dict[str, object]:
    state = kali_state()
    if state not in {"shut off", "shutoff"}:
        raise RuntimeError(f"{KALI_DOMAIN} must be shut off before checkpoint; current state is {state!r}")
    if not label:
        label = "cockpit-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    if not SNAPSHOT_LABEL_RE.match(label):
        raise RuntimeError("invalid checkpoint label")
    result = run(
        [
            str(KALI_SCRIPT),
            "snapshot-checkpoint",
            label,
            "--description",
            f"CTOS Kali cockpit checkpoint: {label}",
        ],
        timeout=180.0,
    )
    if not result["ok"]:
        raise RuntimeError(str(result["stderr"] or result["stdout"] or "checkpoint failed"))
    return {"ok": True, "message": result["stdout"], "label": label}


def run_vm_action(payload: dict[str, object]) -> dict[str, object]:
    domain = str(payload.get("domain", ""))
    action = str(payload.get("action", ""))
    if domain != KALI_DOMAIN:
        raise RuntimeError("only ctos-kali is exposed through cockpit actions")
    if action == "start":
        return action_start()
    if action == "shutdown":
        return action_shutdown()
    if action == "console":
        return action_console()
    if action == "checkpoint":
        label = payload.get("label")
        return action_checkpoint(str(label) if label else None)
    raise RuntimeError(f"unsupported action: {action}")


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/status":
            payload = json.dumps(snapshot()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if parsed.path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/vm/action":
            self.send_error(404)
            return
        if self.client_address[0] not in {"127.0.0.1", "::1"}:
            self.send_error(403)
            return

        length = int(self.headers.get("Content-Length", "0") or "0")
        if length > 4096:
            self.send_error(413)
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            result = run_vm_action(payload)
            self.send_json(200, result)
        except (json.JSONDecodeError, RuntimeError) as error:
            self.send_json(400, {"ok": False, "error": str(error)})

    def send_json(self, status: int, data: dict[str, object]) -> None:
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="CTOS local control dashboard")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"CTOS control dashboard: http://{args.host}:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
