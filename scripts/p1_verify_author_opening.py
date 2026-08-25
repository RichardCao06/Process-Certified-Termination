#!/usr/bin/env python3
"""Verify the post-Pass-B opening record for Fixture Author Expectations.

This script does not decrypt ciphertext. The custody process performs decryption outside
the annotation session, then this script verifies that opening happened only after both
human passes were frozen and that the opened plaintext matches its pre-existing hash.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pass-a-freeze", type=Path, required=True)
    parser.add_argument("--pass-b-freeze", type=Path, required=True)
    parser.add_argument("--expectation-commitment", type=Path, required=True)
    parser.add_argument("--opened-expectations", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pass_a = load_object(args.pass_a_freeze)
    pass_b = load_object(args.pass_b_freeze)
    commitment = load_object(args.expectation_commitment)

    if pass_a.get("frozen") is not True and pass_a.get("status") not in {
        "FROZEN",
        "frozen",
    }:
        raise ValueError("Pass A is not recorded as frozen")
    if pass_b.get("frozen") is not True and pass_b.get("status") not in {
        "FROZEN",
        "frozen",
    }:
        raise ValueError("Pass B is not recorded as frozen")
    expected_sha = commitment.get("plaintext_sha256") or commitment.get(
        "author_expectations_sha256"
    )
    if not isinstance(expected_sha, str) or len(expected_sha) != 64:
        raise ValueError(
            "expectation commitment does not contain a plaintext SHA-256"
        )
    actual_sha = digest(args.opened_expectations)
    if actual_sha != expected_sha:
        raise ValueError(
            "opened Fixture Author Expectations do not match the pre-existing commitment"
        )

    value = json.loads(args.opened_expectations.read_text(encoding="utf-8"))
    items = value.get("expectations") if isinstance(value, dict) else value
    if not isinstance(items, list):
        raise ValueError(
            "opened expectations must be a list or an object with expectations"
        )
    ids = [item.get("trajectory_id") for item in items if isinstance(item, dict)]
    if len(ids) != len(items) or len(ids) != len(set(ids)):
        raise ValueError("opened expectations require unique trajectory_id values")

    record = {
        "record_type": "PCT_P1_FIXTURE_AUTHOR_EXPECTATION_OPENING_VERIFICATION",
        "verified": True,
        "not_gold": True,
        "pass_a_freeze_sha256": digest(args.pass_a_freeze),
        "pass_b_freeze_sha256": digest(args.pass_b_freeze),
        "commitment_sha256": digest(args.expectation_commitment),
        "opened_expectations_sha256": actual_sha,
        "expectation_count": len(items),
        "interpretation": (
            "Fixture Author Expectations are a developmental third reference "
            "and are not automatically adjudicated truth."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Verified {len(items)} opened Fixture Author Expectations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
