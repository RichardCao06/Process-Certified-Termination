"""Deterministic replay entry point for P2 Shadow development bundles."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .auditor import DeterministicShadowAuditor
from .canonical import digest_json, json_clone
from .event_log import AppendOnlyEventLog
from .evidence import EvidenceLedger
from .mutation_guard import assert_payload_is_observable_only
from .snapshot import build_candidate_stop_snapshot


def run_replay(inputs: Mapping[str, Any]) -> dict[str, Any]:
    """Replay one Candidate Stop without invoking the Worker or external tools."""
    assert_payload_is_observable_only(inputs)
    event_log = AppendOnlyEventLog.from_dicts(inputs.get("events", []))
    evidence_ledger = EvidenceLedger.from_dicts(
        inputs.get("evidence_records", [])
    )
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
        "verdict": verdict,
        "verdict_digest": digest_json(verdict),
    }
    bundle["bundle_digest"] = digest_json(
        {
            key: value
            for key, value in bundle.items()
            if key != "bundle_digest"
        }
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
    if replayed.get("snapshot") != bundle.get("snapshot"):
        errors.append("snapshot mismatch")
    if replayed.get("verdict") != bundle.get("verdict"):
        errors.append("verdict mismatch")
    return errors
