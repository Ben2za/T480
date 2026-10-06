#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ai.ctos_prompt import compose_system_prompt, enforce_identity_contract  # noqa: E402


DEFAULT_MODEL = os.environ.get("CTOS_AI_MODEL", "qwen2.5-coder:0.5b")
DEFAULT_OLLAMA_URL = os.environ.get("CTOS_AI_OLLAMA_URL", "http://127.0.0.1:11435")
DEFAULT_API_HOST = os.environ.get("CTOS_AI_API_HOST", "127.0.0.1")
DEFAULT_API_PORT = int(os.environ.get("CTOS_AI_API_PORT", "8767"))


class ApiError(RuntimeError):
    def __init__(self, message: str, status: int = 500):
        super().__init__(message)
        self.status = status


def json_request(method: str, url: str, payload: dict[str, Any] | None = None, timeout: float = 30.0) -> dict[str, Any]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            text = response.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as error:
        raise ApiError(f"Ollama API unavailable at {url}: {error}", status=503) from error
    try:
        data = json.loads(text or "{}")
    except json.JSONDecodeError as error:
        raise ApiError(f"Ollama API returned invalid JSON: {error}", status=502) from error
    if not isinstance(data, dict):
        raise ApiError("Ollama API returned a non-object JSON payload", status=502)
    return data


def tokens_per_second(payload: dict[str, Any]) -> float:
    eval_count = int(payload.get("eval_count") or 0)
    eval_duration = int(payload.get("eval_duration") or 0)
    if not eval_count or not eval_duration:
        return 0.0
    return round(eval_count / (eval_duration / 1_000_000_000), 2)


def generate(
    prompt: str,
    model: str = DEFAULT_MODEL,
    system: str = "",
    raw_model: bool = False,
    temperature: float = 0.0,
    max_tokens: int = 256,
    timeout: float = 180.0,
    ollama_url: str = DEFAULT_OLLAMA_URL,
) -> dict[str, Any]:
    prompt = prompt.strip()
    if not prompt:
        raise ApiError("prompt is required", status=400)
    if max_tokens < 1 or max_tokens > 2048:
        raise ApiError("max_tokens must be between 1 and 2048", status=400)

    system_prompt = compose_system_prompt(system, raw_model=raw_model)
    full_prompt = prompt
    if system_prompt:
        full_prompt = f"System:\n{system_prompt}\n\nUser:\n{prompt}"

    started = time.monotonic()
    payload = json_request(
        "POST",
        f"{ollama_url.rstrip('/')}/api/generate",
        {
            "model": model,
            "prompt": full_prompt,
            "stream": False,
            "keep_alive": "5m",
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        },
        timeout=timeout,
    )
    elapsed_ms = round((time.monotonic() - started) * 1000)
    response, identity_guarded = enforce_identity_contract(str(payload.get("response") or ""), raw_model=raw_model)
    return {
        "ok": True,
        "model": model,
        "response": response,
        "identity_guarded": identity_guarded,
        "elapsed_ms": elapsed_ms,
        "tokens_per_second": tokens_per_second(payload),
        "ollama": {
            "done": payload.get("done"),
            "total_duration": payload.get("total_duration"),
            "load_duration": payload.get("load_duration"),
            "prompt_eval_count": payload.get("prompt_eval_count"),
            "prompt_eval_duration": payload.get("prompt_eval_duration"),
            "eval_count": payload.get("eval_count"),
            "eval_duration": payload.get("eval_duration"),
        },
    }


def normalize_messages(messages: object) -> list[dict[str, str]]:
    if not isinstance(messages, list):
        raise ApiError("messages must be a list", status=400)
    normalized: list[dict[str, str]] = []
    for item in messages:
        if not isinstance(item, dict):
            raise ApiError("each message must be an object", status=400)
        role = str(item.get("role") or "").strip().lower()
        content = str(item.get("content") or "").strip()
        if role not in {"system", "user", "assistant"}:
            raise ApiError("message role must be system, user, or assistant", status=400)
        if not content:
            continue
        normalized.append({"role": role, "content": content})
    if not any(item["role"] == "user" for item in normalized):
        raise ApiError("at least one user message is required", status=400)
    return normalized


