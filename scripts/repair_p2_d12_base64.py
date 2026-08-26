#!/usr/bin/env python3
"""Repair bounded transport defects in the D12 base64 bootstrap.

Repairs are accepted only when exact precomputed SHA-256 values are recovered.
This helper deletes itself before the materialized research commit is created.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PART00 = ROOT / "data/p2/bootstrap/p2-d12-payload-v0.1.part-00.b64"
PART03 = ROOT / "data/p2/bootstrap/p2-d12-payload-v0.1.part-03.b64"

PART00_EXPECTED_LENGTH = 15_000
PART00_EXPECTED_SHA256 = "009d0d95b72c4cabf0b74fff22870db4ff4be156d518bdb65e4d2899940248bc"
PART00_REPAIR_START = 8_000
PART00_REPAIR_CHUNK = (
    "4pFBguDhPqV+AoYHTDG8pWe8RFMOoG+IQX2PDO6sZhBnNZjz7sjujuyrPLK1Z+Se"
    "RZ4M4dNhTML5VIXFMx/aN8SaymXt+SparCJ+CplDCbDDi0ngi5ybxjI5UWSOSYKL"
    "2LNnPCbogA6Iu7O7O7uv8uzWn+/sdmYTdCk2qDMrzdlCnVlf6NyCqG1o4m1JChhd"
    "yK0kHHPPWMpU/ytYzg2SAEjK/LM7srsj+yqPbOP5juxbid9MOqJSX1Vv+mKnl/HB"
    "qHTGtN+whx5NWEayo9H80Hxy3ozNr8Qijqaws2KqKP1iam4UgZmLrb87vrvj+yqP"
    "b/P5ju8bmujvFITOfhB8NN5RTy1jCN0ibF+YYV7nLYaK4rweYj8a/pwkYiSOQvdy"
    "kjfhRPQHPs5myzKbTau2+TjXB3BSTfvIaqw/zk3dcTbN7Y6zbrDdcd76OLeeU/iFt"
    "fMzLKfdDO/mH1/sMLcx/sGgKH7IvSaV4QmPLHjnQ2ZKInk2kckn3HM6c+buxO5O7"
    "Gs8sSJdwDOc2AtNVtjFZDp/aTXzKWqfDCUnrRRoZaAJGrOxMvsR3chDbHZIJfLDW"
    "H0lmOhJKIxLu6O7O7qv8uiaL2AcYrkADG+M1hjp3nupw3vCAlbJvTpfRURnzCZD70"
    "96fhXjkUEjH7gj1o23oCZddux3R3Z3ZF/nkX1G16oTkeWxj+kheJgL411f0quKXK"
    "XUl8oA1GT5zLEAIssJ8KMxCwCQBsllYJDsFfxMhwamNjBEagODpDb40WC5B+JlUJ"
    "eN0GA5Cg7lFAR/6OPdrFYrjWau420dVe1N2izT2vogp7r9Ux3krKNn644Ec9Z2312"
    "dty80mL/wRh9JcN58FB4uLPTSpk6+wlcbW5R804b/b1J/7Tu/sNXEqq91YrXXOrH"
    "6a51Y47VOrPnNJyYV1cCbE2MVkJWkuYcu+t0zkpvqFOMnYBo0FQ7LvM2jN/SpYHf"
    "xf7v4P13+14rd3MX/fXfxf5Qgceas5FdMoEXW"
)

PART03_EXPECTED_LENGTH = 13_964
PART03_EXPECTED_SHA256 = "b1f178c386185f5579e4fa927281ff000a8ebe7206fb9af9244deb9d6363af3b"


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("ascii")).hexdigest()


def repair_part00() -> dict[str, object]:
    value = PART00.read_text(encoding="ascii")
    if len(value) != PART00_EXPECTED_LENGTH:
        raise ValueError(f"unexpected part00 length: {len(value)}")
    if digest(value) == PART00_EXPECTED_SHA256:
        return {"repaired": False, "sha256": digest(value)}
    if len(PART00_REPAIR_CHUNK) != 1_000:
        raise ValueError("embedded part00 repair chunk length mismatch")
    value = (
        value[:PART00_REPAIR_START]
        + PART00_REPAIR_CHUNK
        + value[PART00_REPAIR_START + len(PART00_REPAIR_CHUNK) :]
    )
    if digest(value) != PART00_EXPECTED_SHA256:
        raise ValueError("part00 bounded repair did not recover the frozen SHA-256")
    PART00.write_text(value, encoding="ascii")
    return {
        "repaired": True,
        "start": PART00_REPAIR_START,
        "length": len(PART00_REPAIR_CHUNK),
        "sha256": digest(value),
    }


def repair_part03() -> dict[str, object]:
    value = PART03.read_text(encoding="ascii")
    repaired = False
    removed_index: int | None = None
    removed_character: str | None = None
    if len(value) == PART03_EXPECTED_LENGTH and digest(value) == PART03_EXPECTED_SHA256:
        pass
    elif len(value) == PART03_EXPECTED_LENGTH + 1:
        for index in range(len(value)):
            candidate = value[:index] + value[index + 1 :]
            if digest(candidate) == PART03_EXPECTED_SHA256:
                removed_index = index
                removed_character = value[index]
                value = candidate
                repaired = True
                PART03.write_text(value, encoding="ascii")
                break
        else:
            raise ValueError("no single-character deletion recovers the frozen part03 hash")
    else:
        raise ValueError(
            f"unexpected part03 length {len(value)}; expected {PART03_EXPECTED_LENGTH}"
        )
    if len(value) != PART03_EXPECTED_LENGTH or digest(value) != PART03_EXPECTED_SHA256:
        raise ValueError("repaired part03 does not match the frozen SHA-256")
    return {
        "repaired": repaired,
        "removed_index": removed_index,
        "removed_character": removed_character,
        "final_length": len(value),
        "sha256": digest(value),
    }


def main() -> int:
    result = {
        "status": "PASS",
        "part00": repair_part00(),
        "part03": repair_part03(),
    }
    Path(__file__).unlink(missing_ok=True)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
