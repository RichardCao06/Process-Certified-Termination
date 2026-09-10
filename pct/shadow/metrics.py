"""Aggregate non-claiming engineering metrics over frozen Shadow bundles."""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from .replay import verify_replay


def summarize_bundles(bundles: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    items = list(bundles)
    total = len(items)
    complete = sum(
        item.get("snapshot", {}).get("metadata_status") == "COMPLETE" for item in items
    )
    legacy = sum(
        item.get("snapshot", {}).get("metadata_status") == "LEGACY_EXPLICIT" for item in items
    )
    missing = sum(
        item.get("snapshot", {}).get("metadata_status") == "MISSING" for item in items
    )
    covered = sum(
        item.get("verdict", {}).get("deterministic_decision_covered") is True
        for item in items
    )
    replay_equal = sum(not verify_replay(item) for item in items)

    def rate(value: int) -> float | None:
        return round(value / total, 6) if total else None

    return {
        "total_candidate_stops": total,
        "explicit_sidecar_complete": complete,
        "legacy_explicit": legacy,
        "missing_metadata": missing,
        "explicit_sidecar_completeness_rate": rate(complete),
        "metadata_available_rate": rate(complete + legacy),
        "deterministic_decision_covered": covered,
        "deterministic_decision_coverage_rate": rate(covered),
        "deterministic_replay_equal": replay_equal,
        "deterministic_replay_equality_rate": rate(replay_equal),
        "applied_to_runtime_count": sum(
            item.get("applied_to_runtime") is not False for item in items
        ),
    }
