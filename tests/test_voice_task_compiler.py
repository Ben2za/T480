from __future__ import annotations

import io
import json
import unittest
import urllib.error
from unittest import mock

from ai import voice_task_compiler as compiler


VALID_SPEC = {
    "schema_version": "ctos.voice_task.v1",
    "goal": "Summarize the current voice stack status.",
    "workspace": "/home/operator/T480",
    "allowed_scope": ["context", "scripts"],
    "constraints": ["Read-only; do not change files or external state."],
    "deliverable": "A concise status summary.",
    "acceptance_checks": ["Cite the inspected local files or commands."],
    "approval_class": "read_only",
    "clarification_state": "resolved",
}


class FakeResponse:
    def __init__(self, payload: object):
        self.body = io.BytesIO(json.dumps(payload).encode("utf-8"))

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self, size: int = -1) -> bytes:
        return self.body.read(size)


class VoiceTaskCompilerTests(unittest.TestCase):
    def test_rejects_empty_oversize_and_secret_input(self) -> None:
        with self.assertRaisesRegex(compiler.VoiceTaskCompilerError, "empty"):
            compiler.validate_transcript("   ")
        with self.assertRaisesRegex(compiler.VoiceTaskCompilerError, "bounded"):
            compiler.validate_transcript("x" * (compiler.MAX_TRANSCRIPT_CHARS + 1))
        with self.assertRaisesRegex(compiler.VoiceTaskCompilerError, "secret guard"):
            compiler.validate_transcript("api_key=abcdef1234567890")

    def test_requires_loopback_plain_http_endpoint(self) -> None:
        self.assertEqual(
            compiler.validate_local_ollama_url("http://127.0.0.1:11435/"),
            "http://127.0.0.1:11435",
        )
        for value in (
            "https://ollama.example.com",
            "http://10.42.0.2:11434",
            "http://user:pass@127.0.0.1:11435",
            "http://127.0.0.1:11435/api/generate",
        ):
            with self.subTest(value=value):
                with self.assertRaises(compiler.VoiceTaskCompilerError):
                    compiler.validate_local_ollama_url(value)

    def test_explicit_operator_path_is_a_deterministic_scope_ceiling(self) -> None:
        broad = {**VALID_SPEC, "allowed_scope": ["ai", "scripts"]}
        response = lambda *_args, **_kwargs: FakeResponse({"response": json.dumps(broad)})
        result = compiler.compile_transcript(
            "Inspecte uniquement ai/voice_task_spec.py sans rien modifier.",
            opener=response,
        )
        self.assertEqual(result["spec"]["allowed_scope"], ["ai/voice_task_spec.py"])
        self.assertTrue(result["scope_restricted_to_explicit_paths"])

    def test_structured_request_returns_only_validated_spec_metadata(self) -> None:
        captured: dict[str, object] = {}

        def opener(request: object, *, timeout: float) -> FakeResponse:
            captured["url"] = request.full_url  # type: ignore[attr-defined]
            captured["payload"] = json.loads(request.data.decode("utf-8"))  # type: ignore[attr-defined]
            captured["timeout"] = timeout
            return FakeResponse({"response": json.dumps(VALID_SPEC), "done": True})

        raw_sentinel = "Affiche le statut CTOS RAW-SENTINEL-73"
        result = compiler.compile_transcript(raw_sentinel, opener=opener)

        self.assertEqual(captured["url"], "http://127.0.0.1:11435/api/generate")
        payload = captured["payload"]
        self.assertEqual(payload["prompt"], raw_sentinel)  # type: ignore[index]
        self.assertFalse(payload["stream"])  # type: ignore[index]
        self.assertEqual(payload["options"]["temperature"], 0)  # type: ignore[index]
        self.assertIsInstance(payload["format"], dict)  # type: ignore[index]
        self.assertEqual(result["spec"], VALID_SPEC)
        self.assertNotIn("RAW-SENTINEL-73", json.dumps(result))
        self.assertNotIn("transcript", result)

    def test_rejects_malformed_or_invalid_compiler_output(self) -> None:
        malformed = lambda *_args, **_kwargs: FakeResponse({"response": "not json"})
        with self.assertRaisesRegex(compiler.VoiceTaskCompilerError, "malformed"):
            compiler.compile_transcript("résume le projet", opener=malformed)

        invalid = {**VALID_SPEC, "workspace": "/tmp/outside"}
        bad_spec = lambda *_args, **_kwargs: FakeResponse({"response": json.dumps(invalid)})
        with self.assertRaisesRegex(compiler.VoiceTaskCompilerError, "rejected"):
            compiler.compile_transcript("résume le projet", opener=bad_spec)

    def test_api_failure_does_not_echo_input(self) -> None:
        def failed(*_args: object, **_kwargs: object) -> object:
            raise urllib.error.URLError("offline")

        secret_free_sentinel = "PRIVATE-VOICE-SENTINEL-91"
        with self.assertRaises(compiler.VoiceTaskCompilerError) as raised:
            compiler.compile_transcript(secret_free_sentinel, opener=failed)
        self.assertNotIn(secret_free_sentinel, str(raised.exception))


if __name__ == "__main__":
    unittest.main()
