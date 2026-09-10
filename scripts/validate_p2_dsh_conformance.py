#!/usr/bin/env python3
"""Validate the exact frozen DeepSeek Harness source and synthetic envelope."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pct.shadow.adapter import DeepSeekHarnessAdapter  # noqa: E402


def load(path: str) -> dict:
    value = json.loads((ROOT / path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected object")
    return value


def git(source: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(source), *args], text=True).strip()


def validate() -> list[str]:
    errors: list[str] = []
    manifest = load("data/p2/conformance/dsh-contract-manifest-v0.1.json")
    freeze = load("governance/p2-dsh-freeze-v0.1.json")
    report = load("reports/p2/dsh-conformance-report-v0.1.json")
    if manifest.get("commit") != freeze.get("commit") or report.get("commit") != freeze.get("commit"):
        errors.append("DSH commit differs across freeze, contract, and report")
    source_value = os.environ.get("PCT_DSH_SOURCE_DIR")
    require = os.environ.get("PCT_REQUIRE_DSH_CONFORMANCE") == "1"
    if not source_value:
        if require:
            errors.append("PCT_DSH_SOURCE_DIR is required in authoritative CI")
        return errors
    source = Path(source_value).resolve()
    if not (source / ".git").exists():
        errors.append(f"DSH source is not a Git checkout: {source}")
        return errors
    actual_commit = git(source, "rev-parse", "HEAD")
    if actual_commit != freeze.get("commit"):
        errors.append(f"DSH commit mismatch: {actual_commit}")
    for relative, expected_blob in manifest.get("git_blob_sha1", {}).items():
        path = source / relative
        if not path.is_file():
            errors.append(f"missing frozen DSH file: {relative}")
            continue
        actual_blob = git(source, "hash-object", relative)
        if actual_blob != expected_blob:
            errors.append(f"DSH blob mismatch for {relative}: {actual_blob}")

    known = (source / "packages/core/session/src/known-event-types.ts").read_text(encoding="utf-8")
    for event_type in manifest.get("required_event_vocabulary", []):
        if f"'{event_type}'" not in known:
            errors.append(f"frozen DSH event vocabulary missing {event_type}")
    loop = (source / "packages/core/agent-loop/src/agent.ts").read_text(encoding="utf-8")
    stopping = "await this.dispatch.serial('agent/turn-stopping'"
    turn_end = "this.session.append('turn/end'"
    if stopping not in loop or turn_end not in loop:
        errors.append("frozen DSH loop lacks expected turn-stopping/turn-end boundaries")
    elif loop.index(stopping) > loop.index(turn_end):
        errors.append("agent/turn-stopping is not before turn/end in frozen source")
    runtime = (source / "packages/core/agent/src/runtime-types.ts").read_text(encoding="utf-8")
    if "'agent/turn-stopping'" not in runtime or "payload: { agent: Agent; turn: number; signal: AbortSignal }" not in runtime:
        errors.append("native agent/turn-stopping payload contract changed")
    if "steer(message: UserMessage): void" not in runtime:
        errors.append("frozen Agent interface shape changed; re-review no-Steering guard")
    message = (source / "packages/llm/llm/src/message.ts").read_text(encoding="utf-8")
    if "type: 'tool-result'" not in message or "isError: input.isError" not in message:
        errors.append("frozen ToolResultMessage shape changed")

    fixture = load("data/p2/conformance/dsh-durable-envelope-v0.1.json")
    event = DeepSeekHarnessAdapter().normalize_session_event(
        fixture["envelope"], sequence=1, goal_id="G", goal_revision=1,
        snapshot_id="S", created_at="2026-08-26T03:00:00Z",
    )
    if event is None:
        errors.append("adapter rejected frozen synthetic DSH envelope")
    else:
        expected = fixture["expected_pct"]
        if event.event_type != expected["event_type"]:
            errors.append("adapter event_type mismatch")
        if event.payload.get("reported_status") != expected["reported_status"]:
            errors.append("adapter reported_status mismatch")
        if event.payload.get("authoritative") is not expected["authoritative"]:
            errors.append("adapter incorrectly promoted Tool result authority")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("P2 DSH conformance validation failed:", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1
    source = os.environ.get("PCT_DSH_SOURCE_DIR")
    if source:
        print("P2 DSH conformance passed against the exact frozen checkout; live model calls=0.")
    else:
        print("P2 DSH conformance manifest validated; source checkout not requested for this local run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