def chat_prompt(messages: list[dict[str, str]], max_turns: int = 8) -> tuple[str, str]:
    system_parts = [item["content"] for item in messages if item["role"] == "system"]
    dialog = [item for item in messages if item["role"] in {"user", "assistant"}]
    if max_turns > 0:
        dialog = dialog[-max_turns * 2 :]
    lines = [
        "Conversation CTOS locale. Reponds au dernier message utilisateur.",
        "Garde les reponses courtes, pratiques et en francais sauf demande contraire.",
        "",
    ]
    for item in dialog:
        label = "Utilisateur" if item["role"] == "user" else "CTOS"
        lines.append(f"{label}: {item['content']}")
    lines.append("CTOS:")
    return "\n".join(lines), "\n\n".join(system_parts)


def generate_chat(
    messages: object,
    model: str = DEFAULT_MODEL,
    system: str = "",
    raw_model: bool = False,
    temperature: float = 0.2,
    max_tokens: int = 256,
    timeout: float = 180.0,
    ollama_url: str = DEFAULT_OLLAMA_URL,
    max_turns: int = 8,
) -> dict[str, Any]:
    normalized = normalize_messages(messages)
    prompt, embedded_system = chat_prompt(normalized, max_turns=max_turns)
    system_prompt = "\n\n".join(part for part in [embedded_system, system] if part.strip())
    result = generate(
        prompt=prompt,
        model=model,
        system=system_prompt,
        raw_model=raw_model,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
        ollama_url=ollama_url,
    )
    return {
        **result,
        "messages": [*normalized, {"role": "assistant", "content": result["response"]}],
        "history_turns_used": max_turns,
    }


def health(ollama_url: str = DEFAULT_OLLAMA_URL) -> dict[str, Any]:
    version = json_request("GET", f"{ollama_url.rstrip('/')}/api/version", timeout=3)
    tags = json_request("GET", f"{ollama_url.rstrip('/')}/api/tags", timeout=5)
    models = tags.get("models", [])
    if not isinstance(models, list):
        models = []
    return {
        "ok": True,
        "ollama_url": ollama_url,
        "version": version.get("version"),
        "models": [
            {
                "name": item.get("name"),
                "size": item.get("size"),
                "details": item.get("details"),
            }
            for item in models
            if isinstance(item, dict)
        ],
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "ctos-ai-api/0.1"

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"{self.address_string()} - {fmt % args}", file=sys.stderr)

    def write_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length") or "0")
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as error:
            raise ApiError(f"invalid JSON body: {error}", status=400) from error
        if not isinstance(payload, dict):
            raise ApiError("JSON body must be an object", status=400)
        return payload

    def do_GET(self) -> None:  # noqa: N802
        try:
            if self.path in {"/", "/health"}:
                self.write_json(200, health())
                return
            self.write_json(404, {"ok": False, "error": "not found"})
        except ApiError as error:
            self.write_json(error.status, {"ok": False, "error": str(error)})

    def do_POST(self) -> None:  # noqa: N802
        try:
            if self.path not in {"/ask", "/chat"}:
                self.write_json(404, {"ok": False, "error": "not found"})
                return
            payload = self.read_json()
            if self.path == "/ask":
                result = generate(
                    prompt=str(payload.get("prompt") or ""),
                    model=str(payload.get("model") or DEFAULT_MODEL),
                    system=str(payload.get("system") or ""),
                    raw_model=bool(payload.get("raw_model", False)),
                    temperature=float(payload.get("temperature", 0.0)),
                    max_tokens=int(payload.get("max_tokens", 256)),
                    timeout=float(payload.get("timeout", 180.0)),
                )
            else:
                result = generate_chat(
                    messages=payload.get("messages"),
                    model=str(payload.get("model") or DEFAULT_MODEL),
                    system=str(payload.get("system") or ""),
                    raw_model=bool(payload.get("raw_model", False)),
                    temperature=float(payload.get("temperature", 0.2)),
                    max_tokens=int(payload.get("max_tokens", 256)),
                    timeout=float(payload.get("timeout", 180.0)),
                    max_turns=int(payload.get("max_turns", 8)),
                )
            self.write_json(200, result)
        except (TypeError, ValueError) as error:
            self.write_json(400, {"ok": False, "error": str(error)})
        except ApiError as error:
            self.write_json(error.status, {"ok": False, "error": str(error)})


