from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from pct.agreement import agreement_report, cohens_kappa, mean_multilabel_jaccard, percent_agreement
from pct.dsh_mapping import map_session_event, map_turn_stopping
from pct.validation import TaxonomyIndex, lint_trajectory, load_json, validate_annotation, validate_taxonomy, validate_trajectory

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "data" / "p1" / "synthetic"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class TaxonomyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.taxonomy_data = load_json(ROOT / "taxonomy" / "process-failure-taxonomy-v0.1-draft.json")
        cls.taxonomy = TaxonomyIndex.from_data(cls.taxonomy_data)

    def test_taxonomy_is_structurally_valid(self) -> None:
        self.assertEqual(validate_taxonomy(self.taxonomy_data), [])
        self.assertIn("EVD.STALE_EVIDENCE", self.taxonomy.codes)
        self.assertIn("INT.EVALUATOR_TAMPERING", self.taxonomy.hard_gate_codes)

    def test_every_hard_code_has_p0_provenance(self) -> None:
        for family in self.taxonomy_data["families"]:
            for item in family["codes"]:
                if item["candidate_hard_gate"]:
                    self.assertTrue(item.get("p0_hard_gate"), item["code"])


class TrajectoryTests(unittest.TestCase):
    def test_all_synthetic_fixtures_are_structurally_valid(self) -> None:
        for path in FIXTURES.glob("*.json"):
            with self.subTest(path=path.name):
                self.assertEqual(validate_trajectory(load_json(path)), [])

    def test_expected_lints(self) -> None:
        expected = load_json(ROOT / "tests" / "fixtures" / "p1" / "expected-lints.json")
        for filename, expected_codes in expected.items():
            with self.subTest(filename=filename):
                actual = sorted(item.code for item in lint_trajectory(load_json(FIXTURES / filename)))
                self.assertEqual(actual, sorted(expected_codes))

    def test_valid_alternative_path_is_negative_control(self) -> None:
        self.assertEqual(lint_trajectory(load_json(FIXTURES / "valid-alternative-path.json")), [])

    def test_duplicate_event_id_is_rejected(self) -> None:
        data = load_json(FIXTURES / "valid-alternative-path.json")
        data["events"][1]["event_id"] = data["events"][0]["event_id"]
        codes = {item.code for item in validate_trajectory(data)}
        self.assertIn("DUPLICATE_EVENT", codes)

    def test_hidden_gold_field_is_rejected(self) -> None:
        data = load_json(FIXTURES / "valid-alternative-path.json")
        data["events"][0]["payload"]["gold_label"] = "PASS"
        codes = {item.code for item in validate_trajectory(data)}
        self.assertIn("SEALED_LEAKAGE_FIELD", codes)

    def test_failure_trajectory_remains_structurally_valid(self) -> None:
        data = load_json(FIXTURES / "ignored-tool-failure.json")
        self.assertEqual(validate_trajectory(data), [])
        self.assertIn("ACT.TOOL_FAILURE_IGNORED", {item.code for item in lint_trajectory(data)})


class AnnotationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.taxonomy = TaxonomyIndex.from_data(load_json(ROOT / "taxonomy" / "process-failure-taxonomy-v0.1-draft.json"))
        cls.trajectories = {load_json(path)["trajectory_id"]: load_json(path) for path in FIXTURES.glob("*.json")}
        cls.annotations = read_jsonl(ROOT / "data" / "p1" / "annotations" / "fixture-author.jsonl")

    def test_fixture_annotations_are_valid(self) -> None:
        for annotation in self.annotations:
            trajectory = self.trajectories[annotation["trajectory_id"]]
            with self.subTest(annotation=annotation["annotation_id"]):
                self.assertEqual(validate_annotation(annotation, trajectory, self.taxonomy), [])

    def test_accept_cannot_coexist_with_failed_process(self) -> None:
        annotation = copy.deepcopy(self.annotations[0])
        annotation["process_verdict"] = "FAIL"
        annotation["failure_codes"] = ["EVD.MISSING_REQUIRED_EVIDENCE"]
        codes = {item.code for item in validate_annotation(annotation, self.trajectories[annotation["trajectory_id"]], self.taxonomy)}
        self.assertIn("UNSAFE_ACCEPT", codes)

    def test_unapproved_code_cannot_be_hard_gate(self) -> None:
        annotation = copy.deepcopy(next(item for item in self.annotations if item["trajectory_id"] == "traj-premature-promotion"))
        annotation["failure_codes"].append("EXIT.PREMATURE_TERMINATION")
        annotation["hard_gate_codes"].append("EXIT.PREMATURE_TERMINATION")
        codes = {item.code for item in validate_annotation(annotation, self.trajectories[annotation["trajectory_id"]], self.taxonomy)}
        self.assertIn("UNAPPROVED_HARD_GATE", codes)


class AgreementTests(unittest.TestCase):
    def test_basic_metrics(self) -> None:
        self.assertEqual(percent_agreement(["A", "B"], ["A", "C"]), 0.5)
        self.assertAlmostEqual(cohens_kappa(["A", "B", "A", "B"], ["A", "B", "A", "B"]), 1.0)
        self.assertAlmostEqual(mean_multilabel_jaccard([{"A", "B"}], [{"B", "C"}]), 1 / 3)

    def test_smoke_agreement_report(self) -> None:
        left = read_jsonl(ROOT / "tests" / "fixtures" / "p1" / "annotator-a.jsonl")
        right = read_jsonl(ROOT / "tests" / "fixtures" / "p1" / "annotator-b.jsonl")
        report = agreement_report(left, right)
        self.assertEqual(report["paired_items"], 5)
        self.assertLess(report["failure_code_jaccard"], 1.0)
        self.assertGreater(report["failure_code_jaccard"], 0.8)
        self.assertLess(report["localization_exact_or_status_agreement"], 1.0)


class DeepSeekMappingTests(unittest.TestCase):
    def test_session_tool_result_mapping(self) -> None:
        event = map_session_event(
            {"type": "tool/result", "data": {"result": {"isError": True}}},
            sequence=7,
            goal_revision=1,
            snapshot_id="S1",
        )
        self.assertIsNotNone(event)
        assert event is not None
        self.assertEqual(event["event_type"], "TOOL_RESULT")
        self.assertEqual(event["payload"]["status"], "FAIL")
        self.assertFalse(event["payload"]["authoritative"])

    def test_turn_stopping_mapping(self) -> None:
        event, stop = map_turn_stopping(turn=3, sequence=12, goal_revision=1, snapshot_id="S2")
        self.assertEqual(event["event_type"], "CANDIDATE_STOP")
        self.assertEqual(stop["event_id"], event["event_id"])
        self.assertEqual(stop["worker_claim"], "NO_FURTHER_ACTION")


if __name__ == "__main__":
    unittest.main()
