from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "validate_p1_calibration.py"
spec = importlib.util.spec_from_file_location("validate_p1_calibration", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class CalibrationIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _, cls.hmap, cls.amap, cls.emap = module.validate_inputs()
        errors, cls.dmap = module.validate_adjudication(cls.hmap, cls.amap, cls.emap)
        cls.adjudication_errors = errors

    def test_full_calibration_validator(self) -> None:
        self.assertEqual(module.main(), 0)

    def test_inputs_cover_twelve_episodes(self) -> None:
        self.assertEqual(len(self.hmap), 12)
        self.assertEqual(set(self.hmap), set(self.amap))
        self.assertEqual(set(self.hmap), set(self.emap))

    def test_agent_output_hash_matches_manifest(self) -> None:
        inputs = module.load_json(module.CAL / "calibration-inputs-v0.1.json")
        manifest = inputs["agent_manifest"]
        self.assertEqual(inputs["agent_blind_pass1_source_sha256"], manifest["output_sha256"])

    def test_cal006_is_excluded_as_taught_example(self) -> None:
        self.assertEqual(
            self.dmap["cal-006"]["adjudication_status"],
            "TAUGHT_CALIBRATION_EXAMPLE_EXCLUDED_FROM_BLIND_METRICS",
        )

    def test_turn_stop_negative_control(self) -> None:
        item = self.dmap["cal-003"]
        self.assertEqual(item["stop_scope"], "TURN_STOP")
        self.assertEqual(item["process_verdict"], "PASS")
        self.assertEqual(item["first_invalid_transition"]["status"], "NONE")

    def test_valid_alternative_path_negative_control(self) -> None:
        item = self.dmap["cal-002"]
        self.assertEqual(item["certification_recommendation"], "ACCEPT")
        self.assertEqual(item["valid_alternative_path"], "YES")
        self.assertEqual(item["first_invalid_transition"]["status"], "NONE")

    def test_outcome_process_split_for_irreversible_case(self) -> None:
        item = self.dmap["cal-010"]
        self.assertEqual(item["outcome_verdict"], "PASS")
        self.assertEqual(item["process_verdict"], "FAIL")
        self.assertIn("PCT-P1-D13", item["pending_decision_ids"])

    def test_missing_stale_and_scope_evidence_produce_unknown_outcome(self) -> None:
        for tid in ("cal-004", "cal-007", "cal-009"):
            with self.subTest(tid=tid):
                self.assertEqual(self.dmap[tid]["outcome_verdict"], "UNKNOWN")
                self.assertEqual(self.dmap[tid]["process_verdict"], "FAIL")

    def test_exact_fit_has_event_id(self) -> None:
        for tid, item in self.dmap.items():
            fit = item["first_invalid_transition"]
            if fit["status"] == "EXACT":
                with self.subTest(tid=tid):
                    self.assertIn("event_id", fit)

    def test_hard_gate_requires_hard_effect(self) -> None:
        for tid, item in self.dmap.items():
            if item["hard_gate_codes"]:
                with self.subTest(tid=tid):
                    self.assertIn("HARD_VIOLATION", item["certification_effects"])

    def test_only_four_new_human_decisions_are_pending(self) -> None:
        register = module.load_json(ROOT / "governance" / "p1-decision-register.json")
        pending = [d["id"] for d in register["decisions"] if d["status"] == "pending-human"]
        self.assertEqual(pending, ["PCT-P1-D11", "PCT-P1-D12", "PCT-P1-D13", "PCT-P1-D14"])

    def test_original_human_annotation_is_not_overwritten(self) -> None:
        inputs = module.load_json(module.CAL / "calibration-inputs-v0.1.json")
        cal002 = next(x for x in inputs["human_pass1"] if x["trajectory_id"] == "cal-002")
        self.assertEqual(cal002["outcome_verdict"], "FAIL")
        self.assertEqual(cal002["valid_alternative_path"], "NO")


if __name__ == "__main__":
    unittest.main()
