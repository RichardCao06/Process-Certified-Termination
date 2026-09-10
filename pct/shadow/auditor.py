"""Policy-gated deterministic Shadow Auditor.

The active P2 layer emits labels only under a human-frozen policy. Every output
remains observational: ``mode=SHADOW`` and ``applied_to_runtime=false``.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .canonical import digest_json, json_clone
from .checks import run_checks
from .event_log import AppendOnlyEventLog
from .evidence import EvidenceLedger
from .models import CandidateStopSnapshot, Finding

REQUIRED_POLICY_DECISIONS = {f"PCT-P2-D{i:02d}" for i in range(1, 13)}
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
    if policy.get("mode") != "SHADOW":
        raise ValueError("active Shadow policy must have mode=SHADOW")
    if policy.get("applied_to_runtime") is not False:
        raise ValueError("P2 Shadow policy cannot be applied to runtime")
    if policy.get("online_intervention_authorized") is not False:
        raise ValueError("P2 Shadow policy cannot authorize online intervention")
    if policy.get("worker_behavior_change_authorized") is not False:
        raise ValueError("P2 Shadow policy cannot authorize Worker behavior changes")
    semantic = policy.get("semantic_auditor", {})
    if not isinstance(semantic, Mapping) or semantic.get("enabled") is not False:
        raise ValueError("semantic auditor must remain disabled in this policy")
    approved = set(policy.get("approved_decision_ids", []))
    missing = REQUIRED_POLICY_DECISIONS - approved
    if missing:
        raise ValueError(
            "active Shadow policy is missing required human decisions: "
            + ", ".join(sorted(missing))
        )
    hard_check_ids = policy.get("hard_check_ids")
    descriptive_check_ids = policy.get("descriptive_check_ids")
    if not isinstance(hard_check_ids, list):
        raise ValueError("hard_check_ids must be an array")
    if not isinstance(descriptive_check_ids, list):
        raise ValueError("descriptive_check_ids must be an array")
    overlap = set(hard_check_ids) & set(descriptive_check_ids)
    if overlap:
        raise ValueError("hard and descriptive check registries overlap")
    if not isinstance(policy.get("primary_label_layers"), list):
        raise ValueError("primary_label_layers must be an array")
    if not isinstance(policy.get("human_review_layers"), list):
        raise ValueError("human_review_layers must be an array")


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


def _unresolved_hard(snapshot: CandidateStopSnapshot) -> bool:
    return any(
        item.severity == "HARD" and item.state != "VERIFIED"
        for item in snapshot.obligation_states
    )


def _decision_covered(snapshot: CandidateStopSnapshot) -> bool:
    if snapshot.metadata_status == "MISSING" or snapshot.stop_scope == "UNKNOWN":
        return False
    if (
        snapshot.stop_scope in {"BLOCKER_PROPOSAL", "NO_FURTHER_ACTION_PROPOSAL"}
        and snapshot.recovery_authority == "UNKNOWN"
    ):
        return False
    return True


def _recommendation(
    hard_findings: tuple[Finding, ...],
    *,
    snapshot: CandidateStopSnapshot,
    accept_decision: str,
    outcome_verdict: str,
) -> str:
    if accept_decision == "ACCEPT":
        return "ACCEPT"
    if snapshot.metadata_status == "MISSING" or snapshot.stop_scope == "UNKNOWN":
        return "UNDETERMINED"

    suggestions = {
        finding.suggested_recommendation
        for finding in hard_findings
        if finding.suggested_recommendation
    }
    for value in RECOMMENDATION_PRIORITY:
        if value in suggestions:
            return value

    if snapshot.stop_scope == "HUMAN_ESCALATION" or snapshot.recovery_authority == "HUMAN_ONLY":
        return "HUMAN_REQUIRED"
    if snapshot.recovery_authority in {"EXTERNAL_WAIT", "IMPOSSIBLE"}:
        return "BLOCKED"
    if snapshot.recovery_authority == "UNKNOWN":
        return "UNDETERMINED"
    if outcome_verdict == "UNKNOWN":
        return "EVIDENCE_REQUIRED"
    if outcome_verdict == "FAIL" and snapshot.recovery_authority == "SELF_SERVICE":
        return "CONTINUE"
    if snapshot.stop_scope in {"TURN_STOP", "BUDGET_STOP"}:
        return "UNDETERMINED"
    return "CONTINUE" if snapshot.recovery_authority == "SELF_SERVICE" else "UNDETERMINED"


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
            "metadata_status": snapshot.metadata_status,
            "sidecar_id": snapshot.sidecar_id,
            "sidecar_digest": snapshot.sidecar_digest,
            "citations": {
                "event_ids": sorted(
                    {event_id for finding in findings for event_id in finding.event_ids}
                ),
                "evidence_ids": sorted(
                    {evidence_id for finding in findings for evidence_id in finding.evidence_ids}
                ),
            },
        }
        if self._policy is None:
            base.update(
                {
                    "findings": [finding.to_dict() for finding in findings],
                    "verdict_status": "POLICY_PENDING",
                    "policy_id": None,
                    "policy_digest": None,
                    "open_decision_ids": [f"PCT-P2-D{i:02d}" for i in range(1, 13)],
                    "labels_emitted": False,
                    "deterministic_decision_covered": False,
                }
            )
            return base

        hard_ids = set(self._policy.get("hard_check_ids", []))
        descriptive_ids = set(self._policy.get("descriptive_check_ids", []))
        finding_values: list[dict[str, Any]] = []
        hard_findings: list[Finding] = []
        for finding in findings:
            value = finding.to_dict()
            if finding.check_id in hard_ids:
                value["enforcement"] = "FROZEN_HARD"
                hard_findings.append(finding)
            elif finding.check_id in descriptive_ids:
                value["enforcement"] = "FROZEN_DESCRIPTIVE"
            else:
                value["enforcement"] = "UNREGISTERED_DESCRIPTIVE"
            finding_values.append(value)

        hard_tuple = tuple(hard_findings)
        process_verdict = "FAIL" if hard_tuple else "PASS"
        outcome_verdict = _deterministic_outcome(snapshot, evidence_ledger)
        covered = _decision_covered(snapshot)
        accept_decision = (
            "ACCEPT"
            if covered
            and snapshot.stop_scope == "GOAL_COMPLETION_PROPOSAL"
            and process_verdict == "PASS"
            and outcome_verdict in {"PASS", "NOT_APPLICABLE"}
            and not _unresolved_hard(snapshot)
            else "DO_NOT_ACCEPT"
        )
        base.update(
            {
                "findings": finding_values,
                "verdict_status": "EMITTED",
                "policy_id": self._policy.get("policy_id"),
                "policy_digest": digest_json(self._policy),
                "labels_emitted": True,
                "primary_label_layers": list(self._policy.get("primary_label_layers", [])),
                "human_review_layers": list(self._policy.get("human_review_layers", [])),
                "accept_decision": accept_decision,
                "outcome_verdict": outcome_verdict,
                "process_verdict": process_verdict,
                "stop_scope": snapshot.stop_scope,
                "recovery_authority": snapshot.recovery_authority,
                "certification_recommendation": _recommendation(
                    hard_tuple,
                    snapshot=snapshot,
                    accept_decision=accept_decision,
                    outcome_verdict=outcome_verdict,
                ),
                "hard_check_ids_triggered": [finding.check_id for finding in hard_tuple],
                "human_review_required": bool(self._policy.get("human_review_layers")),
                "deterministic_decision_covered": covered,
            }
        )
        return base
