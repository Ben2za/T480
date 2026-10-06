from __future__ import annotations

import contextlib
import importlib.machinery
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ctos-codex-voice"
LOADER = importlib.machinery.SourceFileLoader("ctos_codex_voice", str(SCRIPT))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
assert SPEC is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
LOADER.exec_module(MODULE)


VALID_SPEC = {
    "schema_version": "ctos.voice_task.v1",
    "goal": "Inspect the voice boundary.",
    "workspace": "/home/operator/T480",
    "allowed_scope": ["ai", "tests"],
    "constraints": ["Do not modify files."],
    "deliverable": "A concise findings report.",
    "acceptance_checks": ["Report only evidence from the allowed scope."],
    "approval_class": "read_only",
    "clarification_state": "resolved",
}

EXPECTED_ARGV = [
    "codex",
    "exec",
    "--ephemeral",
    "--ignore-user-config",
    "-c",
    "project_doc_max_bytes=0",
    "-c",
    'web_search="disabled"',
    "--sandbox",
    "read-only",
    "-C",
    "/home/operator/T480",
    "--output-schema",
    "/home/operator/T480/ai/codex_readonly_result.schema.json",
    "-",
]

VALID_CODEX_RESULT = {
    "schema_version": "ctos.codex_readonly_result.v1",
    "summary": "Read-only review ready.",
    "findings": [],
    "checks": [],
    "clarifications": [],
}


