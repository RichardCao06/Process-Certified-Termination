"""Development-only agreement and disagreement analysis for P1 Pass A / Pass B.

The module deliberately does not read Fixture Author Expectations or decide Gold labels.
It compares two frozen human annotation passes and prepares auditable disagreement data.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


CORE_NOMINAL_FIELDS = (
    "accept_decision",
    "outcome_verdict",
    "process_verdict",
    "certification_recommendation",
    "stop_scope",
    "recovery_authority",
    "valid_alternative_path",
)
MULTILABEL_FIELDS = (
    "certification_effects",
    "control_actions",
    "failure_codes",
    "hard_gate_codes",
)


def _safe_rate(numerator: int, denominator: int) -> float | None:
    return None if denominator == 0 else numerator / denominator


def percent_agreement(left: Sequence[Any], right: Sequence[Any]) -> float | None:
    if len(left) != len(right):
        raise ValueError("agreement inputs must have equal length")
    return _safe_rate(sum(a == b for a, b in zip(left, right)), len(left))


def cohens_kappa(left: Sequence[Any], right: Sequence[Any]) -> float | None:
    if len(left) != len(right):
        raise ValueError("kappa inputs must have equal length")
    if not left:
        return None
    observed = percent_agreement(left, right)
    assert observed is not None
    left_counts, right_counts = Counter(left), Counter(right)
    n = len(left)
    expected = sum(
        (left_counts[label] / n) * (right_counts[label] / n)
        for label in set(left_counts) | set(right_counts)
    )
    if expected == 1:
        return 1.0 if observed == 1 else 0.0
    return (observed - expected) / (1 - expected)


def jaccard(left: Iterable[str], right: Iterable[str]) -> float:
    a, b = set(left), set(right)
    union = a | b
    return 1.0 if not union else len(a & b) / len(union)


def annotation_key(item: Mapping[str, Any]) -> tuple[str, str]:
    trajectory_id = item.get("trajectory_id")
    stop_id = item.get("stop_id")
    if not isinstance(trajectory_id, str) or not trajectory_id:
        raise ValueError("annotation is missing trajectory_id")
    if not isinstance(stop_id, str) or not stop_id:
        raise ValueError(f"{trajectory_id}: annotation is missing stop_id")
    return trajectory_id, stop_id


def _unique_map(
    items: Sequence[Mapping[str, Any]], label: str
) -> dict[tuple[str, str], Mapping[str, Any]]:
    result: dict[tuple[str, str], Mapping[str, Any]] = {}
    for item in items:
        key = annotation_key(item)
        if key in result:
            raise ValueError(f"{label}: duplicate annotation key {key}")
        result[key] = item
    return result


def pair_annotations(
    left: Sequence[Mapping[str, Any]],
    right: Sequence[Mapping[str, Any]],
) -> list[tuple[Mapping[str, Any], Mapping[str, Any]]]:
    left_map = _unique_map(left, "left")
    right_map = _unique_map(right, "right")
    if set(left_map) != set(right_map):
        missing_left = sorted(set(right_map) - set(left_map))
        missing_right = sorted(set(left_map) - set(right_map))
        raise ValueError(
            "annotation sets differ; "
            f"missing_from_left={missing_left}, missing_from_right={missing_right}"
        )
    return [(left_map[key], right_map[key]) for key in sorted(left_map)]


def _fit_locator(item: Mapping[str, Any]) -> tuple[Any, ...]:
    fit = item.get("first_invalid_transition")
    if not isinstance(fit, Mapping):
        raise ValueError(f"{annotation_key(item)}: missing first_invalid_transition")
    status = fit.get("status")
    if status == "EXACT":
        return status, fit.get("event_id")
    if status == "RANGE":
        return status, fit.get("start_event_id"), fit.get("end_event_id")
    return (status,)


def _confidence(item: Mapping[str, Any]) -> float | None:
    fit = item.get("first_invalid_transition")
    if not isinstance(fit, Mapping):
        return None
    value = fit.get("confidence")
    return float(value) if isinstance(value, (int, float)) else None


def _field_value(item: Mapping[str, Any], field: str) -> Any:
    if field == "accept_decision" and field not in item:
        return (
            "ACCEPT"
            if item.get("certification_recommendation") == "ACCEPT"
            else "DO_NOT_ACCEPT"
        )
    if field not in item:
        raise ValueError(f"{annotation_key(item)}: missing required field {field}")
    return item[field]


def classify_disagreement(
    left: Mapping[str, Any], right: Mapping[str, Any]
) -> list[str]:
    categories: list[str] = []
    field_to_category = {
        "accept_decision": "ACCEPT_DECISION",
        "outcome_verdict": "OUTCOME_VERDICT",
        "process_verdict": "PROCESS_VERDICT",
        "certification_recommendation": "RECOMMENDATION",
        "stop_scope": "STOP_SCOPE",
        "recovery_authority": "RECOVERY_AUTHORITY",
        "valid_alternative_path": "VALID_ALTERNATIVE_PATH",
    }
    for field, category in field_to_category.items():
        if _field_value(left, field) != _field_value(right, field):
            categories.append(category)
    for field in MULTILABEL_FIELDS:
        if set(_field_value(left, field)) != set(_field_value(right, field)):
            categories.append(field.upper())
    if left.get("evidence_assessment") != right.get("evidence_assessment"):
        categories.append("EVIDENCE_ASSESSMENT")
    left_fit = left.get("first_invalid_transition", {})
    right_fit = right.get("first_invalid_transition", {})
    if left_fit.get("status") != right_fit.get("status"):
        categories.append("FIT_STATUS")
    elif _fit_locator(left) != _fit_locator(right):
        categories.append("FIT_LOCATOR")
    return categories


@dataclass(frozen=True)
class PairSummary:
    trajectory_id: str
    stop_id: str
    disagreements: tuple[str, ...]
    core_consensus: bool
    strict_consensus: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "trajectory_id": self.trajectory_id,
            "stop_id": self.stop_id,
            "disagreements": list(self.disagreements),
            "core_consensus": self.core_consensus,
            "strict_consensus": self.strict_consensus,
        }


def intrarater_report(
    pass_a: Sequence[Mapping[str, Any]],
    pass_b: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    pairs = pair_annotations(pass_a, pass_b)
    nominal: dict[str, Any] = {}
    for field in CORE_NOMINAL_FIELDS:
        left_values = [_field_value(left, field) for left, _ in pairs]
        right_values = [_field_value(right, field) for _, right in pairs]
        agreements = sum(a == b for a, b in zip(left_values, right_values))
        nominal[field] = {
            "agreement_count": agreements,
            "n": len(pairs),
            "percent_agreement": _safe_rate(agreements, len(pairs)),
            "cohens_kappa": cohens_kappa(left_values, right_values),
        }

    multilabel: dict[str, Any] = {}
    for field in MULTILABEL_FIELDS:
        scores = [
            jaccard(_field_value(left, field), _field_value(right, field))
            for left, right in pairs
        ]
        exact = sum(
            set(_field_value(left, field)) == set(_field_value(right, field))
            for left, right in pairs
        )
        multilabel[field] = {
            "exact_match_count": exact,
            "n": len(pairs),
            "exact_match_rate": _safe_rate(exact, len(pairs)),
            "mean_jaccard": None if not scores else sum(scores) / len(scores),
        }

    fit_status = [
        left["first_invalid_transition"]["status"]
        == right["first_invalid_transition"]["status"]
        for left, right in pairs
    ]
    fit_locator = [_fit_locator(left) == _fit_locator(right) for left, right in pairs]
    invalid_presence = [
        (left["first_invalid_transition"]["status"] != "NONE")
        == (right["first_invalid_transition"]["status"] != "NONE")
        for left, right in pairs
    ]
    hard_presence = [
        bool(left["hard_gate_codes"]) == bool(right["hard_gate_codes"])
        for left, right in pairs
    ]

    pair_summaries: list[PairSummary] = []
    for left, right in pairs:
        disagreements = classify_disagreement(left, right)
        core_consensus = all(
            _field_value(left, field) == _field_value(right, field)
            for field in ("accept_decision", "outcome_verdict", "process_verdict")
        )
        pair_summaries.append(
            PairSummary(
                trajectory_id=str(left["trajectory_id"]),
                stop_id=str(left["stop_id"]),
                disagreements=tuple(disagreements),
                core_consensus=core_consensus,
                strict_consensus=not disagreements,
            )
        )

    confidence_deltas = []
    for left, right in pairs:
        left_conf, right_conf = _confidence(left), _confidence(right)
        if left_conf is not None and right_conf is not None:
            confidence_deltas.append(right_conf - left_conf)

    citation = {
        "pass_a_empty_event_citations": sum(
            not item.get("citations", {}).get("event_ids") for item, _ in pairs
        ),
        "pass_b_empty_event_citations": sum(
            not item.get("citations", {}).get("event_ids") for _, item in pairs
        ),
        "pass_a_empty_evidence_citations": sum(
            not item.get("citations", {}).get("evidence_ids") for item, _ in pairs
        ),
        "pass_b_empty_evidence_citations": sum(
            not item.get("citations", {}).get("evidence_ids") for _, item in pairs
        ),
    }

    return {
        "report_type": "PCT_P1_DEVELOPMENTAL_INTRARATER_AGREEMENT",
        "paired_items": len(pairs),
        "not_independent_inter_rater": True,
        "not_gold": True,
        "nominal": nominal,
        "multilabel": multilabel,
        "fit": {
            "status_agreement_count": sum(fit_status),
            "status_agreement_rate": _safe_rate(sum(fit_status), len(pairs)),
            "locator_agreement_count": sum(fit_locator),
            "locator_agreement_rate": _safe_rate(sum(fit_locator), len(pairs)),
            "invalid_transition_presence_agreement_count": sum(invalid_presence),
            "invalid_transition_presence_agreement_rate": _safe_rate(
                sum(invalid_presence), len(pairs)
            ),
        },
        "hard_gate_presence": {
            "agreement_count": sum(hard_presence),
            "n": len(pairs),
            "agreement_rate": _safe_rate(sum(hard_presence), len(pairs)),
        },
        "consensus": {
            "core_consensus_count": sum(
                item.core_consensus for item in pair_summaries
            ),
            "strict_consensus_count": sum(
                item.strict_consensus for item in pair_summaries
            ),
        },
        "confidence": {
            "paired_count": len(confidence_deltas),
            "mean_pass_b_minus_pass_a": (
                None
                if not confidence_deltas
                else sum(confidence_deltas) / len(confidence_deltas)
            ),
        },
        "citation_capture": citation,
        "pairs": [item.to_dict() for item in pair_summaries],
    }
