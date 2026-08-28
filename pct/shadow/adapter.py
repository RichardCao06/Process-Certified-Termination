"""Observable-only DeepSeek Harness adapter contract for P2 Shadow.

This module normalizes supplied envelopes and delegates Candidate-Stop metadata
binding to the explicit read-only sidecar observer approved by PCT-P2-D12. It
contains no hook registration and no runtime mutation API.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .canonical import digest_json, json_clone
from .models import PctEvent
from .mutation_guard import assert_payload_is_observable_only
from .sidecar import CandidateStopSidecar, ReadOnlyCandidateStopObserver

SESSION_EVENT_MAP = {
    "turn/start": "TURN_START",
    "turn/end": "TURN_END",
    "step/start": "STEP_START",
    "step/end": "STEP_END",
    "user/message": "HUMAN_INPUT",
    "assistant/message": "MODEL_MESSAGE",
    "tool/call": "TOOL_CALL",
    "tool/result": "TOOL_RESULT",
    "goal/change": "GOAL_CHANGE",
}


def _source_for(event_type: str, data: Mapping[str, Any]) -> str:
    if event_type == "assistant/message":
        return "WORKER"
    if event_type in {"tool/call", "tool/result"}:
        return "TOOL"
    if event_type == "user/message":
        message = data.get("message", data)
        if isinstance(message, Mapping):
            source = message.get("source")
            if isinstance(source, Mapping):
                kind = source.get("kind")
                if kind == "user":
                    return "HUMAN"
                if kind in {"plugin", "cron", "goal", "subagent-settled"}:
                    return "SYSTEM"
        return "HARNESS"
    if event_type == "goal/change":
        return "SYSTEM"
    return "HARNESS"


def _tool_result_is_error(data: Mapping[str, Any]) -> bool | None:
    """Read the frozen DSH ToolResultMessage shape without claiming authority."""
    message = data.get("message")
    if isinstance(message, Mapping):
        content = message.get("content")
        if isinstance(content, list):
            for block in content:
                if isinstance(block, Mapping) and block.get("type") == "tool-result":
                    is_error = block.get("isError")
                    if isinstance(is_error, bool):
                        return is_error
    # Legacy synthetic envelope retained only for Foundation fixture replay.
    result = data.get("result")
    if isinstance(result, Mapping) and isinstance(result.get("isError"), bool):
        return bool(result["isError"])
    return None


class DeepSeekHarnessAdapter:
    """Pure event normalizer. It cannot steer, block, resume, or mutate Goals."""

    adapter_id = "pct-p2-dsh-observable-adapter"
    version = "0.2-sidecar"
    frozen_upstream_commit = "b150a551b8d465e31e418e1b2eaf5e79bbb7d28e"

    def normalize_session_event(
        self,
        envelope: Mapping[str, Any],
        *,
        sequence: int,
        goal_id: str,
        goal_revision: int,
        snapshot_id: str,
        created_at: str,
    ) -> PctEvent | None:
        event_type = envelope.get("type")
        if event_type not in SESSION_EVENT_MAP:
            return None
        data = envelope.get("data", {})
        if not isinstance(data, Mapping):
            data = {"raw": data}
        payload: dict[str, Any] = {
            "dsh_event_type": event_type,
            "dsh_data": json_clone(data),
        }
        if event_type == "tool/result":
            is_error = _tool_result_is_error(data)
            if is_error is not None:
                payload["reported_status"] = "FAIL" if is_error else "PASS"
                payload["authoritative"] = False
        assert_payload_is_observable_only(payload)
        source_event_id = envelope.get("id")
        stable_material = {
            "type": event_type,
            "data": data,
            "source_event_id": source_event_id,
            "sequence": sequence,
        }
        return PctEvent(
            event_id=f"dsh-{sequence}-{digest_json(stable_material)[:16]}",
            sequence=sequence,
            event_type=SESSION_EVENT_MAP[event_type],
            source=_source_for(str(event_type), data),
            goal_id=goal_id,
            goal_revision=goal_revision,
            snapshot_id=snapshot_id,
            payload=payload,
            created_at=created_at,
            source_event_id=str(source_event_id) if source_event_id is not None else None,
        )

    def normalize_turn_stopping(
        self,
        *,
        turn: int,
        sequence: int,
        goal_id: str,
        goal_revision: int,
        snapshot_id: str,
        created_at: str,
        stop_scope: str,
        recovery_authority: str,
        worker_claim: str = "NO_FURTHER_ACTION",
        claims_goal_complete: bool = False,
        session_id: str = "legacy-explicit-session",
        sidecar_id: str | None = None,
    ) -> tuple[PctEvent, dict[str, Any]]:
        """Backward-compatible explicit API, now materialized as a sidecar.

        Values are caller-supplied state, never inferred from assistant prose.
        New integrations should call :class:`ReadOnlyCandidateStopObserver`
        directly so missing metadata can be represented explicitly.
        """
        sidecar = CandidateStopSidecar(
            sidecar_id=sidecar_id or f"sidecar-turn-{turn}-{sequence}",
            source="HARNESS_ADAPTER",
            session_id=session_id,
            turn=turn,
            goal_id=goal_id,
            goal_revision=goal_revision,
            snapshot_id=snapshot_id,
            stop_scope=stop_scope,
            recovery_authority=recovery_authority,
            worker_claim=worker_claim,
            claims_goal_complete=claims_goal_complete,
            created_at=created_at,
        )
        event, candidate_stop, _ = ReadOnlyCandidateStopObserver().observe_turn_stopping(
            sequence=sequence,
            session_id=session_id,
            turn=turn,
            goal_id=goal_id,
            goal_revision=goal_revision,
            snapshot_id=snapshot_id,
            created_at=created_at,
            sidecar=sidecar,
        )
        return event, candidate_stop
