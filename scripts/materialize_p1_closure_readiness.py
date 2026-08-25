#!/usr/bin/env python3
"""Materialize the P1 closure-readiness data bundle into a destination directory."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
PASS_B = ROOT / "data" / "p1" / "development-pilot" / "pass-b"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "build" / "p1-closure-readiness",
    )
    args = parser.parse_args()
    manifest = json.loads(
        (PASS_B / "closure-readiness-bundle-manifest-v0.1.json").read_text(
            encoding="utf-8"
        )
    )
    encoded = "".join(
        "".join((PASS_B / part).read_text(encoding="utf-8").split())
        for part in manifest["parts"]
    )
    archive = base64.b64decode(encoded, validate=True)
    actual = hashlib.sha256(archive).hexdigest()
    if actual != manifest["sha256"]:
        raise ValueError(
            f"closure-readiness bundle SHA-256 mismatch: {actual} != {manifest['sha256']}"
        )
    args.output.mkdir(parents=True, exist_ok=True)
    archive_path = args.output / manifest["decoded_filename"]
    archive_path.write_bytes(archive)
    root = args.output.resolve()
    with tarfile.open(archive_path, "r:gz") as tf:
        for member in tf.getmembers():
            target = (root / member.name).resolve()
            if target != root and root not in target.parents:
                raise ValueError(f"unsafe archive path: {member.name}")
        tf.extractall(root, filter="data")
    print(f"Materialized P1 closure-readiness data under {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
