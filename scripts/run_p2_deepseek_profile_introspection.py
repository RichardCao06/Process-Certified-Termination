#!/usr/bin/env python3
"""Perform a read-only DeepSeek model-list introspection without task generation."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


FORBIDDEN_OUTPUT_KEYS = {
    "api_key",
    "apikey",
    "authorization",
    "cookie",
    "secret",
    "token_value",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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


def parse_model_listing(payload: object, requested_model: str) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("model-list response must be a JSON object")
    if payload.get("object") != "list":
        raise ValueError("model-list response object must equal 'list'")
    raw_data = payload.get("data")
    if not isinstance(raw_data, list):
        raise ValueError("model-list response data must be an array")

    models: list[dict[str, str]] = []
    for item in raw_data:
        if not isinstance(item, dict):
            raise ValueError("each model-list item must be an object")
        model_id = item.get("id")
        object_type = item.get("object")
        owner = item.get("owned_by")
        if not all(isinstance(value, str) and value for value in (model_id, object_type, owner)):
            raise ValueError("model-list item is missing id/object/owned_by")
        models.append(
            {
                "id": model_id,
                "object": object_type,
                "owned_by": owner,
            }
        )

    models.sort(key=lambda item: item["id"])
    match = next((item for item in models if item["id"] == requested_model), None)
    return {
        "models": models,
        "available_model_ids": [item["id"] for item in models],
        "requested_model_found": match is not None,
        "requested_model_record": match,
    }


def get_model_listing(base_url: str, api_key: str, timeout_seconds: int) -> tuple[int, object]:
    endpoint = base_url.rstrip("/") + "/models"
    request = Request(
        endpoint,
        method="GET",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "User-Agent": "PCT-P2-read-only-profile-introspection/0.1",
        },
    )
    with urlopen(request, timeout=timeout_seconds) as response:
        status = int(getattr(response, "status", 200))
        payload = json.loads(response.read().decode("utf-8"))
    return status, payload


def assert_no_secret_keys(value: object, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).strip().lower()
            if normalized in FORBIDDEN_OUTPUT_KEYS:
                raise ValueError(f"forbidden secret-bearing key at {path}.{key}")
            assert_no_secret_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_no_secret_keys(child, f"{path}[{index}]")


def build_report(
    *,
    requested_model: str,
    base_url: str,
    http_status: int,
    parsed: dict,
    profile_path: Path,
    prompt_path: Path,
    tool_catalog_path: Path,
    source_mode: str,
) -> dict:
    report = {
        "schema_version": "0.1",
        "record_type": "PCT_P2_DEEPSEEK_PROVIDER_INTROSPECTION",
        "report_id": "PCT-P2-DEEPSEEK-PROVIDER-INTROSPECTION-v0.1",
        "status": "PASS" if parsed["requested_model_found"] else "FAIL_MODEL_NOT_LISTED",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "source_mode": source_mode,
        "request": {
            "method": "GET",
            "base_url": base_url.rstrip("/"),
            "endpoint_path": "/models",
            "requested_model_identifier": requested_model,
            "task_generation": False,
            "chat_completion_calls": 0,
            "worker_trajectory_calls": 0,
        },
        "response": {
            "http_status": http_status,
            "object": "list",
            "requested_model_found": parsed["requested_model_found"],
            "returned_model_identifier": (
                parsed["requested_model_record"]["id"]
                if parsed["requested_model_record"]
                else None
            ),
            "returned_model_owner": (
                parsed["requested_model_record"]["owned_by"]
                if parsed["requested_model_record"]
                else None
            ),
            "available_model_ids": parsed["available_model_ids"],
        },
        "model_revision_or_snapshot": "NOT_EXPOSED_BY_PROVIDER",
        "frozen_input_artifacts": {
            "profile_candidate_path": profile_path.as_posix(),
            "profile_candidate_sha256": sha256_file(profile_path),
            "system_prompt_path": prompt_path.as_posix(),
            "system_prompt_sha256": sha256_file(prompt_path),
            "tool_catalog_path": tool_catalog_path.as_posix(),
            "tool_catalog_sha256": sha256_file(tool_catalog_path),
        },
        "credential_handling": {
            "credential_source": "GITHUB_ACTIONS_ENVIRONMENT_SECRET",
            "environment": "p2-natural-pilot",
            "secret_name": "DEEPSEEK_API_KEY",
            "secret_value_recorded": False,
            "secret_hash_recorded": False,
            "authorization_header_recorded": False,
        },
        "research_boundaries": {
            "natural_task_worker_calls": 0,
            "semantic_auditor_calls": 0,
            "reference_packets_opened": 0,
            "applied_to_runtime": False,
            "online_intervention": False,
        },
    }
    assert_no_secret_keys(report)
    report["report_digest"] = canonical_digest(report, "report_digest")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="https://api.deepseek.com")
    parser.add_argument("--requested-model", default="deepseek-v4-pro")
    parser.add_argument(
        "--profile",
        default="config/p2/deepseek-v4-pro-profile-candidate-v0.1.json",
    )
    parser.add_argument(
        "--system-prompt",
        default="config/p2/natural-pilot-system-prompt-v0.1.txt",
    )
    parser.add_argument(
        "--tool-catalog",
        default="config/p2/natural-pilot-tool-catalog-v0.1.json",
    )
    parser.add_argument(
        "--output",
        default="reports/p2/deepseek-provider-introspection-v0.1.json",
    )
    parser.add_argument("--models-json", default=None)
    parser.add_argument("--timeout-seconds", type=int, default=30)
    args = parser.parse_args()

    profile_path = Path(args.profile)
    prompt_path = Path(args.system_prompt)
    tool_catalog_path = Path(args.tool_catalog)
    for path in (profile_path, prompt_path, tool_catalog_path):
        if not path.is_file():
            raise FileNotFoundError(path)

    if args.models_json:
        http_status = 200
        payload = json.loads(Path(args.models_json).read_text(encoding="utf-8"))
        source_mode = "OFFLINE_TEST_FIXTURE"
    else:
        api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        if not api_key:
            print("DEEPSEEK_API_KEY is not available to the approved environment job.", file=sys.stderr)
            return 3
        try:
            http_status, payload = get_model_listing(
                args.base_url,
                api_key,
                args.timeout_seconds,
            )
        except HTTPError as exc:
            print(f"DeepSeek model-list introspection failed with HTTP {exc.code}.", file=sys.stderr)
            return 4
        except URLError as exc:
            print(f"DeepSeek model-list introspection network failure: {type(exc.reason).__name__}.", file=sys.stderr)
            return 5
        source_mode = "LIVE_READ_ONLY_PROVIDER_INTROSPECTION"

    parsed = parse_model_listing(payload, args.requested_model)
    report = build_report(
        requested_model=args.requested_model,
        base_url=args.base_url,
        http_status=http_status,
        parsed=parsed,
        profile_path=profile_path,
        prompt_path=prompt_path,
        tool_catalog_path=tool_catalog_path,
        source_mode=source_mode,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        "DeepSeek read-only model-list introspection: "
        f"status={report['status']}; requested_model={args.requested_model}; "
        f"task_generation=0; chat_completion_calls=0."
    )
    return 0 if report["status"] == "PASS" else 6


if __name__ == "__main__":
    raise SystemExit(main())
