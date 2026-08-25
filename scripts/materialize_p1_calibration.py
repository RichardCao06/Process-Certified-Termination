#!/usr/bin/env python3
"""Materialize the versioned P1 calibration data bundle into the working tree."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import tarfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    bundle_dir = root / "data" / "p1" / "calibration"
    manifest = json.loads((bundle_dir / "bundle-manifest.json").read_text(encoding="utf-8"))
    archive = base64.b64decode(
        "".join(
            "".join((bundle_dir / part).read_text(encoding="utf-8").split())
            for part in manifest["parts"]
        ),
        validate=True,
    )
    actual = hashlib.sha256(archive).hexdigest()
    if actual != manifest["sha256"]:
        raise SystemExit(f"bundle SHA-256 mismatch: expected {manifest['sha256']}, got {actual}")
    archive_path = bundle_dir / manifest["decoded_filename"]
    archive_path.write_bytes(archive)
    with tarfile.open(archive_path, "r:gz") as tf:
        for member in tf.getmembers():
            target = (root / member.name).resolve()
            if root not in target.parents and target != root:
                raise SystemExit(f"unsafe bundle path: {member.name}")
            if target.exists() and not args.force:
                raise SystemExit(f"refusing to overwrite {target}; pass --force to materialize the reviewed bundle")
        tf.extractall(root, filter="data")
    archive_path.unlink()
    print(f"Materialized {len(manifest['files'])} files; bundle SHA-256 {actual}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
