from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from ai.voice_task_spec import (
    MAX_CANONICAL_BYTES,
    RESULT_SCHEMA_VERSION,
    SCHEMA_VERSION,
    VoiceTaskSpecError,
    canonical_json,
    load_and_validate,
    spec_digest,
    validate_codex_result,
    validate_spec,
)


ROOT = Path(__file__).resolve().parents[1]


def valid_spec() -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "goal": "Inspect the voice boundary.",
        "workspace": "/home/operator/T480",
        "allowed_scope": ["ai", "tests"],
        "constraints": ["Do not modify files."],
        "deliverable": "A concise findings report.",
        "acceptance_checks": ["Report only evidence from the allowed scope."],
        "approval_class": "read_only",
        "clarification_state": "resolved",
    }


def valid_result() -> dict[str, object]:
    return {
        "schema_version": RESULT_SCHEMA_VERSION,
        "summary": "The requested inspection completed.",
        "findings": ["The boundary is explicit."],
        "checks": ["Validation completed."],
        "clarifications": [],
    }


class SchemaContractTests(unittest.TestCase):
    def test_task_schema_is_closed_and_matches_validator_fields(self) -> None:
        schema = json.loads((ROOT / "ai/voice_task_spec.schema.json").read_text(encoding="utf-8"))
        expected = set(valid_spec())
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["required"]), expected)
        self.assertEqual(set(schema["properties"]), expected)
        self.assertEqual(schema["properties"]["schema_version"]["const"], SCHEMA_VERSION)
        self.assertEqual(schema["properties"]["workspace"]["const"], "/home/operator/T480")
        self.assertEqual(schema["properties"]["approval_class"]["const"], "read_only")
        self.assertEqual(
            schema["properties"]["clarification_state"]["enum"],
            ["resolved", "needs_clarification"],
        )

    def test_result_schema_is_closed_bounded_and_has_no_prompt_fields(self) -> None:
        schema = json.loads(
            (ROOT / "ai/codex_readonly_result.schema.json").read_text(encoding="utf-8")
        )
        expected = set(valid_result())
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["required"]), expected)
        self.assertEqual(set(schema["properties"]), expected)
        self.assertEqual(
            schema["properties"]["schema_version"]["const"], RESULT_SCHEMA_VERSION
        )
        for name in ("findings", "checks", "clarifications"):
            self.assertIn("maxItems", schema["properties"][name])
            self.assertIn("maxLength", schema["properties"][name]["items"])
        self.assertTrue({"transcript", "audio", "raw", "prompt"}.isdisjoint(expected))


