#!/usr/bin/env python3
"""Replay a P2 Shadow development bundle from observable JSON input."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pct.shadow.canonical import canonical_json  # noqa: E402
from pct.shadow.replay import run_replay, verify_replay  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="Observable replay-input JSON")
    parser.add_argument("--output", type=Path, help="Output bundle path; stdout when omitted")
    parser.add_argument("--verify", action="store_true", help="Treat input as an existing replay bundle and verify it")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    if args.verify:
        errors = verify_replay(payload)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        print("P2 Shadow replay verification passed.")
        return 0
    bundle = run_replay(payload)
    rendered = canonical_json(bundle) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
