"""Observable-only DeepSeek Harness adapter contract for P2 Shadow foundation.

This module normalizes supplied envelopes. It deliberately contains no hook
registration and no runtime mutation API.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .canonical import digest_json, json_clone
from .models import PctEvent
from .mutation_guard import assert_payload_is_observable_only

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


class DeepSeekHarnessAdapter:
    """Pure event normalizer. It cannot steer, block, resume, or mutate Goals."""

    adapter_id = "pct-p2-dsh-observable-adapter"
    version = "0.1-foundation"

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
            result = data.get("result")
            if isinstance(result, Mapping):
                payload["reported_status"] = (
                    "FAIL" if result.get("isError") is True else "PASS"
                )
                # Authority is not inferred from a tool's own success flag.
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
            source_event_id=(
                str(source_event_id) if source_event_id is not None else None
            ),
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
    ) -> tuple[PctEvent, dict[str, Any]]:
        payload = {
            "dsh_event_type": "agent/turn-stopping",
            "turn": turn,
            "worker_claim": worker_claim,
            "stop_scope": stop_scope,
            "recovery_authority": recovery_authority,
            "claims_goal_complete": claims_goal_complete,
        }
        assert_payload_is_observable_only(payload)
        event = PctEvent(
            event_id=f"dsh-turn-stopping-{turn}-{sequence}",
            sequence=sequence,
            event_type="CANDIDATE_STOP",
            source="HARNESS",
            goal_id=goal_id,
            goal_revision=goal_revision,
            snapshot_id=snapshot_id,
            payload=payload,
            created_at=created_at,
        )
        candidate_stop = {
            "stop_id": f"stop-turn-{turn}-{sequence}",
            "stop_event_id": event.event_id,
            "stop_scope": stop_scope,
            "goal_id": goal_id,
            "goal_revision": goal_revision,
            "snapshot_id": snapshot_id,
            "recovery_authority": recovery_authority,
        }
        return event, candidate_stop
