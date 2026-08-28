#!/usr/bin/env python3
"""Recompute the approved P2 20+10 synthetic Shadow regression."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pct.shadow.regression import catalog, run_regression  # noqa: E402


def main() -> int:
    policy = json.loads((ROOT / "governance/p2-shadow-policy-v0.1.json").read_text(encoding="utf-8"))
    report = run_regression(policy)
    catalog_path = ROOT / "data/p2/fixtures/synthetic-regression-catalog-v0.1.json"
    report_path = ROOT / "reports/p2/synthetic-shadow-regression-v0.1.json"
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    catalog_path.write_text(json.dumps(catalog(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("status", "total", "passed", "failed", "live_model_calls", "applied_to_runtime")}, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
