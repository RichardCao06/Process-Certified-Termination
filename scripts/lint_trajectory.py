#!/usr/bin/env python3
"""Validate and lint one observable PCT trajectory."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pct.validation import lint_trajectory, load_json, validate_trajectory  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trajectory", type=Path)
    args = parser.parse_args()
    data = load_json(args.trajectory)
    structural = validate_trajectory(data)
    result = {
        "trajectory_id": data.get("trajectory_id"),
        "structural_issues": [item.to_dict() for item in structural],
        "candidate_process_findings": [] if structural else [item.to_dict() for item in lint_trajectory(data)],
        "notice": "Deterministic findings are candidates for review, not empirical Gold labels.",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if structural else 0


if __name__ == "__main__":
    raise SystemExit(main())
