from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from pct.shadow.adapter import DeepSeekHarnessAdapter
from pct.shadow.replay import run_replay, verify_replay
from pct.shadow.sidecar import CandidateStopSidecar, ReadOnlyCandidateStopObserver

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / "governance/p2-shadow-policy-v0.1.json").read_text(encoding="utf-8"))


def replay_input(*, sidecar: CandidateStopSidecar | None, assistant_text: str = "") -> dict:
    observer = ReadOnlyCandidateStopObserver()
    events = [
        {
            "event_id": "E1", "sequence": 1, "event_type": "GOAL_STATE", "source": "SYSTEM",
            "goal_id": "G", "goal_revision": 1, "snapshot_id": "S",
            "payload": {"obligation_ids": ["O1"]}, "created_at": "2026-08-26T03:00:00Z",
        },
        {
            "event_id": "E2", "sequence": 2, "event_type": "TOOL_RESULT", "source": "TOOL",
            "goal_id": "G", "goal_revision": 1, "snapshot_id": "S",
            "payload": {"evidence_id": "EV1", "result": "PASS", "authoritative": True}, "created_at": "2026-08-26T03:00:01Z",
        },
        {
            "event_id": "E3", "sequence": 3, "event_type": "OBLIGATION_TRANSITION", "source": "HARNESS",
            "goal_id": "G", "goal_revision": 1, "snapshot_id": "S",
            "payload": {"obligation_id": "O1", "to_state": "VERIFIED", "evidence_ids": ["EV1"]}, "created_at": "2026-08-26T03:00:02Z",
        },
    ]
    seq = 4
    if assistant_text:
        events.append({
            "event_id": "E4", "sequence": 4, "event_type": "MODEL_MESSAGE", "source": "WORKER",
            "goal_id": "G", "goal_revision": 1, "snapshot_id": "S",
            "payload": {"text": assistant_text}, "created_at": "2026-08-26T03:00:03Z",
        })
        seq = 5
    stop, candidate, sidecar_value = observer.observe_turn_stopping(
        sequence=seq, session_id="SESSION", turn=1, goal_id="G", goal_revision=1,
        snapshot_id="S", created_at=f"2026-08-26T03:00:0{seq-1}Z", sidecar=sidecar,
    )
    candidate["stop_id"] = "STOP"
    events.append(stop.to_dict())
    value = {
        "schema_version": "0.1", "events": events,
        "evidence_records": [{
            "evidence_id": "EV1", "producer": "validator", "source_class": "DETERMINISTIC_VALIDATOR",
            "goal_id": "G", "goal_revision": 1, "snapshot_id": "S", "obligation_ids": ["O1"],
            "result": "PASS", "scope": ["artifact"], "digest": "1" * 64,
            "created_event_id": "E2", "authoritative": True, "invalidated_by_event_ids": [],
        }],
        "obligations": [{
            "obligation_id": "O1", "kind": "DELIVERABLE", "severity": "HARD", "state": "VERIFIED",
            "evidence_ids": ["EV1"], "last_transition_event_id": "E3",
        }],
        "candidate_stop": candidate, "policy": copy.deepcopy(POLICY),
    }
    if sidecar_value is not None:
        value["candidate_stop_sidecar"] = sidecar_value
    return value


class P2SidecarTests(unittest.TestCase):
    def test_explicit_sidecar_is_bound_and_replayable(self) -> None:
        sidecar = CandidateStopSidecar(
            sidecar_id="SC1", source="TEST_FIXTURE", session_id="SESSION", turn=1,
            goal_id="G", goal_revision=1, snapshot_id="S",
            stop_scope="GOAL_COMPLETION_PROPOSAL", recovery_authority="NOT_APPLICABLE",
            worker_claim="COMPLETE", claims_goal_complete=True, created_at="2026-08-26T03:00:03Z",
        )
        bundle = run_replay(replay_input(sidecar=sidecar))
        self.assertEqual([], verify_replay(bundle))
        self.assertEqual("COMPLETE", bundle["snapshot"]["metadata_status"])
        self.assertEqual(sidecar.digest(), bundle["snapshot"]["sidecar_digest"])
        self.assertEqual("ACCEPT", bundle["verdict"]["accept_decision"])
        self.assertTrue(bundle["verdict"]["deterministic_decision_covered"])
        self.assertFalse(bundle["applied_to_runtime"])

    def test_missing_sidecar_preserves_unknown_and_undetermined(self) -> None:
        bundle = run_replay(replay_input(sidecar=None))
        verdict = bundle["verdict"]
        self.assertEqual("MISSING", verdict["metadata_status"])
        self.assertEqual("UNKNOWN", verdict["stop_scope"])
        self.assertEqual("UNKNOWN", verdict["recovery_authority"])
        self.assertEqual("DO_NOT_ACCEPT", verdict["accept_decision"])
        self.assertEqual("UNDETERMINED", verdict["certification_recommendation"])
        self.assertFalse(verdict["deterministic_decision_covered"])
        self.assertIn("P2.CHK.MISSING_CANDIDATE_STOP_METADATA", {x["check_id"] for x in verdict["findings"]})

    def test_assistant_prose_does_not_fill_missing_sidecar(self) -> None:
        bundle = run_replay(replay_input(sidecar=None, assistant_text="Task complete; everything is done."))
        self.assertEqual("MISSING", bundle["snapshot"]["metadata_status"])
        self.assertEqual("UNKNOWN", bundle["verdict"]["stop_scope"])
        self.assertEqual("DO_NOT_ACCEPT", bundle["verdict"]["accept_decision"])

    def test_sidecar_identity_mismatch_is_rejected(self) -> None:
        sidecar = CandidateStopSidecar(
            sidecar_id="SC1", source="TEST_FIXTURE", session_id="OTHER", turn=1,
            goal_id="G", goal_revision=1, snapshot_id="S", stop_scope="TURN_STOP",
            recovery_authority="NOT_APPLICABLE", worker_claim="TURN_COMPLETE",
            claims_goal_complete=False, created_at="2026-08-26T03:00:03Z",
        )
        with self.assertRaisesRegex(ValueError, "identity does not match"):
            replay_input(sidecar=sidecar)

    def test_frozen_dsh_tool_result_shape_is_read_without_authority_promotion(self) -> None:
        event = DeepSeekHarnessAdapter().normalize_session_event(
            {
                "type": "tool/result",
                "seq": 9,
                "data": {
                    "turn": 1, "step": 1,
                    "message": {"content": [{"type": "tool-result", "isError": False}]},
                },
            },
            sequence=1, goal_id="G", goal_revision=1, snapshot_id="S",
            created_at="2026-08-26T03:00:00Z",
        )
        self.assertIsNotNone(event)
        assert event is not None
        self.assertEqual("PASS", event.payload["reported_status"])
        self.assertFalse(event.payload["authoritative"])


if __name__ == "__main__":
    unittest.main()