class CodexVoiceBoundaryTests(unittest.TestCase):
    def invoke(
        self,
        argv: list[str],
        *,
        stdin_text: str = "",
    ) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            mock.patch.object(MODULE.sys, "stdin", io.StringIO(stdin_text)),
            contextlib.redirect_stdout(stdout),
            contextlib.redirect_stderr(stderr),
        ):
            rc = MODULE.main(argv)
        return rc, stdout.getvalue(), stderr.getvalue()

    def write_spec(self, directory: str, payload: object = VALID_SPEC) -> Path:
        path = Path(directory) / "task.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_plan_prints_exact_argv_canonical_spec_and_digest_without_execution(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_spec(directory)
            with mock.patch.object(MODULE.subprocess, "run") as run:
                rc, stdout, stderr = self.invoke(["plan", str(path)])

        self.assertEqual(rc, 0)
        self.assertEqual(stderr, "")
        run.assert_not_called()
        payload = json.loads(stdout)
        normalized = MODULE.validate_spec(VALID_SPEC)
        self.assertEqual(payload["operation"], "plan")
        self.assertFalse(payload["will_execute"])
        self.assertEqual(payload["argv"], EXPECTED_ARGV)
        self.assertEqual(payload["canonical_spec"], MODULE.canonical_json(normalized))
        self.assertEqual(payload["spec_sha256"], MODULE.spec_digest(normalized))

    def test_validate_accepts_a_spec_from_stdin_without_starting_codex(self) -> None:
        with mock.patch.object(MODULE.subprocess, "run") as run:
            rc, stdout, stderr = self.invoke(
                ["validate", "-"], stdin_text=json.dumps(VALID_SPEC)
            )

        self.assertEqual(rc, 0)
        self.assertEqual(stderr, "")
        run.assert_not_called()
        payload = json.loads(stdout)
        self.assertEqual(payload["operation"], "validate")
        self.assertEqual(
            payload["canonical_spec"],
            MODULE.canonical_json(MODULE.validate_spec(VALID_SPEC)),
        )

    def test_checked_in_result_schema_is_present_and_valid_json(self) -> None:
        self.assertIsNone(MODULE.ensure_result_schema())

    def test_run_requires_explicit_confirmation_before_any_process(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_spec(directory)
            with mock.patch.object(MODULE.subprocess, "run") as run:
                rc, stdout, stderr = self.invoke(["run", str(path)])

        self.assertEqual(rc, 2)
        self.assertEqual(stdout, "")
        self.assertIn("explicit --yes confirmation", stderr)
        run.assert_not_called()

    def test_run_uses_only_exact_codex_flags_and_rebuilt_spec_only_stdin(self) -> None:
        raw_sentinel = "RAW_STT_SENTINEL_MUST_NOT_CROSS_BOUNDARY"
        codex_result = json.dumps(VALID_CODEX_RESULT)
        completed = subprocess.CompletedProcess(
            EXPECTED_ARGV,
            0,
            stdout=codex_result,
            stderr="",
        )

        with (
            mock.patch.object(MODULE, "ensure_result_schema"),
            mock.patch.object(MODULE.subprocess, "run", return_value=completed) as run,
        ):
            rc, stdout, stderr = self.invoke(
                ["run", "-", "--yes", "--timeout", "37"],
                stdin_text=json.dumps(VALID_SPEC),
            )

        self.assertEqual(rc, 0)
        self.assertEqual(stderr, "")
        self.assertEqual(json.loads(stdout), json.loads(codex_result))
        run.assert_called_once()
        call = run.call_args
        self.assertEqual(call.args[0], EXPECTED_ARGV)
        self.assertEqual(call.kwargs["timeout"], 37)
        self.assertTrue(call.kwargs["capture_output"])
        self.assertTrue(call.kwargs["text"])
        self.assertFalse(call.kwargs["check"])

        normalized = MODULE.validate_spec(VALID_SPEC)
        self.assertEqual(
            call.kwargs["input"],
            f"{MODULE.FIXED_INSTRUCTION}{MODULE.canonical_json(normalized)}\n",
        )
        self.assertIn(
            "Inspect only repository paths listed in allowed_scope",
            call.kwargs["input"],
        )
        self.assertNotIn(raw_sentinel, call.kwargs["input"])

    def test_raw_transcript_field_is_rejected_without_echo_or_execution(self) -> None:
        raw_sentinel = "RAW_STT_SENTINEL_MUST_NOT_CROSS_BOUNDARY"
        invalid = dict(VALID_SPEC)
        invalid["transcript"] = raw_sentinel

        with mock.patch.object(MODULE.subprocess, "run") as run:
            rc, stdout, stderr = self.invoke(
                ["run", "-", "--yes"], stdin_text=json.dumps(invalid)
            )

        self.assertEqual(rc, 2)
        self.assertEqual(stdout, "")
        self.assertIn("task spec rejected", stderr)
        self.assertNotIn(raw_sentinel, stderr)
        run.assert_not_called()

    def test_duplicate_spec_keys_are_rejected_from_stdin_and_files(self) -> None:
        duplicate = json.dumps(VALID_SPEC)[:-1] + ',"goal":"second value"}'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text(duplicate, encoding="utf-8")
            cases = (
                (["run", "-", "--yes"], duplicate),
                (["run", str(path), "--yes"], ""),
            )
            for argv, stdin_text in cases:
                with self.subTest(source=argv[1]):
                    with mock.patch.object(MODULE.subprocess, "run") as run:
                        rc, stdout, stderr = self.invoke(
                            argv, stdin_text=stdin_text
                        )

                    self.assertEqual(rc, 2)
                    self.assertEqual(stdout, "")
                    self.assertIn("duplicate JSON field", stderr)
                    run.assert_not_called()

    def test_codex_failure_is_visible_and_has_no_local_fallback(self) -> None:
        completed = subprocess.CompletedProcess(
            EXPECTED_ARGV,
            75,
            stdout="",
            stderr="authentication or quota failure",
        )
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_spec(directory)
            with (
                mock.patch.object(MODULE, "ensure_result_schema"),
                mock.patch.object(
                    MODULE.subprocess, "run", return_value=completed
                ) as run,
            ):
                rc, stdout, stderr = self.invoke(["run", str(path), "--yes"])

        self.assertEqual(rc, 75)
        self.assertEqual(stdout, "")
        self.assertIn("Codex exited with status 75", stderr)
        self.assertIn("authentication or quota failure", stderr)
        run.assert_called_once()
        self.assertEqual(run.call_args.args[0][0:2], ["codex", "exec"])
        self.assertNotIn("ollama", repr(run.call_args).lower())

    def test_success_status_with_non_json_or_schema_invalid_output_fails_closed(
        self,
    ) -> None:
        outputs = (
            ("not JSON", "not one valid JSON document"),
            (
                '{"schema_version":"ctos.codex_readonly_result.v1"}\n'
                '{"summary":"second document"}',
                "not one valid JSON document",
            ),
            (
                '{"schema_version":"ctos.codex_readonly_result.v1"}',
                "missing required field",
            ),
        )
        for stdout_value, expected_error in outputs:
            with self.subTest(stdout=stdout_value):
                completed = subprocess.CompletedProcess(
                    EXPECTED_ARGV,
                    0,
                    stdout=stdout_value,
                    stderr="",
                )
                with (
                    mock.patch.object(MODULE, "ensure_result_schema"),
                    mock.patch.object(
                        MODULE.subprocess, "run", return_value=completed
                    ) as run,
                ):
                    rc, stdout, stderr = self.invoke(
                        ["run", "-", "--yes"], stdin_text=json.dumps(VALID_SPEC)
                    )

                self.assertEqual(rc, 1)
                self.assertEqual(stdout, "")
                self.assertIn(expected_error, stderr)
                run.assert_called_once()

    def test_success_status_with_oversized_output_is_rejected(self) -> None:
        completed = subprocess.CompletedProcess(
            EXPECTED_ARGV,
            0,
            stdout="x" * (MODULE.MAX_CODEX_STDOUT_BYTES + 1),
            stderr="",
        )
        with (
            mock.patch.object(MODULE, "ensure_result_schema"),
            mock.patch.object(MODULE.subprocess, "run", return_value=completed) as run,
        ):
            rc, stdout, stderr = self.invoke(
                ["run", "-", "--yes"], stdin_text=json.dumps(VALID_SPEC)
            )

        self.assertEqual(rc, 1)
        self.assertEqual(stdout, "")
        self.assertIn("result exceeds", stderr)
        run.assert_called_once()

    def test_stderr_excerpt_removes_controls_and_stays_bounded(self) -> None:
        excerpt = MODULE.safe_stderr_excerpt(
            "\x1b" + "failure " * MODULE.MAX_CODEX_STDERR_DISPLAY_BYTES
        )
        self.assertNotIn("\x1b", excerpt)
        self.assertIn("[Codex stderr truncated]", excerpt)
        self.assertLessEqual(
            len(excerpt.encode("utf-8")), MODULE.MAX_CODEX_STDERR_DISPLAY_BYTES
        )


if __name__ == "__main__":
    unittest.main()