def cmd_health(args: argparse.Namespace) -> int:
    try:
        payload = health(args.ollama_url)
    except ApiError as error:
        print(str(error), file=sys.stderr)
        return 1
    print(json.dumps(payload, ensure_ascii=False, indent=2) if args.json else f"ok ollama={payload['version']} models={len(payload['models'])}")
    return 0


def cmd_ask(args: argparse.Namespace) -> int:
    prompt = " ".join(args.prompt).strip()
    if prompt == "-":
        prompt = sys.stdin.read().strip()
    try:
        payload = generate(
            prompt=prompt,
            model=args.model,
            system=args.system,
            raw_model=args.raw_model,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            timeout=args.timeout,
            ollama_url=args.ollama_url,
        )
    except ApiError as error:
        print(str(error), file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(payload["response"])
        if args.stats:
            print()
            print(f"model              {payload['model']}")
            print(f"elapsed_ms         {payload['elapsed_ms']}")
            print(f"tokens_per_second  {payload['tokens_per_second']}")
    return 0


def cmd_chat(args: argparse.Namespace) -> int:
    prompt = " ".join(args.prompt).strip()
    if prompt == "-":
        prompt = sys.stdin.read().strip()
    messages = [{"role": "user", "content": prompt}]
    try:
        payload = generate_chat(
            messages=messages,
            model=args.model,
            system=args.system,
            raw_model=args.raw_model,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            timeout=args.timeout,
            ollama_url=args.ollama_url,
            max_turns=args.max_turns,
        )
    except ApiError as error:
        print(str(error), file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(payload["response"])
        if args.stats:
            print()
            print(f"model              {payload['model']}")
            print(f"elapsed_ms         {payload['elapsed_ms']}")
            print(f"tokens_per_second  {payload['tokens_per_second']}")
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"ctos-ai-api listening on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        server.server_close()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CTOS local AI HTTP API over a localhost Ollama tunnel")
    sub = parser.add_subparsers(dest="command", required=True)

    common_parent = argparse.ArgumentParser(add_help=False)
    common_parent.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL)

    health_parser = sub.add_parser("health", parents=[common_parent], help="check the local Ollama tunnel")
    health_parser.add_argument("--json", action="store_true")
    health_parser.set_defaults(func=cmd_health)

    ask_parser = sub.add_parser("ask", parents=[common_parent], help="ask CTOS Local through the fast localhost tunnel")
    ask_parser.add_argument("prompt", nargs="+", help="prompt text, or '-' to read stdin")
    ask_parser.add_argument("--model", default=DEFAULT_MODEL)
    ask_parser.add_argument("--system", default="")
    ask_parser.add_argument("--raw-model", action="store_true")
    ask_parser.add_argument("--temperature", type=float, default=0.0)
    ask_parser.add_argument("--max-tokens", type=int, default=256)
    ask_parser.add_argument("--timeout", type=float, default=180.0)
    ask_parser.add_argument("--stats", action="store_true")
    ask_parser.add_argument("--json", action="store_true")
    ask_parser.set_defaults(func=cmd_ask)

    chat_parser = sub.add_parser("chat", parents=[common_parent], help="single-turn chat call using the /chat message format")
    chat_parser.add_argument("prompt", nargs="+", help="prompt text, or '-' to read stdin")
    chat_parser.add_argument("--model", default=DEFAULT_MODEL)
    chat_parser.add_argument("--system", default="")
    chat_parser.add_argument("--raw-model", action="store_true")
    chat_parser.add_argument("--temperature", type=float, default=0.2)
    chat_parser.add_argument("--max-tokens", type=int, default=256)
    chat_parser.add_argument("--timeout", type=float, default=180.0)
    chat_parser.add_argument("--max-turns", type=int, default=8)
    chat_parser.add_argument("--stats", action="store_true")
    chat_parser.add_argument("--json", action="store_true")
    chat_parser.set_defaults(func=cmd_chat)

    serve_parser = sub.add_parser("serve", help="serve GET /health plus POST /ask and /chat on localhost")
    serve_parser.add_argument("--host", default=DEFAULT_API_HOST)
    serve_parser.add_argument("--port", type=int, default=DEFAULT_API_PORT)
    serve_parser.set_defaults(func=cmd_serve)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
