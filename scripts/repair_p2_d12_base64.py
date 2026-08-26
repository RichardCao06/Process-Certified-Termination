#!/usr/bin/env python3
"""Repair a one-character transport defect in the final D12 base64 part.

The repair is accepted only when the exact precomputed SHA-256 of the intended
final part is recovered. This helper deletes itself before the materialized
research commit is created.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "data/p2/bootstrap/p2-d12-payload-v0.1.part-03.b64"
EXPECTED_LENGTH = 13_964
EXPECTED_SHA256 = "b1f178c386185f5579e4fa927281ff000a8ebe7206fb9af9244deb9d6363af3b"


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("ascii")).hexdigest()


def main() -> int:
    value = TARGET.read_text(encoding="ascii")
    repaired = False
    removed_index: int | None = None
    removed_character: str | None = None

    if len(value) == EXPECTED_LENGTH and digest(value) == EXPECTED_SHA256:
        pass
    elif len(value) == EXPECTED_LENGTH + 1:
        for index in range(len(value)):
            candidate = value[:index] + value[index + 1 :]
            if digest(candidate) == EXPECTED_SHA256:
                removed_index = index
                removed_character = value[index]
                value = candidate
                repaired = True
                TARGET.write_text(value, encoding="ascii")
                break
        else:
            raise ValueError("no single-character deletion recovers the frozen part hash")
    else:
        raise ValueError(
            f"unexpected final-part length {len(value)}; expected {EXPECTED_LENGTH}"
        )

    if len(value) != EXPECTED_LENGTH or digest(value) != EXPECTED_SHA256:
        raise ValueError("repaired final part does not match the frozen SHA-256")

    Path(__file__).unlink(missing_ok=True)
    print(
        json.dumps(
            {
                "status": "PASS",
                "repaired": repaired,
                "removed_index": removed_index,
                "removed_character": removed_character,
                "final_length": len(value),
                "final_sha256": digest(value),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
