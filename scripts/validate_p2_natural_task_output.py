#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pct.pilot.validators import validate_task


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the frozen deterministic validator for one highly verifiable P2 task.")
    parser.add_argument("task_id")
    parser.add_argument("workspace")
    args = parser.parse_args()
    result = validate_task(args.task_id, args.workspace)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
