"""Exploratory agreement metrics for P1 annotation feasibility.

These metrics are development diagnostics only. They are not the frozen
confirmatory analysis plan.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Iterable, Mapping, Sequence


def percent_agreement(left: Sequence[Any], right: Sequence[Any]) -> float:
    if len(left) != len(right):
        raise ValueError("agreement inputs must have equal length")
    if not left:
        return float("nan")
    return sum(a == b for a, b in zip(left, right)) / len(left)


def cohens_kappa(left: Sequence[Any], right: Sequence[Any]) -> float:
    if len(left) != len(right):
        raise ValueError("kappa inputs must have equal length")
    if not left:
        return float("nan")
    observed = percent_agreement(left, right)
    left_counts, right_counts = Counter(left), Counter(right)
    n = len(left)
    expected = sum((left_counts[label] / n) * (right_counts[label] / n) for label in set(left_counts) | set(right_counts))
    if expected == 1:
        return 1.0 if observed == 1 else 0.0
    return (observed - expected) / (1 - expected)


def mean_multilabel_jaccard(left: Sequence[Iterable[str]], right: Sequence[Iterable[str]]) -> float:
    if len(left) != len(right):
        raise ValueError("Jaccard inputs must have equal length")
    if not left:
        return float("nan")
    scores: list[float] = []
    for a_values, b_values in zip(left, right):
        a, b = set(a_values), set(b_values)
        union = a | b
        scores.append(1.0 if not union else len(a & b) / len(union))
    return sum(scores) / len(scores)


def pair_annotations(left: Sequence[Mapping[str, Any]], right: Sequence[Mapping[str, Any]]) -> list[tuple[Mapping[str, Any], Mapping[str, Any]]]:
    def key(item: Mapping[str, Any]) -> tuple[str, str]:
        return str(item.get("trajectory_id")), str(item.get("stop_id"))

    left_map, right_map = {key(item): item for item in left}, {key(item): item for item in right}
    if set(left_map) != set(right_map):
        missing_left = sorted(set(right_map) - set(left_map))
        missing_right = sorted(set(left_map) - set(right_map))
        raise ValueError(f"annotation sets differ; missing_left={missing_left}, missing_right={missing_right}")
    return [(left_map[item_key], right_map[item_key]) for item_key in sorted(left_map)]


def agreement_report(left: Sequence[Mapping[str, Any]], right: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    pairs = pair_annotations(left, right)
    l_items, r_items = zip(*pairs) if pairs else ((), ())
    fields = ("outcome_verdict", "process_verdict", "certification_recommendation", "valid_alternative_path")
    report: dict[str, Any] = {"paired_items": len(pairs), "nominal": {}}
    for field in fields:
        l_values = [item[field] for item in l_items]
        r_values = [item[field] for item in r_items]
        report["nominal"][field] = {
            "percent_agreement": percent_agreement(l_values, r_values),
            "cohens_kappa": cohens_kappa(l_values, r_values),
        }
    report["failure_code_jaccard"] = mean_multilabel_jaccard(
        [item["failure_codes"] for item in l_items],
        [item["failure_codes"] for item in r_items],
    )
    report["hard_gate_jaccard"] = mean_multilabel_jaccard(
        [item["hard_gate_codes"] for item in l_items],
        [item["hard_gate_codes"] for item in r_items],
    )
    exact = []
    status = []
    for left_item, right_item in pairs:
        l_loc, r_loc = left_item["first_invalid_transition"], right_item["first_invalid_transition"]
        status.append(l_loc["status"] == r_loc["status"])
        exact.append(l_loc.get("event_id") == r_loc.get("event_id") if l_loc["status"] == r_loc["status"] == "EXACT" else l_loc["status"] == r_loc["status"])
    report["localization_status_agreement"] = sum(status) / len(status) if status else float("nan")
    report["localization_exact_or_status_agreement"] = sum(exact) / len(exact) if exact else float("nan")
    return report
