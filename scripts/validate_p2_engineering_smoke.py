#!/usr/bin/env python3
"""Validate a persisted D19 smoke report; absence remains an authorized-not-run state."""
from __future__ import annotations
import hashlib, json, sys
from copy import deepcopy
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/p2/engineering-smoke-run-v0.2.json"

def digest(value: dict, field: str) -> str:
    item = deepcopy(value); item.pop(field, None)
    return hashlib.sha256(json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def main() -> int:
    if not REPORT.is_file():
        print("P2 D19 smoke report not present: authorized-not-run state is valid.")
        return 0
    value = json.loads(REPORT.read_text(encoding="utf-8"))
    errors = []
    if value.get("schema_version") != "0.2" or value.get("record_type") != "PCT_P2_ENGINEERING_SMOKE_REPORT": errors.append("report identity mismatch")
    if value.get("report_digest") != digest(value, "report_digest"): errors.append("report digest mismatch")
    if len(value.get("runs", [])) > 2: errors.append("more than two smoke trajectories")
    boundaries = value.get("research_boundaries", {})
    expected = {"primary_schedule_runs": 0, "reference_packets_opened": 0, "semantic_auditor_calls": 0, "applied_to_runtime": False, "online_intervention": False, "raw_model_or_tool_content_persisted": False}
    for key, expected_value in expected.items():
        if boundaries.get(key) != expected_value: errors.append(f"boundary mismatch: {key}")
    for run in value.get("runs", []):
        if run.get("excluded_from_primary_schedule") is not True: errors.append("run entered primary schedule")
        if run.get("driver", {}).get("secret_output_detected") is not False: errors.append("secret output detected")
        if run.get("runtime_tool_catalog", {}).get("expected") != ["edit", "read", "write"]: errors.append("runtime tool catalog mismatch")
    if errors:
        print("P2 D19 smoke result validation failed:", file=sys.stderr)
        for error in errors: print(f" - {error}", file=sys.stderr)
        return 1
    print(f"P2 D19 smoke report preserved: status={value.get('status')}; runs={len(value.get('runs', []))}; primary_schedule_runs=0.")
    return 0
if __name__ == "__main__": raise SystemExit(main())
