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


class DevelopmentPilotIntegrityTests(unittest.TestCase):
    def test_full_validator(self) -> None:
        self.assertEqual(module.main(), 0)

    def test_pass_a_frozen_counts_and_order(self) -> None:
        temp, root = module.extract_pass_a_bundle()
        try:
            annotations = module.read_jsonl(
                root / "data/p1/development-pilot/pass-a/human-pass-a-raw.jsonl"
            )
            self.assertEqual([x["trajectory_id"] for x in annotations], module.EXPECTED_COMPLETED)
            self.assertEqual(len(annotations), 25)
        finally:
            temp.cleanup()

    def test_reserve_cases_are_not_imputed(self) -> None:
        temp, root = module.extract_pass_a_bundle()
        try:
            freeze = module.load_json(
                root / "data/p1/development-pilot/pass-a/freeze-manifest-v0.1.json"
            )
            self.assertEqual(freeze["unannotated_trajectory_ids"], module.EXPECTED_RESERVE)
            self.assertEqual(freeze["missingness_treatment"]["imputation"], "NONE")
        finally:
            temp.cleanup()

    def test_historical_commitments_do_not_disclose_ids(self) -> None:
        for name in ("subset-commitment-v0.1.json", "subset-commitment-v0.2.json"):
            commitment = module.load_json(module.PASS_B / name)
            self.assertEqual(commitment["selected_count"], 12)
            self.assertFalse(commitment["identifiers_disclosed_before_pass_b"])
            self.assertNotIn("selected_trajectory_ids", commitment)
            self.assertNotIn("ordered_trajectory_ids", commitment)

    def test_release_matches_precommitted_order(self) -> None:
        release = module.load_json(module.PASS_B / "release-record-v0.1.json")
        self.assertEqual(release["ordered_trajectory_ids"], module.EXPECTED_PASS_B_ORDER)
        self.assertEqual(
            module.canonical_order_sha(release["ordered_trajectory_ids"]),
            module.EXPECTED_PASS_B_COMMITMENT,
        )
        self.assertTrue(release["commitment_verified"])
        self.assertFalse(release["selection_or_order_changed_at_release"])

    def test_release_delivery_contains_no_author_expectations(self) -> None:
        manifest = module.load_json(module.PASS_B / "release-delivery-manifest-v0.1.json")
        self.assertFalse(manifest["contains_pass_a_annotations"])
        self.assertFalse(manifest["contains_pass_a_qc"])
        self.assertFalse(manifest["contains_fixture_author_expectations"])
        self.assertFalse(manifest["held_out_or_sealed_data"])


if __name__ == "__main__":
    unittest.main()
