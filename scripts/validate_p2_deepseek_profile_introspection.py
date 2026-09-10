#!/usr/bin/env python3
"""Validate the sanitized DeepSeek provider-introspection report."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


FORBIDDEN_TEXT = (
    "Bearer ",
    "sk-",
    "DEEPSEEK_API_KEY=",
    "\"api_key\"",
    "\"authorization\"",
)


def canonical_digest(value: dict, field: str) -> str:
    base = dict(value)
    base.pop(field, None)
    raw = json.dumps(
        base,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    raw = path.read_text(encoding="utf-8")
    for marker in FORBIDDEN_TEXT:
        if marker in raw:
            errors.append(f"sanitized report contains forbidden marker: {marker}")

    report = json.loads(raw)
    if report.get("record_type") != "PCT_P2_DEEPSEEK_PROVIDER_INTROSPECTION":
        errors.append("record_type mismatch")
    if report.get("status") != "PASS":
        errors.append("provider introspection did not pass")
    if report.get("report_digest") != canonical_digest(report, "report_digest"):
        errors.append("report digest mismatch")

    request = report.get("request", {})
    if request.get("method") != "GET" or request.get("endpoint_path") != "/models":
        errors.append("introspection must use GET /models")
    if request.get("requested_model_identifier") != "deepseek-v4-pro":
        errors.append("requested model mismatch")
    for field in ("task_generation", "chat_completion_calls", "worker_trajectory_calls"):
        expected = False if field == "task_generation" else 0
        if request.get(field) != expected:
            errors.append(f"{field} is not zero/false")

    response = report.get("response", {})
    if response.get("http_status") != 200:
        errors.append("HTTP status is not 200")
    if response.get("requested_model_found") is not True:
        errors.append("requested model was not listed")
    if response.get("returned_model_identifier") != "deepseek-v4-pro":
        errors.append("returned model identifier mismatch")
    if "deepseek-v4-pro" not in response.get("available_model_ids", []):
        errors.append("requested model missing from available_model_ids")

    credentials = report.get("credential_handling", {})
    for field in (
        "secret_value_recorded",
        "secret_hash_recorded",
        "authorization_header_recorded",
    ):
        if credentials.get(field) is not False:
            errors.append(f"{field} must be false")

    boundaries = report.get("research_boundaries", {})
    for field in (
        "natural_task_worker_calls",
        "semantic_auditor_calls",
        "reference_packets_opened",
    ):
        if boundaries.get(field) != 0:
            errors.append(f"{field} must be zero")
    for field in ("applied_to_runtime", "online_intervention"):
        if boundaries.get(field) is not False:
            errors.append(f"{field} must be false")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
        nargs="?",
        default="reports/p2/deepseek-provider-introspection-v0.1.json",
    )
    args = parser.parse_args()
    errors = validate(Path(args.path))
    if errors:
        print("P2 DeepSeek provider-introspection validation failed:", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1
    print("P2 DeepSeek provider-introspection validation passed; no task generation or secret material was recorded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
