"""Deterministic replay entry point for P2 Shadow development bundles."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .auditor import DeterministicShadowAuditor
from .canonical import digest_json, json_clone
from .event_log import AppendOnlyEventLog
from .evidence import EvidenceLedger
from .mutation_guard import assert_payload_is_observable_only
from .sidecar import CandidateStopSidecar
from .snapshot import build_candidate_stop_snapshot


def _validate_sidecar_binding(inputs: Mapping[str, Any]) -> None:
    candidate = inputs["candidate_stop"]
    status = candidate.get("metadata_status", "LEGACY_EXPLICIT")
    raw_sidecar = inputs.get("candidate_stop_sidecar")
    if status == "COMPLETE":
        if not isinstance(raw_sidecar, Mapping):
            raise ValueError("COMPLETE Candidate Stop requires candidate_stop_sidecar")
        sidecar = CandidateStopSidecar.from_dict(raw_sidecar)
        if candidate.get("sidecar_id") != sidecar.sidecar_id:
            raise ValueError("candidate_stop sidecar_id mismatch")
        if candidate.get("sidecar_digest") != sidecar.digest():
            raise ValueError("candidate_stop sidecar_digest mismatch")
        for field in ("goal_id", "goal_revision", "snapshot_id", "stop_scope", "recovery_authority"):
            if candidate.get(field) != getattr(sidecar, field):
                raise ValueError(f"candidate_stop {field} does not match sidecar")
        stop_event = next(
            (item for item in inputs.get("events", []) if item.get("event_id") == candidate.get("stop_event_id")),
            None,
        )
        if not isinstance(stop_event, Mapping):
            raise ValueError("candidate_stop stop_event_id is absent from events")
        payload = stop_event.get("payload", {})
        if not isinstance(payload, Mapping):
            raise ValueError("Candidate-Stop event payload must be an object")
        if payload.get("session_id") != sidecar.session_id or payload.get("turn") != sidecar.turn:
            raise ValueError("sidecar identity does not match Candidate-Stop event")
    elif raw_sidecar is not None:
        raise ValueError("candidate_stop_sidecar is only valid with metadata_status=COMPLETE")
    if status == "MISSING":
        if candidate.get("stop_scope") != "UNKNOWN":
            raise ValueError("missing sidecar must preserve stop_scope=UNKNOWN")
        if candidate.get("recovery_authority") != "UNKNOWN":
            raise ValueError("missing sidecar must preserve recovery_authority=UNKNOWN")


def run_replay(inputs: Mapping[str, Any]) -> dict[str, Any]:
    """Replay one Candidate Stop without invoking the Worker or external tools."""
    assert_payload_is_observable_only(inputs)
    _validate_sidecar_binding(inputs)
    event_log = AppendOnlyEventLog.from_dicts(inputs.get("events", []))
    evidence_ledger = EvidenceLedger.from_dicts(inputs.get("evidence_records", []))
    snapshot = build_candidate_stop_snapshot(
        event_log=event_log,
        evidence_ledger=evidence_ledger,
        candidate_stop=inputs["candidate_stop"],
        obligations=inputs.get("obligations", []),
    )
    policy = inputs.get("policy")
    auditor = DeterministicShadowAuditor(policy)
    verdict = auditor.audit(
        snapshot=snapshot,
        event_log=event_log,
        evidence_ledger=evidence_ledger,
    )
    frozen_inputs = json_clone(inputs)
    bundle = {
        "schema_version": "0.1",
        "record_type": "PCT_P2_SHADOW_REPLAY_BUNDLE",
        "mode": "SHADOW",
        "applied_to_runtime": False,
        "inputs": frozen_inputs,
        "input_digest": digest_json(frozen_inputs),
        "event_log_digest": event_log.digest(),
        "snapshot": snapshot.to_dict(),
        "snapshot_digest": digest_json(snapshot.to_dict()),
        "candidate_stop_metadata": {
            "metadata_status": snapshot.metadata_status,
            "sidecar_id": snapshot.sidecar_id,
            "sidecar_digest": snapshot.sidecar_digest,
        },
        "verdict": verdict,
        "verdict_digest": digest_json(verdict),
    }
    bundle["bundle_digest"] = digest_json(
        {key: value for key, value in bundle.items() if key != "bundle_digest"}
    )
    return bundle


def verify_replay(bundle: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if bundle.get("record_type") != "PCT_P2_SHADOW_REPLAY_BUNDLE":
        errors.append("record_type mismatch")
        return errors
    try:
        replayed = run_replay(bundle["inputs"])
    except Exception as exc:  # pragma: no cover - error text is returned
        errors.append(f"replay failed: {exc}")
        return errors
    for field in (
        "input_digest",
        "event_log_digest",
        "snapshot_digest",
        "verdict_digest",
        "bundle_digest",
    ):
        if replayed.get(field) != bundle.get(field):
            errors.append(f"{field} mismatch")
    for field in ("snapshot", "candidate_stop_metadata", "verdict"):
        if replayed.get(field) != bundle.get(field):
            errors.append(f"{field} mismatch")
    return errors
