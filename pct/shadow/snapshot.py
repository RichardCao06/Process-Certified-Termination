"""Candidate-Stop snapshot construction from frozen observable records."""
from __future__ import annotations

from collections.abc import Iterable, Mapping

from .event_log import AppendOnlyEventLog
from .evidence import EvidenceLedger
from .models import CandidateStopSnapshot, ObligationState


def build_candidate_stop_snapshot(
    *,
    event_log: AppendOnlyEventLog,
    evidence_ledger: EvidenceLedger,
    candidate_stop: Mapping,
    obligations: Iterable[ObligationState | Mapping],
) -> CandidateStopSnapshot:
    stop_event_id = candidate_stop["stop_event_id"]
    stop_event = event_log.event_by_id(stop_event_id)
    if stop_event.event_type != "CANDIDATE_STOP":
        raise ValueError("stop_event_id must refer to a CANDIDATE_STOP event")
    if stop_event.sequence != event_log.last_sequence:
        raise ValueError("Candidate-Stop snapshot must bind to the log tail")
    for field in ("goal_id", "goal_revision", "snapshot_id"):
        if candidate_stop[field] != getattr(stop_event, field):
            raise ValueError(f"candidate_stop {field} does not match stop event")

    metadata_status = candidate_stop.get("metadata_status", "LEGACY_EXPLICIT")
    if stop_event.payload.get("metadata_status", metadata_status) != metadata_status:
        raise ValueError("candidate_stop metadata_status does not match stop event")
    sidecar_id = candidate_stop.get("sidecar_id")
    sidecar_digest = candidate_stop.get("sidecar_digest")
    if sidecar_id != stop_event.payload.get("sidecar_id"):
        if sidecar_id is not None or stop_event.payload.get("sidecar_id") is not None:
            raise ValueError("candidate_stop sidecar_id does not match stop event")
    if sidecar_digest != stop_event.payload.get("sidecar_digest"):
        if sidecar_digest is not None or stop_event.payload.get("sidecar_digest") is not None:
            raise ValueError("candidate_stop sidecar_digest does not match stop event")
    if candidate_stop["stop_scope"] != stop_event.payload.get("stop_scope"):
        raise ValueError("candidate_stop stop_scope does not match stop event")
    if candidate_stop["recovery_authority"] != stop_event.payload.get("recovery_authority"):
        raise ValueError("candidate_stop recovery_authority does not match stop event")

    states = tuple(
        item if isinstance(item, ObligationState) else ObligationState.from_dict(item)
        for item in obligations
    )
    return CandidateStopSnapshot(
        stop_id=candidate_stop["stop_id"],
        stop_event_id=stop_event_id,
        stop_scope=candidate_stop["stop_scope"],
        goal_id=candidate_stop["goal_id"],
        goal_revision=candidate_stop["goal_revision"],
        snapshot_id=candidate_stop["snapshot_id"],
        recovery_authority=candidate_stop["recovery_authority"],
        obligation_states=states,
        evidence_ids=evidence_ledger.current_evidence_ids(
            goal_id=candidate_stop["goal_id"],
            goal_revision=candidate_stop["goal_revision"],
        ),
        last_sequence=event_log.last_sequence,
        event_log_digest=event_log.digest(),
        created_at=stop_event.created_at,
        metadata_status=metadata_status,
        sidecar_id=sidecar_id,
        sidecar_digest=sidecar_digest,
    )
