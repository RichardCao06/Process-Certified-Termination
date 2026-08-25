from __future__ import annotations

import unittest

from pct.pilot_analysis import classify_disagreement, intrarater_report, pair_annotations


def annotation(
    trajectory_id: str,
    *,
    accept: str = "ACCEPT",
    outcome: str = "PASS",
    process: str = "PASS",
    recommendation: str = "ACCEPT",
    fit: dict | None = None,
    failures: list[str] | None = None,
    hard: list[str] | None = None,
) -> dict:
    return {
        "trajectory_id": trajectory_id,
        "stop_id": "STOP1",
        "accept_decision": accept,
        "outcome_verdict": outcome,
        "process_verdict": process,
        "certification_recommendation": recommendation,
        "stop_scope": "GOAL_COMPLETION_PROPOSAL",
        "recovery_authority": "NOT_APPLICABLE",
        "valid_alternative_path": "NOT_APPLICABLE",
        "certification_effects": (
            ["NONE"] if process == "PASS" else ["HARD_VIOLATION"]
        ),
        "control_actions": (
            ["CERTIFY_GOAL_COMPLETE"]
            if accept == "ACCEPT"
            else ["WITHHOLD_CERTIFICATION"]
        ),
        "failure_codes": failures or [],
        "hard_gate_codes": hard or [],
        "first_invalid_transition": fit
        or {"status": "NONE", "reason": "none", "confidence": 0.5},
        "evidence_assessment": {
            "sufficiency": "PASS",
            "currentness": "PASS",
            "scope_match": "PASS",
            "conflicts_resolved": "PASS",
        },
        "citations": {"event_ids": ["E1"], "evidence_ids": ["EV1"]},
    }


class PilotAnalysisTests(unittest.TestCase):
    def test_pairs_by_trajectory_not_input_order(self) -> None:
        pairs = pair_annotations(
            [annotation("b"), annotation("a")],
            [annotation("a"), annotation("b")],
        )
        self.assertEqual(
            [left["trajectory_id"] for left, _ in pairs], ["a", "b"]
        )

    def test_duplicate_annotation_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            pair_annotations(
                [annotation("a"), annotation("a")], [annotation("a")]
            )

    def test_report_captures_hierarchical_agreement(self) -> None:
        left = [
            annotation("a"),
            annotation(
                "b",
                accept="DO_NOT_ACCEPT",
                outcome="UNKNOWN",
                process="FAIL",
                recommendation="EVIDENCE_REQUIRED",
                fit={
                    "status": "EXACT",
                    "event_id": "E2",
                    "reason": "x",
                    "confidence": 0.5,
                },
                failures=["EVD.MISSING_REQUIRED_EVIDENCE"],
                hard=["EVD.MISSING_REQUIRED_EVIDENCE"],
            ),
        ]
        right = [
            annotation("a"),
            annotation(
                "b",
                accept="DO_NOT_ACCEPT",
                outcome="UNKNOWN",
                process="FAIL",
                recommendation="CONTINUE",
                fit={
                    "status": "EXACT",
                    "event_id": "E3",
                    "reason": "y",
                    "confidence": 0.7,
                },
                failures=[
                    "EVD.MISSING_REQUIRED_EVIDENCE",
                    "EXIT.PREMATURE_TERMINATION",
                ],
                hard=["EVD.MISSING_REQUIRED_EVIDENCE"],
            ),
        ]
        report = intrarater_report(left, right)
        self.assertEqual(report["paired_items"], 2)
        self.assertEqual(
            report["nominal"]["accept_decision"]["agreement_count"], 2
        )
        self.assertEqual(
            report["nominal"]["certification_recommendation"][
                "agreement_count"
            ],
            1,
        )
        self.assertEqual(report["fit"]["status_agreement_count"], 2)
        self.assertEqual(report["fit"]["locator_agreement_count"], 1)
        self.assertEqual(report["consensus"]["core_consensus_count"], 2)
        self.assertEqual(report["consensus"]["strict_consensus_count"], 1)

    def test_disagreement_categories_are_explicit(self) -> None:
        left = annotation(
            "a",
            accept="DO_NOT_ACCEPT",
            outcome="UNKNOWN",
            process="FAIL",
            recommendation="EVIDENCE_REQUIRED",
            fit={
                "status": "EXACT",
                "event_id": "E2",
                "reason": "x",
                "confidence": 0.5,
            },
            failures=["EVD.MISSING_REQUIRED_EVIDENCE"],
            hard=["EVD.MISSING_REQUIRED_EVIDENCE"],
        )
        right = annotation(
            "a",
            accept="DO_NOT_ACCEPT",
            outcome="FAIL",
            process="FAIL",
            recommendation="CONTINUE",
            fit={
                "status": "EXACT",
                "event_id": "E3",
                "reason": "y",
                "confidence": 0.5,
            },
            failures=["ACT.TOOL_FAILURE_IGNORED"],
            hard=["ACT.TOOL_FAILURE_IGNORED"],
        )
        categories = classify_disagreement(left, right)
        self.assertIn("OUTCOME_VERDICT", categories)
        self.assertIn("RECOMMENDATION", categories)
        self.assertIn("FAILURE_CODES", categories)
        self.assertIn("FIT_LOCATOR", categories)


if __name__ == "__main__":
    unittest.main()
