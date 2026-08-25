#!/usr/bin/env python3
"""Compute exploratory field-level agreement for two P1 JSONL annotation sets."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pct.agreement import agreement_report  # noqa: E402


def read_jsonl(path: Path) -> list[dict]:
    items: list[dict] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_no}: expected object")
        items.append(value)
    return items


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = agreement_report(read_jsonl(args.left), read_jsonl(args.right))
    report["status"] = "exploratory-development-diagnostic"
    report["warning"] = "P1 metrics are not frozen confirmatory thresholds."
    text = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
