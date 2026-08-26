"""Typed immutable data objects for the non-intervening P2 Shadow prototype."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping

from .canonical import json_clone

EVENT_TYPES = {
    "GOAL_STATE", "OBSERVATION", "TOOL_CALL", "TOOL_RESULT", "STATE_DELTA",
    "DECISION_CHECKPOINT", "OBLIGATION_TRANSITION", "CANDIDATE_STOP",
    "HUMAN_STEERING", "TURN_START", "TURN_END", "STEP_START", "STEP_END",
    "HUMAN_INPUT", "MODEL_MESSAGE", "GOAL_CHANGE",
}
EVENT_SOURCES = {"HARNESS", "WORKER", "TOOL", "HUMAN", "SYSTEM", "AUDITOR"}
EVIDENCE_SOURCE_CLASSES = {
    "DETERMINISTIC_VALIDATOR", "ENVIRONMENT_OBSERVATION", "TOOL_RESULT",
    "AUDIT_AGENT", "WORKER_CLAIM", "HUMAN_ACCEPTANCE",
}
EVIDENCE_RESULTS = {"PASS", "FAIL", "UNKNOWN"}
OBLIGATION_KINDS = {"OUTCOME", "DELIVERABLE", "INVARIANT", "PROCESS", "SEMANTIC", "EVIDENCE"}
OBLIGATION_SEVERITIES = {"HARD", "MAJOR", "MINOR"}
OBLIGATION_STATES = {"PENDING", "ATTEMPTED", "PROVISIONAL", "VERIFIED", "FAILED", "UNKNOWN"}
STOP_SCOPES = {
    "TURN_STOP", "GOAL_COMPLETION_PROPOSAL", "HUMAN_ESCALATION",
    "NO_FURTHER_ACTION_PROPOSAL", "BLOCKER_PROPOSAL", "BUDGET_STOP",
    "OTHER", "UNKNOWN",
}
RECOVERY_AUTHORITIES = {"SELF_SERVICE", "HUMAN_ONLY", "EXTERNAL_WAIT", "IMPOSSIBLE", "UNKNOWN", "NOT_APPLICABLE"}
METADATA_STATUSES = {"COMPLETE", "MISSING", "LEGACY_EXPLICIT"}
RECOMMENDATIONS = {"ACCEPT", "CONTINUE", "EVIDENCE_REQUIRED", "HUMAN_REQUIRED", "BLOCKED", "NO_PROGRESS", "UNDETERMINED", "INCIDENT_ESCALATION"}


def _required_text(name: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _enum(name: str, value: Any, allowed: set[str]) -> str:
    value = _required_text(name, value)
    if value not in allowed:
        raise ValueError(f"{name}={value!r} is not allowed")
    return value


def _tuple_text(name: str, values: Iterable[Any] | None) -> tuple[str, ...]:
    if values is None:
        return ()
    result = tuple(_required_text(name, value) for value in values)
    if len(result) != len(set(result)):
        raise ValueError(f"{name} contains duplicate values")
    return result


@dataclass(frozen=True)
class PctEvent:
    event_id: str
    sequence: int
    event_type: str
    source: str
    goal_id: str
    goal_revision: int
    snapshot_id: str
    payload: Mapping[str, Any]
    created_at: str
    source_event_id: str | None = None

    def __post_init__(self) -> None:
        _required_text("event_id", self.event_id)
        if not isinstance(self.sequence, int) or self.sequence < 1:
            raise ValueError("sequence must be a positive integer")
        _enum("event_type", self.event_type, EVENT_TYPES)
        _enum("source", self.source, EVENT_SOURCES)
        _required_text("goal_id", self.goal_id)
        if not isinstance(self.goal_revision, int) or self.goal_revision < 1:
            raise ValueError("goal_revision must be a positive integer")
        _required_text("snapshot_id", self.snapshot_id)
        if not isinstance(self.payload, Mapping):
            raise ValueError("payload must be an object")
        _required_text("created_at", self.created_at)
        if self.source_event_id is not None:
            _required_text("source_event_id", self.source_event_id)

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "PctEvent":
        return cls(
            event_id=value["event_id"], sequence=value["sequence"],
            event_type=value["event_type"], source=value["source"],
            goal_id=value["goal_id"], goal_revision=value["goal_revision"],
            snapshot_id=value["snapshot_id"], payload=json_clone(value.get("payload", {})),
            created_at=value["created_at"], source_event_id=value.get("source_event_id"),
        )

    def to_dict(self) -> dict[str, Any]:
        value = {
            "event_id": self.event_id, "sequence": self.sequence,
            "event_type": self.event_type, "source": self.source,
            "goal_id": self.goal_id, "goal_revision": self.goal_revision,
            "snapshot_id": self.snapshot_id, "payload": json_clone(self.payload),
            "created_at": self.created_at,
        }
        if self.source_event_id is not None:
            value["source_event_id"] = self.source_event_id
        return value


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    producer: str
    source_class: str
    goal_id: str
    goal_revision: int
    snapshot_id: str
    obligation_ids: tuple[str, ...]
    result: str
    scope: tuple[str, ...]
    digest: str
    created_event_id: str
    authoritative: bool = False
    invalidated_by_event_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _required_text("evidence_id", self.evidence_id)
        _required_text("producer", self.producer)
        _enum("source_class", self.source_class, EVIDENCE_SOURCE_CLASSES)
        _required_text("goal_id", self.goal_id)
        if not isinstance(self.goal_revision, int) or self.goal_revision < 1:
            raise ValueError("goal_revision must be a positive integer")
        _required_text("snapshot_id", self.snapshot_id)
        if not self.obligation_ids:
            raise ValueError("obligation_ids must not be empty")
        _tuple_text("obligation_ids", self.obligation_ids)
        _enum("result", self.result, EVIDENCE_RESULTS)
        _tuple_text("scope", self.scope)
        _required_text("digest", self.digest)
        _required_text("created_event_id", self.created_event_id)
        _tuple_text("invalidated_by_event_ids", self.invalidated_by_event_ids)
        if not isinstance(self.authoritative, bool):
            raise ValueError("authoritative must be boolean")

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "EvidenceRecord":
        return cls(
            evidence_id=value["evidence_id"], producer=value["producer"],
            source_class=value["source_class"], goal_id=value["goal_id"],
            goal_revision=value["goal_revision"], snapshot_id=value["snapshot_id"],
            obligation_ids=_tuple_text("obligation_ids", value.get("obligation_ids")),
            result=value["result"], scope=_tuple_text("scope", value.get("scope", [])),
            digest=value["digest"], created_event_id=value["created_event_id"],
            authoritative=bool(value.get("authoritative", False)),
            invalidated_by_event_ids=_tuple_text("invalidated_by_event_ids", value.get("invalidated_by_event_ids", [])),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id, "producer": self.producer,
            "source_class": self.source_class, "goal_id": self.goal_id,
            "goal_revision": self.goal_revision, "snapshot_id": self.snapshot_id,
            "obligation_ids": list(self.obligation_ids), "result": self.result,
            "scope": list(self.scope), "digest": self.digest,
            "created_event_id": self.created_event_id, "authoritative": self.authoritative,
            "invalidated_by_event_ids": list(self.invalidated_by_event_ids),
        }


@dataclass(frozen=True)
class ObligationState:
    obligation_id: str
    kind: str
    severity: str
    state: str
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)
    last_transition_event_id: str | None = None

    def __post_init__(self) -> None:
        _required_text("obligation_id", self.obligation_id)
        _enum("kind", self.kind, OBLIGATION_KINDS)
        _enum("severity", self.severity, OBLIGATION_SEVERITIES)
        _enum("state", self.state, OBLIGATION_STATES)
        _tuple_text("evidence_ids", self.evidence_ids)
        if self.last_transition_event_id is not None:
            _required_text("last_transition_event_id", self.last_transition_event_id)

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "ObligationState":
        return cls(
            obligation_id=value["obligation_id"], kind=value["kind"],
            severity=value["severity"], state=value["state"],
            evidence_ids=_tuple_text("evidence_ids", value.get("evidence_ids", [])),
            last_transition_event_id=value.get("last_transition_event_id"),
        )

    def to_dict(self) -> dict[str, Any]:
        value: dict[str, Any] = {
            "obligation_id": self.obligation_id, "kind": self.kind,
            "severity": self.severity, "state": self.state,
            "evidence_ids": list(self.evidence_ids),
        }
        if self.last_transition_event_id is not None:
            value["last_transition_event_id"] = self.last_transition_event_id
        return value


@dataclass(frozen=True)
class CandidateStopSnapshot:
    stop_id: str
    stop_event_id: str
    stop_scope: str
    goal_id: str
    goal_revision: int
    snapshot_id: str
    recovery_authority: str
    obligation_states: tuple[ObligationState, ...]
    evidence_ids: tuple[str, ...]
    last_sequence: int
    event_log_digest: str
    created_at: str
    metadata_status: str = "LEGACY_EXPLICIT"
    sidecar_id: str | None = None
    sidecar_digest: str | None = None

    def __post_init__(self) -> None:
        _required_text("stop_id", self.stop_id)
        _required_text("stop_event_id", self.stop_event_id)
        _enum("stop_scope", self.stop_scope, STOP_SCOPES)
        _required_text("goal_id", self.goal_id)
        if not isinstance(self.goal_revision, int) or self.goal_revision < 1:
            raise ValueError("goal_revision must be a positive integer")
        _required_text("snapshot_id", self.snapshot_id)
        _enum("recovery_authority", self.recovery_authority, RECOVERY_AUTHORITIES)
        _enum("metadata_status", self.metadata_status, METADATA_STATUSES)
        ids = [item.obligation_id for item in self.obligation_states]
        if len(ids) != len(set(ids)):
            raise ValueError("obligation_states contains duplicate obligation IDs")
        _tuple_text("evidence_ids", self.evidence_ids)
        if not isinstance(self.last_sequence, int) or self.last_sequence < 1:
            raise ValueError("last_sequence must be a positive integer")
        _required_text("event_log_digest", self.event_log_digest)
        _required_text("created_at", self.created_at)
        if self.metadata_status == "MISSING":
            if self.stop_scope != "UNKNOWN" or self.recovery_authority != "UNKNOWN":
                raise ValueError("missing metadata must preserve UNKNOWN scope and recovery authority")
            if self.sidecar_id is not None or self.sidecar_digest is not None:
                raise ValueError("missing metadata cannot claim a sidecar binding")
        if self.metadata_status == "COMPLETE":
            _required_text("sidecar_id", self.sidecar_id)
            digest = _required_text("sidecar_digest", self.sidecar_digest)
            if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
                raise ValueError("sidecar_digest must be lowercase SHA-256")

    def to_dict(self) -> dict[str, Any]:
        value = {
            "stop_id": self.stop_id, "stop_event_id": self.stop_event_id,
            "stop_scope": self.stop_scope, "goal_id": self.goal_id,
            "goal_revision": self.goal_revision, "snapshot_id": self.snapshot_id,
            "recovery_authority": self.recovery_authority,
            "obligation_states": [item.to_dict() for item in self.obligation_states],
            "evidence_ids": list(self.evidence_ids), "last_sequence": self.last_sequence,
            "event_log_digest": self.event_log_digest, "created_at": self.created_at,
            "metadata_status": self.metadata_status,
        }
        if self.sidecar_id is not None:
            value["sidecar_id"] = self.sidecar_id
        if self.sidecar_digest is not None:
            value["sidecar_digest"] = self.sidecar_digest
        return value


@dataclass(frozen=True)
class Finding:
    check_id: str
    category: str
    message: str
    event_ids: tuple[str, ...] = field(default_factory=tuple)
    evidence_ids: tuple[str, ...] = field(default_factory=tuple)
    suggested_failure_code: str | None = None
    suggested_recommendation: str | None = None
    enforcement: str = "DESCRIPTIVE_PENDING_P2_D03"

    def __post_init__(self) -> None:
        _required_text("check_id", self.check_id)
        _required_text("category", self.category)
        _required_text("message", self.message)
        _tuple_text("event_ids", self.event_ids)
        _tuple_text("evidence_ids", self.evidence_ids)
        if self.suggested_failure_code is not None:
            _required_text("suggested_failure_code", self.suggested_failure_code)
        if self.suggested_recommendation is not None:
            _enum("suggested_recommendation", self.suggested_recommendation, RECOMMENDATIONS)
        _required_text("enforcement", self.enforcement)

    def to_dict(self) -> dict[str, Any]:
        value: dict[str, Any] = {
            "check_id": self.check_id, "category": self.category,
            "message": self.message, "event_ids": list(self.event_ids),
            "evidence_ids": list(self.evidence_ids), "enforcement": self.enforcement,
        }
        if self.suggested_failure_code is not None:
            value["suggested_failure_code"] = self.suggested_failure_code
        if self.suggested_recommendation is not None:
            value["suggested_recommendation"] = self.suggested_recommendation
        return value
