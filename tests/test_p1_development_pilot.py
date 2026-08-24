from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "validate_p1_development_pilot.py"
spec = importlib.util.spec_from_file_location("validate_p1_development_pilot", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class DevelopmentPilotPassAIntegrityTests(unittest.TestCase):
    def test_full_validator(self) -> None:
        self.assertEqual(module.main(), 0)

    def test_frozen_counts_and_order(self) -> None:
        temp, root = module.extract_bundle()
        try:
            annotations = module.read_jsonl(
                root / "data/p1/development-pilot/pass-a/human-pass-a-raw.jsonl"
            )
            self.assertEqual([x["trajectory_id"] for x in annotations], module.EXPECTED_COMPLETED)
            self.assertEqual(len(annotations), 25)
        finally:
            temp.cleanup()

    def test_reserve_cases_are_not_imputed(self) -> None:
        temp, root = module.extract_bundle()
        try:
            freeze = module.load_json(
                root / "data/p1/development-pilot/pass-a/freeze-manifest-v0.1.json"
            )
            self.assertEqual(freeze["unannotated_trajectory_ids"], module.EXPECTED_RESERVE)
            self.assertEqual(freeze["missingness_treatment"]["imputation"], "NONE")
        finally:
            temp.cleanup()

    def test_pass_b_commitment_does_not_disclose_ids(self) -> None:
        commitment = module.load_json(
            module.PILOT / "pass-b" / "subset-commitment-v0.1.json"
        )
        self.assertEqual(commitment["selected_count"], 12)
        self.assertFalse(commitment["identifiers_disclosed_before_pass_b"])
        self.assertNotIn("selected_trajectory_ids", commitment)
        self.assertNotIn("ordered_trajectory_ids", commitment)

    def test_delivery_manifest_preserves_source_and_key_commitments(self) -> None:
        delivery = module.load_json(module.PASS_A / "delivery-manifest-v0.2.json")
        self.assertEqual(delivery["episode_count"], 30)
        self.assertIn("PCT_P1_Development_Pilot_Pass_A_v0.2.zip", delivery["files"])
        self.assertIn("PCT_P1_Development_Pilot_Author_Key_Custody_v0.2.zip", delivery["files"])


if __name__ == "__main__":
    unittest.main()
