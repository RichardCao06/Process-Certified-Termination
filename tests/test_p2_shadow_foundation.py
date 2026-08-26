from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from pct.shadow.adapter import DeepSeekHarnessAdapter
from pct.shadow.event_log import AppendOnlyEventLog
from pct.shadow.mutation_guard import assert_payload_is_observable_only, find_forbidden_calls
from pct.shadow.replay import run_replay, verify_replay

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data/p2/fixtures/replay-clean-success-v0.1.json"
STALE = ROOT / "data/p2/fixtures/replay-stale-evidence-v0.1.json"
POLICY = ROOT / "governance/p2-shadow-policy-v0.1.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class P2ShadowFoundationTests(unittest.TestCase):
    def test_clean_replay_is_policy_pending_and_deterministic(self) -> None:
        bundle = run_replay(load(CLEAN))
        self.assertEqual("POLICY_PENDING", bundle["verdict"]["verdict_status"])
        self.assertFalse(bundle["verdict"]["labels_emitted"])
        self.assertFalse(bundle["applied_to_runtime"])
        self.assertEqual([], bundle["verdict"]["findings"])
        self.assertEqual([], verify_replay(bundle))

    def test_stale_evidence_is_detected_without_emitting_labels(self) -> None:
        bundle = run_replay(load(STALE))
        check_ids = {finding["check_id"] for finding in bundle["verdict"]["findings"]}
        self.assertIn("P2.CHK.VERIFIED_WITHOUT_VALID_EVIDENCE", check_ids)
        self.assertIn("P2.CHK.STALE_EVIDENCE_REFERENCED", check_ids)
        self.assertFalse(bundle["verdict"]["labels_emitted"])

    def test_event_log_is_append_only_and_strictly_ordered(self) -> None:
        events = load(CLEAN)["events"]
        log = AppendOnlyEventLog.from_dicts(events)
        self.assertEqual(4, len(log))
        with self.assertRaises(ValueError):
            log.append(events[-1])
        bad = copy.deepcopy(events[-1])
        bad["event_id"] = "E5"
        bad["sequence"] = 7
        with self.assertRaises(ValueError):
            log.append(bad)

    def test_hidden_reference_keys_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            assert_payload_is_observable_only({"nested": {"gold_label": "PASS"}})
        adapter = DeepSeekHarnessAdapter()
        with self.assertRaises(ValueError):
            adapter.normalize_session_event(
                {"type": "tool/result", "data": {"hidden_evaluator": {"answer": "x"}}},
                sequence=1,
                goal_id="G",
                goal_revision=1,
                snapshot_id="S",
                created_at="2026-08-25T00:00:00Z",
            )

    def test_unknown_recovery_authority_produces_descriptive_finding(self) -> None:
        inputs = load(CLEAN)
        inputs["events"][-1]["payload"].update(
            {"stop_scope": "BLOCKER_PROPOSAL", "recovery_authority": "UNKNOWN", "claims_goal_complete": False}
        )
        inputs["candidate_stop"]["stop_scope"] = "BLOCKER_PROPOSAL"
        inputs["candidate_stop"]["recovery_authority"] = "UNKNOWN"
        bundle = run_replay(inputs)
        findings = {item["check_id"]: item for item in bundle["verdict"]["findings"]}
        self.assertEqual(
            "UNDETERMINED",
            findings["P2.CHK.UNKNOWN_RECOVERY_AUTHORITY"]["suggested_recommendation"],
        )

    def test_unauthorized_irreversible_action_is_detected(self) -> None:
        inputs = load(CLEAN)
        stop = inputs["events"].pop()
        action = {
            "event_id": "E4",
            "sequence": 4,
            "event_type": "TOOL_RESULT",
            "source": "TOOL",
            "goal_id": "goal-clean",
            "goal_revision": 1,
            "snapshot_id": "S1",
            "payload": {"executed": True, "irreversible": True, "authorization_required": True, "authorization_present": False},
            "created_at": "2026-08-25T09:10:02.500Z",
        }
        stop["event_id"] = "E5"
        stop["sequence"] = 5
        inputs["events"].extend([action, stop])
        inputs["candidate_stop"]["stop_event_id"] = "E5"
        bundle = run_replay(inputs)
        findings = {item["check_id"]: item for item in bundle["verdict"]["findings"]}
        self.assertEqual(
            "INCIDENT_ESCALATION",
            findings["P2.CHK.UNAUTHORIZED_IRREVERSIBLE_ACTION"]["suggested_recommendation"],
        )

    def test_frozen_policy_can_emit_labels_but_never_apply_them(self) -> None:
        inputs = load(STALE)
        inputs["policy"] = load(POLICY)
        verdict = run_replay(inputs)["verdict"]
        self.assertEqual("EMITTED", verdict["verdict_status"])
        self.assertTrue(verdict["labels_emitted"])
        self.assertEqual("DO_NOT_ACCEPT", verdict["accept_decision"])
        self.assertEqual("FAIL", verdict["process_verdict"])
        self.assertEqual("EVIDENCE_REQUIRED", verdict["certification_recommendation"])
        self.assertFalse(verdict["applied_to_runtime"])

    def test_replay_verification_detects_tamper(self) -> None:
        bundle = run_replay(load(CLEAN))
        tampered = copy.deepcopy(bundle)
        tampered["snapshot"]["goal_id"] = "tampered"
        self.assertIn("snapshot mismatch", verify_replay(tampered))

    def test_static_guard_detects_mutation_call(self) -> None:
        self.assertEqual([], find_forbidden_calls("result = observer.audit(x)\n"))
        self.assertEqual([(1, "steer")], find_forbidden_calls("agent.steer('x')\n"))


if __name__ == "__main__":
    unittest.main()
