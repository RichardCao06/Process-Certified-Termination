from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def annotation(trajectory_id: str, recommendation: str = "ACCEPT") -> dict:
    accept = "ACCEPT" if recommendation == "ACCEPT" else "DO_NOT_ACCEPT"
    process = "PASS" if accept == "ACCEPT" else "FAIL"
    return {
        "trajectory_id": trajectory_id,
        "stop_id": "STOP1",
        "display_id": f"DISPLAY-{trajectory_id}",
        "accept_decision": accept,
        "outcome_verdict": "PASS" if accept == "ACCEPT" else "UNKNOWN",
        "process_verdict": process,
        "certification_recommendation": recommendation,
        "stop_scope": "GOAL_COMPLETION_PROPOSAL",
        "recovery_authority": (
            "NOT_APPLICABLE" if accept == "ACCEPT" else "SELF_SERVICE"
        ),
        "valid_alternative_path": "NOT_APPLICABLE",
        "certification_effects": (
            ["NONE"] if accept == "ACCEPT" else ["EVIDENCE_GAP"]
        ),
        "control_actions": (
            ["CERTIFY_GOAL_COMPLETE"]
            if accept == "ACCEPT"
            else ["REQUEST_VALIDATION"]
        ),
        "failure_codes": (
            [] if accept == "ACCEPT" else ["EVD.MISSING_REQUIRED_EVIDENCE"]
        ),
        "hard_gate_codes": (
            [] if accept == "ACCEPT" else ["EVD.MISSING_REQUIRED_EVIDENCE"]
        ),
        "first_invalid_transition": (
            {"status": "NONE", "reason": "none", "confidence": 0.5}
            if accept == "ACCEPT"
            else {
                "status": "EXACT",
                "event_id": "E2",
                "reason": "missing",
                "confidence": 0.5,
            }
        ),
        "evidence_assessment": {
            "sufficiency": "PASS" if accept == "ACCEPT" else "FAIL",
            "currentness": "PASS",
            "scope_match": "PASS",
            "conflicts_resolved": "PASS",
        },
        "citations": {
            "event_ids": ["E1"],
            "evidence_ids": ["EV1"] if accept == "ACCEPT" else [],
        },
    }


def write_jsonl(path: Path, items: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(item) + "\n" for item in items), encoding="utf-8"
    )


class AnalysisCliTests(unittest.TestCase):
    def test_agreement_and_adjudication_clis(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_name:
            tmp = Path(tmp_name)
            pass_a = tmp / "a.jsonl"
            pass_b = tmp / "b.jsonl"
            write_jsonl(
                pass_a,
                [annotation("a"), annotation("b", "EVIDENCE_REQUIRED")],
            )
            write_jsonl(pass_b, [annotation("b", "CONTINUE"), annotation("a")])
            episodes = tmp / "episodes.json"
            episodes.write_text(
                json.dumps(
                    {
                        "episodes": [
                            {
                                "trajectory_id": "a",
                                "episode": {
                                    "trajectory_id": "a",
                                    "events": [{"event_id": "E1"}],
                                },
                            },
                            {
                                "trajectory_id": "b",
                                "episode": {
                                    "trajectory_id": "b",
                                    "events": [
                                        {"event_id": "E1"},
                                        {"event_id": "E2"},
                                    ],
                                },
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )
            report = tmp / "report.json"
            pairs = tmp / "pairs.csv"
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "p1_pass_b_agreement.py"),
                    "--pass-a",
                    str(pass_a),
                    "--pass-b",
                    str(pass_b),
                    "--output-json",
                    str(report),
                    "--output-csv",
                    str(pairs),
                    "--expected-pairs",
                    "2",
                ],
                cwd=ROOT,
                check=True,
            )
            self.assertEqual(json.loads(report.read_text())["paired_items"], 2)

            packet = tmp / "packet.json"
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "p1_prepare_adjudication_packet.py"),
                    "--episodes",
                    str(episodes),
                    "--pass-a",
                    str(pass_a),
                    "--pass-b",
                    str(pass_b),
                    "--output",
                    str(packet),
                ],
                cwd=ROOT,
                check=True,
            )
            self.assertEqual(
                json.loads(packet.read_text())["disagreement_case_count"], 1
            )

    def test_author_opening_requires_two_frozen_passes_and_hash_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_name:
            tmp = Path(tmp_name)
            pass_a = tmp / "pass-a.json"
            pass_b = tmp / "pass-b.json"
            pass_a.write_text('{"frozen":true}', encoding="utf-8")
            pass_b.write_text('{"frozen":true}', encoding="utf-8")
            opened = tmp / "expectations.json"
            opened.write_text(
                '{"expectations":[{"trajectory_id":"a"}]}', encoding="utf-8"
            )
            commitment = tmp / "commitment.json"
            commitment.write_text(
                json.dumps(
                    {
                        "plaintext_sha256": hashlib.sha256(
                            opened.read_bytes()
                        ).hexdigest()
                    }
                ),
                encoding="utf-8",
            )
            output = tmp / "opening.json"
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "p1_verify_author_opening.py"),
                    "--pass-a-freeze",
                    str(pass_a),
                    "--pass-b-freeze",
                    str(pass_b),
                    "--expectation-commitment",
                    str(commitment),
                    "--opened-expectations",
                    str(opened),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                check=True,
            )
            self.assertTrue(json.loads(output.read_text())["verified"])


if __name__ == "__main__":
    unittest.main()
