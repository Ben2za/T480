from __future__ import annotations

import io
import json
import unittest
from email.message import Message
from unittest import mock

from control import voice_console as console


VALID_SPEC = {
    "schema_version": "ctos.voice_task.v1",
    "goal": "Inspect the current voice stack status.",
    "workspace": "/home/operator/T480",
    "allowed_scope": ["context", "ai", "scripts"],
    "constraints": ["Read-only; do not change files or external state."],
    "deliverable": "A concise evidence-based status summary.",
    "acceptance_checks": ["Report the inspected local evidence."],
    "approval_class": "read_only",
    "clarification_state": "resolved",
}


class VoiceConsoleCodexTests(unittest.TestCase):
    def setUp(self) -> None:
        self.codex_run_patch = mock.patch.object(console, "CODEX_RUN_ENABLED", True)
        self.codex_run_patch.start()
        with console.CODEX_PREVIEW_LOCK:
            console.CODEX_PREVIEWS.clear()

    def tearDown(self) -> None:
        self.codex_run_patch.stop()

    def compiled(self) -> dict[str, object]:
        normalized = console.validate_spec(VALID_SPEC)
        return {
            "ok": True,
            "spec": normalized,
            "canonical": console.canonical_json(normalized),
            "digest": console.spec_digest(normalized),
            "model": "local-test-model",
            "elapsed_ms": 12,
        }

    def test_preview_returns_only_validated_spec_and_stores_digest_metadata(self) -> None:
        raw_sentinel = "RAW-VOICE-SENTINEL-411"
        with (
            mock.patch.object(console, "compile_transcript", return_value=self.compiled()) as compile_call,
            mock.patch.object(console.secrets, "token_urlsafe", return_value="A" * 32),
        ):
            preview = console.create_codex_preview(raw_sentinel)

        compile_call.assert_called_once_with(raw_sentinel)
        self.assertNotIn(raw_sentinel, json.dumps(preview))
        self.assertNotIn("transcript", preview)
        self.assertTrue(preview["runnable"])
        self.assertEqual(preview["preview_id"], "A" * 32)
        with console.CODEX_PREVIEW_LOCK:
            stored = console.CODEX_PREVIEWS["A" * 32]
        self.assertEqual(stored[0], preview["spec_sha256"])
        self.assertNotIn(raw_sentinel, repr(stored))
        self.assertNotIn(str(preview["canonical_spec"]), repr(stored))

    def test_legacy_codex_brief_is_fail_closed(self) -> None:
        with mock.patch.object(console, "run_capture") as run:
            result = console.ask_brain("raw sentinel", mode="codex", max_tokens=180)
        self.assertFalse(result["ok"])
        self.assertIn("validated preview", str(result["stderr"]))
        run.assert_not_called()

    def test_chat_empty_success_is_converted_to_visible_failure(self) -> None:
        with mock.patch.object(
            console,
            "run_capture",
            return_value={"ok": True, "rc": 0, "stdout": "  ", "stderr": ""},
        ):
            result = console.ask_brain("safe local question", mode="chat", max_tokens=32)
        self.assertFalse(result["ok"])
        self.assertEqual(result["rc"], 1)
        self.assertEqual(result["answer"], "")
        self.assertIn("empty response", str(result["stderr"]))

    def test_run_requires_exact_digest_confirmation_and_one_time_token(self) -> None:
        compiled = self.compiled()
        with (
            mock.patch.object(console, "compile_transcript", return_value=compiled),
            mock.patch.object(console.secrets, "token_urlsafe", return_value="B" * 32),
        ):
            preview = console.create_codex_preview("local input")

        with self.assertRaisesRegex(console.CodexPreviewError, "confirmation"):
            console.run_codex_preview(
                preview_id=str(preview["preview_id"]),
                supplied_digest=str(preview["spec_sha256"]),
                canonical=str(preview["canonical_spec"]),
                confirmed=False,
            )

        with mock.patch.object(
            console,
            "run_capture",
            return_value={"ok": True, "rc": 0, "stdout": '{"status":"complete"}', "stderr": ""},
        ) as run:
            result = console.run_codex_preview(
                preview_id=str(preview["preview_id"]),
                supplied_digest=str(preview["spec_sha256"]),
                canonical=str(preview["canonical_spec"]),
                confirmed=True,
            )

        self.assertTrue(result["ok"])
        run.assert_called_once_with(
            [str(console.ROOT / "scripts" / "ctos-codex-voice"), "run", "-", "--yes"],
            input_text=f"{preview['canonical_spec']}\n",
            timeout=620.0,
        )
        with self.assertRaisesRegex(console.CodexPreviewError, "consumed"):
            console.run_codex_preview(
                preview_id=str(preview["preview_id"]),
                supplied_digest=str(preview["spec_sha256"]),
                canonical=str(preview["canonical_spec"]),
                confirmed=True,
            )

    def test_live_run_gate_is_fail_closed_without_disclosure_approval(self) -> None:
        compiled = self.compiled()
        with (
            mock.patch.object(console, "CODEX_RUN_ENABLED", False),
            mock.patch.object(console, "compile_transcript", return_value=compiled),
            mock.patch.object(console.secrets, "token_urlsafe", return_value="F" * 32),
            mock.patch.object(console, "run_capture") as run,
        ):
            preview = console.create_codex_preview("local input")
            self.assertFalse(preview["runnable"])
            with self.assertRaisesRegex(console.CodexPreviewError, "external-disclosure"):
                console.run_codex_preview(
                    preview_id=str(preview["preview_id"]),
                    supplied_digest=str(preview["spec_sha256"]),
                    canonical=str(preview["canonical_spec"]),
                    confirmed=True,
                )
            run.assert_not_called()

    def test_tampered_spec_or_digest_never_starts_runner(self) -> None:
        compiled = self.compiled()
        with (
            mock.patch.object(console, "compile_transcript", return_value=compiled),
            mock.patch.object(console.secrets, "token_urlsafe", return_value="C" * 32),
        ):
            preview = console.create_codex_preview("local input")
        tampered = str(preview["canonical_spec"]).replace("concise", "expanded")
        with mock.patch.object(console, "run_capture") as run:
            with self.assertRaises(console.CodexPreviewError):
                console.run_codex_preview(
                    preview_id=str(preview["preview_id"]),
                    supplied_digest=str(preview["spec_sha256"]),
                    canonical=tampered,
                    confirmed=True,
                )
            run.assert_not_called()

    def test_operator_edited_spec_is_revalidated_and_gets_a_new_digest(self) -> None:
        edited = {**VALID_SPEC, "allowed_scope": ["ai/voice_task_spec.py"]}
        with mock.patch.object(console.secrets, "token_urlsafe", return_value="E" * 32):
            preview = console.review_edited_codex_spec(json.dumps(edited, indent=2))
        self.assertEqual(
            json.loads(str(preview["canonical_spec"]))["allowed_scope"],
            ["ai/voice_task_spec.py"],
        )
        self.assertEqual(
            preview["spec_sha256"],
            console.spec_digest(edited),
        )
        self.assertNotIn("compiler", preview)

    def test_duplicate_fields_in_edited_or_run_spec_are_rejected(self) -> None:
        duplicate = json.dumps(VALID_SPEC)[:-1] + ',"goal":"second"}'
        with self.assertRaises(console.CodexPreviewError):
            console.review_edited_codex_spec(duplicate)
        with self.assertRaises(console.CodexPreviewError):
            console.revalidate_canonical_spec(duplicate)

    def test_expired_preview_is_rejected_before_runner(self) -> None:
        compiled = self.compiled()
        with (
            mock.patch.object(console, "compile_transcript", return_value=compiled),
            mock.patch.object(console.secrets, "token_urlsafe", return_value="D" * 32),
        ):
            preview = console.create_codex_preview("local input")
        with console.CODEX_PREVIEW_LOCK:
            digest, _, expires_at = console.CODEX_PREVIEWS["D" * 32]
            console.CODEX_PREVIEWS["D" * 32] = (digest, 0.0, expires_at)
        with mock.patch.object(console, "run_capture") as run:
            with self.assertRaisesRegex(console.CodexPreviewError, "expired"):
                console.run_codex_preview(
                    preview_id=str(preview["preview_id"]),
                    supplied_digest=str(preview["spec_sha256"]),
                    canonical=str(preview["canonical_spec"]),
                    confirmed=True,
                )
            run.assert_not_called()

    def test_json_reader_requires_application_json(self) -> None:
        handler = object.__new__(console.VoiceConsoleHandler)
        handler.headers = Message()
        body = b'{"text":"safe"}'
        handler.headers["Content-Length"] = str(len(body))
        handler.headers["Content-Type"] = "text/plain"
        handler.rfile = io.BytesIO(body)
        with self.assertRaisesRegex(ValueError, "application/json"):
            handler.read_json()

        handler.headers.replace_header("Content-Type", "application/json; charset=utf-8")
        handler.rfile = io.BytesIO(body)
        self.assertEqual(handler.read_json(), {"text": "safe"})

    def test_all_responses_disable_browser_caching(self) -> None:
        handler = object.__new__(console.VoiceConsoleHandler)
        handler.send_header = mock.Mock()
        with mock.patch.object(console.SimpleHTTPRequestHandler, "end_headers") as parent:
            handler.end_headers()
        handler.send_header.assert_has_calls(
            [
                mock.call("Cache-Control", "no-store"),
                mock.call("Pragma", "no-cache"),
                mock.call("Expires", "0"),
            ]
        )
        parent.assert_called_once_with()

    def test_ui_assets_share_the_server_build_cachebuster(self) -> None:
        html = (console.STATIC / "voice.html").read_text(encoding="utf-8")
        javascript = (console.STATIC / "voice.js").read_text(encoding="utf-8")
        build = console.VOICE_CONSOLE_BUILD
        self.assertIn(f'/voice.css?v={build}', html)
        self.assertIn(f'/voice.js?v={build}', html)
        self.assertIn(f'const CLIENT_BUILD = "{build}";', javascript)

    def test_browser_tts_uses_piper_stdin_returns_wav_and_cleans_temp(self) -> None:
        observed: dict[str, object] = {}

        def render(command: list[str], *, input_text: str, timeout: float) -> dict[str, object]:
            observed["command"] = command
            observed["input_text"] = input_text
            observed["timeout"] = timeout
            output = console.Path(command[command.index("--output") + 1])
            observed["output"] = output
            output.write_bytes(b"RIFF" + b"\x24\x00\x00\x00" + b"WAVE" + (b"\0" * 36))
            return {"ok": True, "rc": 0, "stdout": "", "stderr": ""}

        with mock.patch.object(console, "run_capture", side_effect=render) as run:
            audio = console.synthesize_browser_wav("Réponse Piper locale")

        self.assertTrue(audio.startswith(b"RIFF"))
        self.assertEqual(audio[8:12], b"WAVE")
        self.assertEqual(observed["input_text"], "Réponse Piper locale\n")
        self.assertNotIn("Réponse Piper locale", repr(observed["command"]))
        self.assertFalse(observed["output"].exists())
        run.assert_called_once()

    def test_browser_tts_rejects_oversize_without_rendering(self) -> None:
        with mock.patch.object(console, "run_capture") as run:
            with self.assertRaisesRegex(console.BrowserTtsError, "limit"):
                console.synthesize_browser_wav("x" * (console.MAX_BROWSER_TTS_CHARS + 1))
        run.assert_not_called()

    def test_legacy_browser_say_endpoint_cannot_play_on_t480(self) -> None:
        handler = object.__new__(console.VoiceConsoleHandler)
        handler.send_json = mock.Mock()
        with mock.patch.object(console, "run_capture") as run:
            handler.handle_say()
        run.assert_not_called()
        payload = handler.send_json.call_args.args[0]
        self.assertFalse(payload["ok"])
        self.assertIn("disabled", payload["error"])
        self.assertEqual(handler.send_json.call_args.kwargs["status"], console.HTTPStatus.GONE)


if __name__ == "__main__":
    unittest.main()
