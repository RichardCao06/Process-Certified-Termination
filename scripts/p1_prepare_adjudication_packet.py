#!/usr/bin/env python3
"""Prepare a non-Gold A/B disagreement packet before author expectations are opened."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from pct.pilot_analysis import classify_disagreement, pair_annotations


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_no}: expected object")
        result.append(value)
    return result


def load_episodes(path: Path) -> dict[str, dict[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    items = value.get("episodes") if isinstance(value, dict) else value
    if not isinstance(items, list):
        raise ValueError("episodes input must be a list or an object with episodes")
    result: dict[str, dict[str, Any]] = {}
    for wrapper in items:
        if not isinstance(wrapper, dict):
            raise ValueError("episode record must be an object")
        episode = wrapper.get("episode", wrapper)
        if not isinstance(episode, dict):
            raise ValueError("episode payload must be an object")
        trajectory_id = wrapper.get("trajectory_id", episode.get("trajectory_id"))
        if not isinstance(trajectory_id, str) or not trajectory_id:
            raise ValueError("episode is missing trajectory_id")
        if trajectory_id in result:
            raise ValueError(f"duplicate episode {trajectory_id}")
        result[trajectory_id] = episode
    return result


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=Path, required=True)
    parser.add_argument("--pass-a", type=Path, required=True)
    parser.add_argument("--pass-b", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    episodes = load_episodes(args.episodes)
    pass_a = read_jsonl(args.pass_a)
    pass_b = read_jsonl(args.pass_b)
    pairs = pair_annotations(pass_a, pass_b)
    cases: list[dict[str, Any]] = []
    for left, right in pairs:
        trajectory_id = str(left["trajectory_id"])
        if trajectory_id not in episodes:
            raise ValueError(f"missing observable episode {trajectory_id}")
        disagreements = classify_disagreement(left, right)
        cases.append(
            {
                "trajectory_id": trajectory_id,
                "stop_id": left["stop_id"],
                "disagreement_types": disagreements,
                "requires_adjudication": bool(disagreements),
                "episode": episodes[trajectory_id],
                "pass_a_annotation": left,
                "pass_b_annotation": right,
                "adjudication": {
                    "status": (
                        "PENDING_HUMAN_ADJUDICATION"
                        if disagreements
                        else "CONSENSUS_NO_ADJUDICATION_REQUIRED"
                    ),
                    "selected_annotation": None,
                    "retained_ambiguity": None,
                    "reason_codes": [],
                    "rationale": "",
                },
            }
        )
    packet = {
        "packet_type": "PCT_P1_PRE_AUTHOR_OPENING_ADJUDICATION_PACKET",
        "not_gold": True,
        "fixture_author_expectations_included": False,
        "case_level_semantic_feedback_before_pass_b": False,
        "input_hashes": {
            "episodes_sha256": digest(args.episodes),
            "pass_a_sha256": digest(args.pass_a),
            "pass_b_sha256": digest(args.pass_b),
        },
        "case_count": len(cases),
        "disagreement_case_count": sum(
            item["requires_adjudication"] for item in cases
        ),
        "cases": cases,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote {args.output} with {len(cases)} paired cases.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
