"""Canonical serialization helpers for replayable PCT Shadow artifacts."""
from __future__ import annotations

import copy
import hashlib
import json
from typing import Any


def canonical_json(value: Any) -> str:
    """Return stable UTF-8 JSON used for hashes and replay equality."""
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def digest_json(value: Any) -> str:
    """Return a SHA-256 digest of canonical JSON."""
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def json_clone(value: Any) -> Any:
    """Return a JSON-compatible defensive copy."""
    return copy.deepcopy(value)
