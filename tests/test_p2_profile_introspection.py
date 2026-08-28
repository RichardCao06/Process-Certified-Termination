from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def canonical_digest(value: dict, field: str) -> str:
    base = dict(value)
    base.pop(field, None)
    raw = json.dumps(
        base,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class P2ProfileIntrospectionTests(unittest.TestCase):
    def run_offline(self, payload: dict) -> tuple[subprocess.CompletedProcess[str], dict | None]:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            models = tmp_path / "models.json"
            output = tmp_path / "report.json"
            models.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/run_p2_deepseek_profile_introspection.py",
                    "--models-json",
                    str(models),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            report = json.loads(output.read_text(encoding="utf-8")) if output.exists() else None
            return result, report

    def test_offline_model_listing_generates_sanitized_pass(self) -> None:
        result, report = self.run_offline(
            {
                "object": "list",
                "data": [
                    {
                        "id": "deepseek-v4-flash",
                        "object": "model",
                        "owned_by": "deepseek",
                    },
                    {
                        "id": "deepseek-v4-pro",
                        "object": "model",
                        "owned_by": "deepseek",
                    },
                ],
            }
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        assert report is not None
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["response"]["returned_model_identifier"], "deepseek-v4-pro")
        self.assertEqual(report["request"]["chat_completion_calls"], 0)
        self.assertFalse(report["request"]["task_generation"])
        self.assertEqual(report["report_digest"], canonical_digest(report, "report_digest"))
        raw = json.dumps(report)
        self.assertNotIn("sk-", raw)
        self.assertNotIn("Bearer ", raw)

    def test_missing_requested_model_is_not_silently_substituted(self) -> None:
        result, report = self.run_offline(
            {
                "object": "list",
                "data": [
                    {
                        "id": "deepseek-v4-flash",
                        "object": "model",
                        "owned_by": "deepseek",
                    }
                ],
            }
        )
        self.assertEqual(result.returncode, 6)
        assert report is not None
        self.assertEqual(report["status"], "FAIL_MODEL_NOT_LISTED")
        self.assertIsNone(report["response"]["returned_model_identifier"])

    def test_reference_downgrade_is_single_rater_and_not_gold(self) -> None:
        custody = json.loads(
            (ROOT / "governance/p2-reference-custody-v0.2.json").read_text(
                encoding="utf-8"
            )
        )
        semi = custody["semi_open_lane"]
        self.assertEqual(semi["reference_type"], "DEVELOPMENTAL_SINGLE_HUMAN_RATER")
        self.assertTrue(semi["rater_a"]["assigned"])
        self.assertFalse(semi["rater_b"]["assigned"])
        self.assertFalse(semi["independent_inter_rater_reliability_claim_allowed"])
        self.assertFalse(semi["gold_label_claim_allowed"])
        self.assertFalse(custody["reference_opening_authorized"])

    def test_workflow_never_passes_secret_as_cli_argument_or_echoes_it(self) -> None:
        workflow = (
            ROOT / ".github/workflows/p2-deepseek-profile-introspection.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("environment: p2-natural-pilot", workflow)
        self.assertIn("secrets.DEEPSEEK_API_KEY", workflow)
        self.assertNotIn("--api-key", workflow)
        self.assertNotIn("echo $DEEPSEEK_API_KEY", workflow)
        self.assertNotIn("set -x", workflow)


if __name__ == "__main__":
    unittest.main()
