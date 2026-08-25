"""Policy-gated deterministic Shadow Auditor.

The foundation can always produce replayable findings. It emits P1-style label
fields only after a human-frozen P2 policy is supplied. All outputs remain
non-intervening (`applied_to_runtime=false`).
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .canonical import digest_json, json_clone
from .checks import run_checks
from .event_log import AppendOnlyEventLog
from .evidence import EvidenceLedger
from .models import CandidateStopSnapshot, Finding

REQUIRED_POLICY_DECISIONS = {"PCT-P2-D01", "PCT-P2-D03"}
RECOMMENDATION_PRIORITY = (
    "INCIDENT_ESCALATION",
    "HUMAN_REQUIRED",
    "EVIDENCE_REQUIRED",
    "UNDETERMINED",
    "CONTINUE",
    "BLOCKED",
    "NO_PROGRESS",
)


def _validate_frozen_policy(policy: Mapping[str, Any]) -> None:
    if policy.get("status") != "FROZEN":
        raise ValueError("active Shadow policy must have status=FROZEN")
    if policy.get("online_intervention_authorized") is not False:
        raise ValueError("P2 Shadow policy cannot authorize online intervention")
    approved = set(policy.get("approved_decision_ids", []))
    missing = REQUIRED_POLICY_DECISIONS - approved
    if missing:
        raise ValueError(
            "active Shadow policy is missing required human decisions: "
            + ", ".join(sorted(missing))
        )
    hard_check_ids = policy.get("hard_check_ids")
    if not isinstance(hard_check_ids, list):
        raise ValueError("hard_check_ids must be an array")
    if not isinstance(policy.get("primary_label_layers"), list):
        raise ValueError("primary_label_layers must be an array")


def _deterministic_outcome(
    snapshot: CandidateStopSnapshot,
    ledger: EvidenceLedger,
) -> str:
    relevant = tuple(
        item
        for item in snapshot.obligation_states
        if item.kind in {"OUTCOME", "DELIVERABLE", "INVARIANT"}
    )
    if not relevant:
        return "NOT_APPLICABLE"
    for obligation in relevant:
        failures = ledger.authoritative_failures_for_obligation(
            obligation.obligation_id,
            goal_id=snapshot.goal_id,
            goal_revision=snapshot.goal_revision,
        )
        if failures:
            return "FAIL"
    for obligation in relevant:
        valid_pass = any(
            record.authoritative and record.result == "PASS"
            for record in ledger.valid_records_for_obligation(
                obligation.obligation_id,
                goal_id=snapshot.goal_id,
                goal_revision=snapshot.goal_revision,
            )
        )
        if obligation.state != "VERIFIED" or not valid_pass:
            return "UNKNOWN"
    return "PASS"


def _recommendation(
    hard_findings: tuple[Finding, ...],
    *,
    accept_decision: str,
) -> str:
    if accept_decision == "ACCEPT":
        return "ACCEPT"
    suggestions = {
        finding.suggested_recommendation
        for finding in hard_findings
        if finding.suggested_recommendation
    }
    for value in RECOMMENDATION_PRIORITY:
        if value in suggestions:
            return value
    return "UNDETERMINED"


class DeterministicShadowAuditor:
    def __init__(self, policy: Mapping[str, Any] | None = None) -> None:
        self._policy = json_clone(policy) if policy is not None else None
        if self._policy is not None:
            _validate_frozen_policy(self._policy)

    def audit(
        self,
        *,
        snapshot: CandidateStopSnapshot,
        event_log: AppendOnlyEventLog,
        evidence_ledger: EvidenceLedger,
    ) -> dict[str, Any]:
        findings = run_checks(snapshot, event_log, evidence_ledger)
        base: dict[str, Any] = {
            "schema_version": "0.1",
            "mode": "SHADOW",
            "applied_to_runtime": False,
            "stop_id": snapshot.stop_id,
            "stop_event_id": snapshot.stop_event_id,
            "snapshot_digest": digest_json(snapshot.to_dict()),
            "event_log_digest": event_log.digest(),
            "findings": [finding.to_dict() for finding in findings],
            "citations": {
                "event_ids": sorted(
                    {
                        event_id
                        for finding in findings
                        for event_id in finding.event_ids
                    }
                ),
                "evidence_ids": sorted(
                    {
                        evidence_id
                        for finding in findings
                        for evidence_id in finding.evidence_ids
                    }
                ),
            },
        }
        if self._policy is None:
            base.update(
                {
                    "verdict_status": "POLICY_PENDING",
                    "policy_id": None,
                    "policy_digest": None,
                    "open_decision_ids": [
                        "PCT-P2-D01",
                        "PCT-P2-D02",
                        "PCT-P2-D03",
                        "PCT-P2-D04",
                        "PCT-P2-D05",
                        "PCT-P2-D06",
                        "PCT-P2-D07",
                    ],
                    "labels_emitted": False,
                }
            )
            return base

        hard_ids = set(self._policy.get("hard_check_ids", []))
        hard_findings = tuple(
            finding for finding in findings if finding.check_id in hard_ids
        )
        process_verdict = "FAIL" if hard_findings else "PASS"
        outcome_verdict = _deterministic_outcome(snapshot, evidence_ledger)
        accept_decision = (
            "ACCEPT"
            if process_verdict == "PASS"
            and outcome_verdict in {"PASS", "NOT_APPLICABLE"}
            else "DO_NOT_ACCEPT"
        )
        base.update(
            {
                "verdict_status": "EMITTED",
                "policy_id": self._policy.get("policy_id"),
                "policy_digest": digest_json(self._policy),
                "labels_emitted": True,
                "primary_label_layers": list(
                    self._policy.get("primary_label_layers", [])
                ),
                "human_review_layers": list(
                    self._policy.get("human_review_layers", [])
                ),
                "accept_decision": accept_decision,
                "outcome_verdict": outcome_verdict,
                "process_verdict": process_verdict,
                "stop_scope": snapshot.stop_scope,
                "recovery_authority": snapshot.recovery_authority,
                "certification_recommendation": _recommendation(
                    hard_findings,
                    accept_decision=accept_decision,
                ),
                "hard_check_ids_triggered": [
                    finding.check_id for finding in hard_findings
                ],
                "human_review_required": bool(
                    self._policy.get("human_review_layers")
                ),
            }
        )
        return base