class TaskSpecValidationTests(unittest.TestCase):
    def test_valid_spec_is_normalized_without_mutating_input(self) -> None:
        source = valid_spec()
        source["goal"] = "  Re\u0301sumer \n  la frontière.  "
        before = copy.deepcopy(source)
        normalized = validate_spec(source)
        self.assertEqual(normalized["goal"], "Résumer la frontière.")
        self.assertEqual(source, before)
        self.assertIsNot(normalized, source)

    def test_canonical_json_and_digest_are_stable(self) -> None:
        source = valid_spec()
        canonical = canonical_json(source)
        reordered = dict(reversed(list(source.items())))
        self.assertEqual(canonical_json(reordered), canonical)
        self.assertEqual(spec_digest(reordered), spec_digest(source))
        self.assertEqual(spec_digest(source), hashlib.sha256(canonical.encode("utf-8")).hexdigest())
        self.assertNotIn("\n", canonical)
        self.assertEqual(json.loads(canonical), validate_spec(source))

    def test_unknown_and_every_banned_field_name_are_rejected(self) -> None:
        for name in (
            "notes",
            "transcript",
            "audio_blob",
            "rawInput",
            "shell",
            "shell_command",
            "auth_token",
            "private_key",
            "password",
            "credential_data",
        ):
            with self.subTest(name=name):
                source = valid_spec()
                source[name] = "must not cross the boundary"
                with self.assertRaises(VoiceTaskSpecError):
                    validate_spec(source)

    def test_secret_like_content_is_rejected_without_echoing_it(self) -> None:
        sentinels = (
            "password=hunter2",
            "api_key:abcd1234",
            "sk-proj-abcdefghijklmnop",
            "Bearer abcdefghijklmnop",
            "https://alice:correct-horse@example.invalid/path",
            "-----BEGIN PRIVATE KEY-----",
            "eyJabcdefghijk.abcdefghijk.abcdefghijk",
        )
        for sentinel in sentinels:
            with self.subTest(sentinel=sentinel[:12]):
                source = valid_spec()
                source["goal"] = f"Inspect marker {sentinel} safely."
                with self.assertRaises(VoiceTaskSpecError) as raised:
                    validate_spec(source)
                self.assertNotIn(sentinel, str(raised.exception))

    def test_workspace_must_be_exact_literal_resolved_repo(self) -> None:
        for workspace in (
            "/home/operator/T480/",
            "/home/operator/T480/.",
            "/home/operator",
            "/tmp",
            "ai",
        ):
            with self.subTest(workspace=workspace):
                source = valid_spec()
                source["workspace"] = workspace
                with self.assertRaises(VoiceTaskSpecError):
                    validate_spec(source)

    def test_scope_rejects_absolute_traversal_and_noncanonical_paths(self) -> None:
        for scope in (
            "/home/operator/T480/ai",
            "/etc",
            "../etc",
            "ai/../../etc",
            "ai/../context",
            "./ai",
            "ai//voice_task_spec.py",
            "ai/",
            "ai\\voice_task_spec.py",
        ):
            with self.subTest(scope=scope):
                source = valid_spec()
                source["allowed_scope"] = [scope]
                with self.assertRaises(VoiceTaskSpecError):
                    validate_spec(source)

    def test_unresolved_or_unknown_clarification_is_rejected(self) -> None:
        for state in ("unresolved", "needed", "", None, {"status": "resolved"}):
            with self.subTest(state=state):
                source = valid_spec()
                source["clarification_state"] = state
                with self.assertRaises(VoiceTaskSpecError):
                    validate_spec(source)

    def test_read_only_is_the_only_approval_class(self) -> None:
        for approval in ("workspace_write", "full_access", "read-only", ""):
            with self.subTest(approval=approval):
                source = valid_spec()
                source["approval_class"] = approval
                with self.assertRaises(VoiceTaskSpecError):
                    validate_spec(source)

    def test_field_and_list_limits_fail_closed(self) -> None:
        mutations = []
        oversized_goal = valid_spec()
        oversized_goal["goal"] = "g" * 401
        mutations.append(oversized_goal)
        too_many_scopes = valid_spec()
        too_many_scopes["allowed_scope"] = [f"ai/scope-{index}" for index in range(17)]
        mutations.append(too_many_scopes)
        oversized_constraint = valid_spec()
        oversized_constraint["constraints"] = ["c" * 241]
        mutations.append(oversized_constraint)
        duplicate_checks = valid_spec()
        duplicate_checks["acceptance_checks"] = ["same", " same "]
        mutations.append(duplicate_checks)
        for source in mutations:
            with self.subTest(keys=list(source)):
                with self.assertRaises(VoiceTaskSpecError):
                    validate_spec(source)

    def test_total_canonical_limit_is_enforced(self) -> None:
        source = valid_spec()
        source["goal"] = "g" * 400
        source["deliverable"] = "d" * 400
        source["allowed_scope"] = [
            f"ai/scope-{index:02d}-" + ("x" * 145) for index in range(16)
        ]
        source["constraints"] = [f"{index:02d}-" + ("c" * 237) for index in range(12)]
        source["acceptance_checks"] = [f"{index:02d}-" + ("a" * 237) for index in range(12)]
        with self.assertRaisesRegex(VoiceTaskSpecError, "total byte limit"):
            validate_spec(source)

    def test_non_json_and_control_values_are_rejected(self) -> None:
        sources = []
        wrong_list = valid_spec()
        wrong_list["constraints"] = ("tuple",)
        sources.append(wrong_list)
        control = valid_spec()
        control["goal"] = "invisible\u200bmarker"
        sources.append(control)
        non_string = valid_spec()
        non_string["deliverable"] = 7
        sources.append(non_string)
        for source in sources:
            with self.assertRaises(VoiceTaskSpecError):
                validate_spec(source)

    def test_load_validates_bounded_json_and_rejects_duplicate_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            valid_path = Path(directory) / "valid.json"
            valid_path.write_text(json.dumps(valid_spec()), encoding="utf-8")
            self.assertEqual(load_and_validate(valid_path), validate_spec(valid_spec()))

            duplicate_path = Path(directory) / "duplicate.json"
            duplicate_path.write_text(
                '{"schema_version":"ctos.voice_task.v1","schema_version":"duplicate"}',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(VoiceTaskSpecError, "duplicate"):
                load_and_validate(duplicate_path)

            malformed_path = Path(directory) / "malformed.json"
            malformed_path.write_text("{", encoding="utf-8")
            with self.assertRaises(VoiceTaskSpecError):
                load_and_validate(malformed_path)


class CodexResultValidationTests(unittest.TestCase):
    def test_valid_result_is_normalized(self) -> None:
        result = valid_result()
        result["summary"] = "  Inspection  terminée. "
        normalized = validate_codex_result(result)
        self.assertEqual(normalized["summary"], "Inspection terminée.")

    def test_result_rejects_raw_prompt_unknown_and_secret_content(self) -> None:
        for field in ("raw", "transcript", "prompt", "audio"):
            with self.subTest(field=field):
                result = valid_result()
                result[field] = "forbidden"
                with self.assertRaises(VoiceTaskSpecError):
                    validate_codex_result(result)
        result = valid_result()
        result["findings"] = ["password=hunter2"]
        with self.assertRaises(VoiceTaskSpecError):
            validate_codex_result(result)

    def test_result_limits_are_enforced(self) -> None:
        result = valid_result()
        result["findings"] = [f"finding {index}" for index in range(25)]
        with self.assertRaises(VoiceTaskSpecError):
            validate_codex_result(result)
        result = valid_result()
        result["summary"] = "s" * 2001
        with self.assertRaises(VoiceTaskSpecError):
            validate_codex_result(result)


if __name__ == "__main__":
    unittest.main()
