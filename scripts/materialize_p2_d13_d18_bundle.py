#!/usr/bin/env python3
"""Materialize the frozen P2 D13-D18 protocol increment from a transport archive."""
from __future__ import annotations

import base64
import hashlib
import shutil
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTS = sorted((ROOT / "data/p2/bootstrap").glob("p2-d13-d18-payload.part-*.b64"))
EXPECTED_ARCHIVE_SHA256 = "eaa7899feb1448f55d4bdf73ecb838ece2bf775209a593a1f08d5841475cb432"
FINAL_MARKER = ROOT / "reports/p2/d13-d18-protocol-materialization-manifest-v0.1.json"


def main() -> int:
    if FINAL_MARKER.is_file():
        print("D13-D18 protocol is already materialized; no action required.")
        return 0
    if len(PARTS) != 8:
        raise ValueError(f"expected 8 payload parts, found {len(PARTS)}")
    encoded = "".join(path.read_text(encoding="ascii") for path in PARTS)
    archive = base64.b64decode(encoded, validate=True)
    actual = hashlib.sha256(archive).hexdigest()
    if actual != EXPECTED_ARCHIVE_SHA256:
        raise ValueError(f"archive SHA-256 mismatch: {actual}")
    with tempfile.TemporaryDirectory(prefix="pct-p2-d13-d18-") as temp:
        archive_path = Path(temp) / "payload.zip"
        archive_path.write_bytes(archive)
        with zipfile.ZipFile(archive_path) as bundle:
            for member in bundle.infolist():
                relative = Path(member.filename)
                if relative.is_absolute() or ".." in relative.parts:
                    raise ValueError(f"unsafe archive path: {member.filename}")
            bundle.extractall(ROOT)
    shutil.rmtree(ROOT / "data/p2/bootstrap", ignore_errors=True)
    Path(__file__).unlink(missing_ok=True)
    print(f"Materialized P2 D13-D18 protocol from archive {actual}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
