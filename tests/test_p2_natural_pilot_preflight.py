from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_validator_module():
    path = ROOT / "scripts/validate_p2_natural_pilot_preflight.py"
    spec = importlib.util.spec_from_file_location("validate_p2_natural_pilot_preflight", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class P2NaturalPilotPreflightTests(unittest.TestCase):
    def test_preflight_artifacts_are_consistent_but_blocked(self):
        module = load_validator_module()
        self.assertEqual(module.validate(), [])
        report = json.loads((ROOT / "reports/p2/natural-pilot-preflight-v0.1.json").read_text())
        self.assertEqual(report["status"], "BLOCKED")
        self.assertEqual(set(report["blocker_ids"]), module.BLOCKERS)
        self.assertEqual(report["live_worker_model_calls"], 0)

    def test_schedule_is_exactly_twenty_by_three(self):
        schedule = json.loads((ROOT / "data/p2/natural-pilot/run-schedule-v0.1.json").read_text())
        self.assertEqual(len(schedule["runs"]), 60)
        counts = {}
        for run in schedule["runs"]:
            counts[run["task_id"]] = counts.get(run["task_id"], 0) + 1
        self.assertEqual(len(counts), 20)
        self.assertEqual(set(counts.values()), {3})

    def test_materializer_and_deterministic_validator(self):
        from pct.pilot.materialize import materialize_task
        from pct.pilot.validators import validate_task
        with tempfile.TemporaryDirectory() as tmp:
            workspace = materialize_task("PCT-P2-NAT-001", tmp)
            (workspace / "output").mkdir()
            (workspace / "output/inventory.normalized.json").write_text(json.dumps({
                "items": [{"sku": "A-2", "qty": 5, "unit_price": 3.5}, {"sku": "B-1", "qty": 1, "unit_price": 10.0}],
                "summary": {"total_qty": 6, "inventory_value": 27.5},
            }))
            self.assertEqual(validate_task("PCT-P2-NAT-001", workspace)["status"], "PASS")

    def test_semantic_auditor_and_runtime_application_remain_disabled(self):
        protocol = json.loads((ROOT / "governance/p2-natural-pilot-protocol-v0.1.json").read_text())
        self.assertFalse(protocol["semantic_auditor"]["enabled"])
        self.assertFalse(protocol["applied_to_runtime"])
        self.assertFalse(protocol["online_intervention_authorized"])


if __name__ == "__main__":
    unittest.main()
