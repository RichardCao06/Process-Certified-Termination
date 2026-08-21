"""Prototype mapping from selected DeepSeek Harness events to PCT canonical events.

This module is development-only. It preserves observable facts but does not
certify their semantic meaning and does not install a runtime hook.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

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


def _stable_id(prefix: str, payload: Mapping[str, Any]) -> str:
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()[:16]
    return f"{prefix}-{digest}"


def _source_for_session_event(event_type: str, data: Mapping[str, Any]) -> str:
    if event_type == "user/message":
        message = data.get("message", data)
        source = message.get("source") if isinstance(message, Mapping) else None
        kind = source.get("kind") if isinstance(source, Mapping) else None
        if kind == "user":
            return "HUMAN"
        if kind in {"plugin", "cron", "goal", "subagent-settled"}:
            return "SYSTEM"
        return "HARNESS"
    if event_type == "assistant/message":
        return "WORKER"
    if event_type in {"tool/call", "tool/result"}:
        return "TOOL"
    if event_type == "goal/change":
        return "SYSTEM"
    return "HARNESS"


def map_session_event(
    envelope: Mapping[str, Any],
    *,
    sequence: int,
    goal_revision: int,
    snapshot_id: str | None = None,
) -> dict[str, Any] | None:
    """Map one durable session event, returning ``None`` for unsupported types."""
    event_type = envelope.get("type")
    if event_type not in SESSION_EVENT_MAP:
        return None
    data = envelope.get("data", {})
    if not isinstance(data, Mapping):
        data = {"raw": data}
    payload = {"dsh_event_type": event_type, "dsh_data": dict(data)}
    if event_type == "tool/result":
        result = data.get("result")
        if isinstance(result, Mapping):
            payload["status"] = "FAIL" if result.get("isError") is True else "PASS"
            payload["authoritative"] = False
    event = {
        "event_id": _stable_id(f"dsh-{sequence}", {"type": event_type, "data": data}),
        "sequence": sequence,
        "event_type": SESSION_EVENT_MAP[event_type],
        "source": _source_for_session_event(event_type, data),
        "goal_revision": goal_revision,
        "payload": payload,
    }
    if snapshot_id is not None:
        event["snapshot_id"] = snapshot_id
    return event


def map_turn_stopping(
    *,
    turn: int,
    sequence: int,
    goal_revision: int,
    snapshot_id: str,
    worker_claim: str = "NO_FURTHER_ACTION",
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Create a canonical Candidate Stop from ``agent/turn-stopping``."""
    event = {
        "event_id": f"dsh-turn-stopping-{turn}-{sequence}",
        "sequence": sequence,
        "event_type": "CANDIDATE_STOP",
        "source": "HARNESS",
        "goal_revision": goal_revision,
        "snapshot_id": snapshot_id,
        "payload": {
            "dsh_event_type": "agent/turn-stopping",
            "turn": turn,
            "worker_claim": worker_claim,
        },
    }
    stop = {
        "stop_id": f"stop-turn-{turn}-{sequence}",
        "event_id": event["event_id"],
        "goal_revision": goal_revision,
        "snapshot_id": snapshot_id,
        "worker_claim": worker_claim,
        "harness_stop_reason": "DeepSeek Harness reached agent/turn-stopping with no pending next-step input",
    }
    return event, stop
