"""Static and payload guards that keep the P2 foundation non-intervening."""
from __future__ import annotations

import ast
from collections.abc import Mapping, Sequence
from typing import Any

FORBIDDEN_RUNTIME_CALL_NAMES = {
    "steer",
    "block_turn",
    "block_stop",
    "resume_agent",
    "continue_agent",
    "set_goal_state",
    "mark_goal_complete",
    "mark_goal_failed",
    "mutate_goal",
    "apply_shadow_verdict",
}
FORBIDDEN_RUNTIME_INPUT_KEYS = {
    "gold_label",
    "gold_labels",
    "reference_truth",
    "fixture_author_expectation",
    "fixture_author_expectations",
    "hidden_evaluator",
    "hidden_evaluator_output",
    "sealed_test",
    "sealed_data",
    "human_annotation",
    "human_annotations",
    "pass_a_label",
    "pass_b_label",
}


def find_forbidden_calls(source: str) -> list[tuple[int, str]]:
    """Find direct calls to mutation-like functions or methods in Python source."""
    tree = ast.parse(source)
    findings: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name: str | None = None
        if isinstance(node.func, ast.Name):
            name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            name = node.func.attr
        if name in FORBIDDEN_RUNTIME_CALL_NAMES:
            findings.append((getattr(node, "lineno", 0), name))
    return findings


def forbidden_payload_paths(value: Any, path: str = "$") -> list[str]:
    """Return paths containing prohibited hidden/reference input keys."""
    findings: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            child = f"{path}.{key_text}"
            if key_text.lower() in FORBIDDEN_RUNTIME_INPUT_KEYS:
                findings.append(child)
            findings.extend(forbidden_payload_paths(item, child))
    elif isinstance(value, Sequence) and not isinstance(
        value, (str, bytes, bytearray)
    ):
        for index, item in enumerate(value):
            findings.extend(forbidden_payload_paths(item, f"{path}[{index}]"))
    return findings


def assert_payload_is_observable_only(value: Any) -> None:
    paths = forbidden_payload_paths(value)
    if paths:
        raise ValueError(
            "runtime Shadow input contains forbidden hidden/reference fields: "
            + ", ".join(paths)
        )
