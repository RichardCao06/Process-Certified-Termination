from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_p2_d21_preflight", ROOT / "scripts/validate_p2_d21_preflight.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class D21PreflightTests(unittest.TestCase):
    def test_full_preflight(self) -> None:
        self.assertEqual(MODULE.validate(), [])

    def test_active_d19_workflow_is_fail_closed(self) -> None:
        text = (ROOT / ".github/workflows/p2-engineering-smoke.yml").read_text(encoding="utf-8")
        active = MODULE.uncommented_yaml(text)
        self.assertIn("workflow_dispatch:", active)
        self.assertNotIn("pull_request:", active)
        self.assertNotIn("environment: p2-natural-pilot", active)
        self.assertNotIn("secrets.DEEPSEEK_API_KEY", active)
        self.assertIn("PCT-P2-D21", active)

    def test_no_model_evidence_boundaries(self) -> None:
        for relative in (
            "reports/p2/cordis-config-boot-diagnostic-v0.1.json",
            "reports/p2/official-patch-no-model-validation-v0.1.json",
        ):
            payload = json.loads((ROOT / relative).read_text(encoding="utf-8"))
            self.assertTrue(MODULE.zero_boundary(payload["safety_boundary"]))

    def test_d21_is_pending_and_primary_authority_closed(self) -> None:
        status = json.loads((ROOT / "governance/p2-status-v0.7.json").read_text(encoding="utf-8"))
        self.assertEqual(status["open_normative_gate_ids"], ["PCT-P2-D21"])
        self.assertFalse(status["additional_engineering_worker_calls_authorized"])
        self.assertFalse(status["natural_task_shadow_measurement_authorized"])
        self.assertEqual(status["primary_schedule_runs_completed"], 0)


if __name__ == "__main__":
    unittest.main()
