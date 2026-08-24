#!/usr/bin/env python3
"""Compute development-only intra-rater agreement for frozen P1 Pass A/B files."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pct.pilot_analysis import intrarater_report, pair_annotations  # noqa: E402


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_no}: expected JSON object")
        records.append(value)
    return records


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_rows(
    pass_a: list[dict[str, Any]], pass_b: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for left, right in pair_annotations(pass_a, pass_b):
        fit_a = left["first_invalid_transition"]
        fit_b = right["first_invalid_transition"]
        rows.append(
            {
                "trajectory_id": left["trajectory_id"],
                "stop_id": left["stop_id"],
                "pass_a_display_id": left.get("display_id", ""),
                "pass_b_display_id": right.get("display_id", ""),
                "accept_a": left.get(
                    "accept_decision",
                    "ACCEPT"
                    if left.get("certification_recommendation") == "ACCEPT"
                    else "DO_NOT_ACCEPT",
                ),
                "accept_b": right.get(
                    "accept_decision",
                    "ACCEPT"
                    if right.get("certification_recommendation") == "ACCEPT"
                    else "DO_NOT_ACCEPT",
                ),
                "outcome_a": left["outcome_verdict"],
                "outcome_b": right["outcome_verdict"],
                "process_a": left["process_verdict"],
                "process_b": right["process_verdict"],
                "recommendation_a": left["certification_recommendation"],
                "recommendation_b": right["certification_recommendation"],
                "fit_status_a": fit_a["status"],
                "fit_status_b": fit_b["status"],
                "fit_event_a": fit_a.get("event_id", ""),
                "fit_event_b": fit_b.get("event_id", ""),
                "failure_codes_a": ";".join(sorted(left["failure_codes"])),
                "failure_codes_b": ";".join(sorted(right["failure_codes"])),
                "hard_gate_codes_a": ";".join(sorted(left["hard_gate_codes"])),
                "hard_gate_codes_b": ";".join(sorted(right["hard_gate_codes"])),
            }
        )
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pass-a", type=Path, required=True)
    parser.add_argument("--pass-b", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--expected-pairs", type=int, default=12)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pass_a = read_jsonl(args.pass_a)
    pass_b = read_jsonl(args.pass_b)
    report = intrarater_report(pass_a, pass_b)
    if report["paired_items"] != args.expected_pairs:
        raise ValueError(
            f"expected {args.expected_pairs} paired annotations, "
            f"got {report['paired_items']}"
        )
    report["inputs"] = {
        "pass_a_path": str(args.pass_a),
        "pass_a_sha256": sha256(args.pass_a),
        "pass_b_path": str(args.pass_b),
        "pass_b_sha256": sha256(args.pass_b),
    }
    report["interpretation_boundaries"] = [
        "developmental intra-rater feasibility only",
        "not independent inter-rater reliability",
        "not Gold-label validation",
        "does not use Fixture Author Expectations",
        "does not establish automated Auditor accuracy or online PCT effectiveness",
    ]
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    rows = build_rows(pass_a, pass_b)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]) if rows else ["trajectory_id"]
        )
        writer.writeheader()
        writer.writerows(rows)
    print(
        f"Wrote {args.output_json} and {args.output_csv} "
        f"for {report['paired_items']} pairs."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
