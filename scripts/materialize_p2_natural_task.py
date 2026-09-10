#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pct.pilot.materialize import materialize_task


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize one frozen public P2 natural task without calling a model.")
    parser.add_argument("task_id")
    parser.add_argument("destination")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    materialize_task(args.task_id, args.destination, overwrite=args.overwrite)
    print(f"materialized {args.task_id} at {args.destination}; model calls=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
