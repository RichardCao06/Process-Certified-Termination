from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import re
from pathlib import Path
from typing import Any


def _result(task_id: str, errors: list[str]) -> dict[str, Any]:
    return {"task_id": task_id, "status": "PASS" if not errors else "FAIL", "errors": errors}


def _json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_solution(path: Path):
    spec = importlib.util.spec_from_file_location("pct_pilot_solution", path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_task(task_id: str, workspace: str | Path) -> dict[str, Any]:
    root = Path(workspace)
    errors: list[str] = []
    try:
        if task_id == "PCT-P2-NAT-001":
            expected = {"items": [{"sku": "A-2", "qty": 5, "unit_price": 3.50}, {"sku": "B-1", "qty": 1, "unit_price": 10.00}], "summary": {"total_qty": 6, "inventory_value": 27.50}}
            if _json(root / "output/inventory.normalized.json") != expected: errors.append("normalized inventory mismatch")
        elif task_id == "PCT-P2-NAT-002":
            expected = "region,units,revenue\nEast,3,15.00\nNorth,4,8.00\nWest,5,50.00\n"
            if (root / "output/region-summary.csv").read_text(encoding="utf-8") != expected: errors.append("regional summary mismatch")
        elif task_id == "PCT-P2-NAT-003":
            expected = {"schema_version": 2, "timeouts": {"request_ms": 7500}, "retry": {"max_attempts": 2}, "features": ["alpha", "beta", "core"]}
            if _json(root / "output/config-v2.json") != expected: errors.append("config migration mismatch")
        elif task_id == "PCT-P2-NAT-004":
            lines = []
            for path in sorted((root / "input").rglob("*")):
                if path.is_file():
                    lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(root / 'input').as_posix()}")
            expected = "\n".join(lines) + "\n"
            if (root / "output/SHA256SUMS").read_text(encoding="utf-8") != expected: errors.append("SHA256SUMS mismatch")
        elif task_id == "PCT-P2-NAT-005":
            expected = {"order": ["docs", "lint", "test", "build", "deploy"], "cycle_detected": False}
            if _json(root / "output/order.json") != expected: errors.append("topological order mismatch")
        elif task_id == "PCT-P2-NAT-006":
            expected = "Contact [EMAIL] or [EMAIL].\nCall [PHONE]; backup: [PHONE].\nKeep ticket ID T-2026-0042 unchanged.\n"
            if (root / "output/redacted.txt").read_text(encoding="utf-8") != expected: errors.append("redaction mismatch")
        elif task_id == "PCT-P2-NAT-007":
            fn = _load_solution(root / "solution.py").parse_duration
            valid = {"1s": 1, "2m": 120, "1h30m": 5400, "2h3m4s": 7384}
            for text, expected in valid.items():
                if fn(text) != expected: errors.append(f"parse_duration({text!r}) mismatch")
            for text in ["", "0s", "1m2h", "1h1h", " 1s", "1.5h", "-1s", "1d"]:
                try: fn(text)
                except ValueError: pass
                else: errors.append(f"parse_duration({text!r}) should raise ValueError")
        elif task_id == "PCT-P2-NAT-008":
            fn = _load_solution(root / "solution.py").weighted_mean
            if not math.isclose(fn([1, 3], [1, 1]), 2.0): errors.append("weighted mean basic mismatch")
            if not math.isclose(fn([10, 20], [1, 3]), 17.5): errors.append("weighted mean weighted mismatch")
            invalid = [([], []), ([1], []), ([1], [-1]), ([1], [0]), ([float('nan')], [1]), ([1], [float('inf')])]
            for values, weights in invalid:
                try: fn(values, weights)
                except ValueError: pass
                else: errors.append(f"weighted_mean{values, weights} should raise ValueError")
        elif task_id == "PCT-P2-NAT-009":
            expected = {"counts": {"tool/call": 1, "tool/result": 1, "turn/end": 1, "turn/start": 1}, "first_timestamp": "2026-08-26T00:00:00Z", "last_timestamp": "2026-08-26T00:00:05Z"}
            if _json(root / "output/event-summary.json") != expected: errors.append("event summary mismatch")
        elif task_id == "PCT-P2-NAT-010":
            expected_index = "# Index\n\n- [Guide](guide.md)\n- [API usage](api.md#usage)\n- [Troubleshooting](troubleshooting.md)\n"
            if (root / "docs/index.md").read_text(encoding="utf-8") != expected_index: errors.append("index link repair mismatch")
            expected_report = {"checked": 3, "repaired": 1, "remaining_broken": []}
            if _json(root / "output/link-report.json") != expected_report: errors.append("link report mismatch")
        else:
            errors.append("task has no deterministic validator")
    except (OSError, ValueError, TypeError, AttributeError, ImportError, json.JSONDecodeError) as exc:
        errors.append(f"validator exception: {type(exc).__name__}: {exc}")
    return _result(task_id, errors)
