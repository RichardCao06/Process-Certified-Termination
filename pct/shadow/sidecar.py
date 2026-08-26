"""Explicit, read-only Candidate-Stop metadata sidecar approved by PCT-P2-D12.

The observer binds metadata supplied by a Task or Harness adapter to the
observable ``agent/turn-stopping`` boundary. It never infers stop semantics
from assistant prose and exposes no steering, blocking, resume, or Goal
mutation operation.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .canonical import digest_json, json_clone
from .models import PctEvent, RECOVERY_AUTHORITIES, STOP_SCOPES
from .mutation_guard import assert_payload_is_observable_only

SIDECAR_SOURCES = {"TASK_ADAPTER", "HARNESS_ADAPTER", "TEST_FIXTURE"}
WORKER_CLAIMS = {
    "COMPLETE",
    "TURN_COMPLETE",
    "HUMAN_REQUIRED",
    "BLOCKED",
    "BUDGET_EXHAUSTED",
    "NO_FURTHER_ACTION",
    "OTHER",
    "UNKNOWN",
}


def _required_text(name: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _allowed(name: str, value: Any, allowed: set[str]) -> str:
    text = _required_text(name, value)
    if text not in allowed:
        raise ValueError(f"{name}={text!r} is not allowed")
    return text


@dataclass(frozen=True)
class CandidateStopSidecar:
    sidecar_id: str
    source: str
    session_id: str
    turn: int
    goal_id: str
    goal_revision: int
    snapshot_id: str
    stop_scope: str
    recovery_authority: str
    worker_claim: str
    claims_goal_complete: bool
    created_at: str
    schema_version: str = "0.1"

    def __post_init__(self) -> None:
        if self.schema_version != "0.1":
            raise ValueError("schema_version must be 0.1")
        _required_text("sidecar_id", self.sidecar_id)
        _allowed("source", self.source, SIDECAR_SOURCES)
        _required_text("session_id", self.session_id)
        if not isinstance(self.turn, int) or self.turn < 1:
            raise ValueError("turn must be a positive integer")
        _required_text("goal_id", self.goal_id)
        if not isinstance(self.goal_revision, int) or self.goal_revision < 1:
            raise ValueError("goal_revision must be a positive integer")
        _required_text("snapshot_id", self.snapshot_id)
        scope = _allowed("stop_scope", self.stop_scope, STOP_SCOPES)
        if scope == "UNKNOWN":
            raise ValueError("an explicit sidecar cannot claim UNKNOWN stop_scope")
        _allowed("recovery_authority", self.recovery_authority, RECOVERY_AUTHORITIES)
        _allowed("worker_claim", self.worker_claim, WORKER_CLAIMS)
        if not isinstance(self.claims_goal_complete, bool):
            raise ValueError("claims_goal_complete must be boolean")
        _required_text("created_at", self.created_at)
        if self.claims_goal_complete and self.stop_scope != "GOAL_COMPLETION_PROPOSAL":
            raise ValueError(
                "claims_goal_complete=true requires GOAL_COMPLETION_PROPOSAL"
            )
        if self.stop_scope == "GOAL_COMPLETION_PROPOSAL" and not self.claims_goal_complete:
            raise ValueError(
                "GOAL_COMPLETION_PROPOSAL requires claims_goal_complete=true"
            )

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "CandidateStopSidecar":
        item = cls(
            schema_version=value.get("schema_version", "0.1"),
            sidecar_id=value["sidecar_id"],
            source=value["source"],
            session_id=value["session_id"],
            turn=value["turn"],
            goal_id=value["goal_id"],
            goal_revision=value["goal_revision"],
            snapshot_id=value["snapshot_id"],
            stop_scope=value["stop_scope"],
            recovery_authority=value["recovery_authority"],
            worker_claim=value["worker_claim"],
            claims_goal_complete=value["claims_goal_complete"],
            created_at=value["created_at"],
        )
        supplied = value.get("sidecar_digest")
        if supplied is not None and supplied != item.digest():
            raise ValueError("sidecar_digest mismatch")
        return item

    def material(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "sidecar_id": self.sidecar_id,
            "source": self.source,
            "session_id": self.session_id,
            "turn": self.turn,
            "goal_id": self.goal_id,
            "goal_revision": self.goal_revision,
            "snapshot_id": self.snapshot_id,
            "stop_scope": self.stop_scope,
            "recovery_authority": self.recovery_authority,
            "worker_claim": self.worker_claim,
            "claims_goal_complete": self.claims_goal_complete,
            "created_at": self.created_at,
        }

    def digest(self) -> str:
        return digest_json(self.material())

    def to_dict(self) -> dict[str, Any]:
        value = self.material()
        value["sidecar_digest"] = self.digest()
        return value


class ReadOnlyCandidateStopObserver:
    """Create a Candidate-Stop event from explicit sidecar metadata or absence.

    The method is pure: it returns detached values and never calls the Harness.
    """

    observer_id = "pct-p2-read-only-candidate-stop-observer"
    version = "0.1"

    def observe_turn_stopping(
        self,
        *,
        sequence: int,
        session_id: str,
        turn: int,
        goal_id: str,
        goal_revision: int,
        snapshot_id: str,
        created_at: str,
        sidecar: CandidateStopSidecar | Mapping[str, Any] | None,
    ) -> tuple[PctEvent, dict[str, Any], dict[str, Any] | None]:
        if not isinstance(sequence, int) or sequence < 1:
            raise ValueError("sequence must be a positive integer")
        _required_text("session_id", session_id)
        if not isinstance(turn, int) or turn < 1:
            raise ValueError("turn must be a positive integer")
        _required_text("goal_id", goal_id)
        if not isinstance(goal_revision, int) or goal_revision < 1:
            raise ValueError("goal_revision must be a positive integer")
        _required_text("snapshot_id", snapshot_id)
        _required_text("created_at", created_at)

        bound_sidecar: CandidateStopSidecar | None
        if sidecar is None:
            bound_sidecar = None
            metadata_status = "MISSING"
            stop_scope = "UNKNOWN"
            recovery_authority = "UNKNOWN"
            worker_claim = "UNKNOWN"
            claims_goal_complete = False
            sidecar_id = None
            sidecar_digest = None
        else:
            bound_sidecar = (
                sidecar
                if isinstance(sidecar, CandidateStopSidecar)
                else CandidateStopSidecar.from_dict(sidecar)
            )
            expected = {
                "session_id": session_id,
                "turn": turn,
                "goal_id": goal_id,
                "goal_revision": goal_revision,
                "snapshot_id": snapshot_id,
            }
            actual = {
                "session_id": bound_sidecar.session_id,
                "turn": bound_sidecar.turn,
                "goal_id": bound_sidecar.goal_id,
                "goal_revision": bound_sidecar.goal_revision,
                "snapshot_id": bound_sidecar.snapshot_id,
            }
            if actual != expected:
                raise ValueError(
                    "sidecar identity does not match observed turn-stopping boundary"
                )
            metadata_status = "COMPLETE"
            stop_scope = bound_sidecar.stop_scope
            recovery_authority = bound_sidecar.recovery_authority
            worker_claim = bound_sidecar.worker_claim
            claims_goal_complete = bound_sidecar.claims_goal_complete
            sidecar_id = bound_sidecar.sidecar_id
            sidecar_digest = bound_sidecar.digest()

        payload: dict[str, Any] = {
            "dsh_event_type": "agent/turn-stopping",
            "session_id": session_id,
            "turn": turn,
            "metadata_status": metadata_status,
            "stop_scope": stop_scope,
            "recovery_authority": recovery_authority,
            "worker_claim": worker_claim,
            "claims_goal_complete": claims_goal_complete,
            "observer_id": self.observer_id,
            "observer_version": self.version,
        }
        if sidecar_id is not None:
            payload["sidecar_id"] = sidecar_id
        if sidecar_digest is not None:
            payload["sidecar_digest"] = sidecar_digest
        assert_payload_is_observable_only(payload)

        stable = {
            "sequence": sequence,
            "session_id": session_id,
            "turn": turn,
            "goal_id": goal_id,
            "goal_revision": goal_revision,
            "snapshot_id": snapshot_id,
            "metadata_status": metadata_status,
            "sidecar_digest": sidecar_digest,
        }
        event = PctEvent(
            event_id=f"dsh-turn-stopping-{turn}-{digest_json(stable)[:16]}",
            sequence=sequence,
            event_type="CANDIDATE_STOP",
            source="HARNESS",
            goal_id=goal_id,
            goal_revision=goal_revision,
            snapshot_id=snapshot_id,
            payload=payload,
            created_at=created_at,
        )
        candidate_stop: dict[str, Any] = {
            "stop_id": f"stop-turn-{turn}-{sequence}",
            "stop_event_id": event.event_id,
            "stop_scope": stop_scope,
            "goal_id": goal_id,
            "goal_revision": goal_revision,
            "snapshot_id": snapshot_id,
            "recovery_authority": recovery_authority,
            "metadata_status": metadata_status,
        }
        if sidecar_id is not None:
            candidate_stop["sidecar_id"] = sidecar_id
        if sidecar_digest is not None:
            candidate_stop["sidecar_digest"] = sidecar_digest
        return (
            event,
            candidate_stop,
            json_clone(bound_sidecar.to_dict()) if bound_sidecar is not None else None,
        )
