#!/usr/bin/env python3
"""Validate D01-D12 active P2 state, sidecar contract, and 20+10 regression."""
from __future__ import annotations

import ast
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pct.shadow.mutation_guard import find_forbidden_calls  # noqa: E402
from pct.shadow.regression import catalog, run_regression  # noqa: E402
from pct.shadow.replay import run_replay, verify_replay  # noqa: E402
from pct.shadow.sidecar import CandidateStopSidecar, ReadOnlyCandidateStopObserver  # noqa: E402

DECISIONS = {f"PCT-P2-D{i:02d}" for i in range(1, 13)}
OPEN = {f"PCT-P2-D{i:02d}" for i in range(13, 19)}
REQUIRED = [
    "governance/p2-human-approval-d01-d12-v0.1.json",
    "governance/p2-decision-register-v0.2.json",
    "governance/p2-shadow-policy-v0.1.json",
    "governance/p2-dsh-freeze-v0.1.json",
    "governance/p2-status-v0.2.json",
    "governance/p2-state-reconciliation-record-v0.1.json",
    "schemas/pct-p2-candidate-stop-sidecar-v0.1.schema.json",
    "data/p2/fixtures/synthetic-regression-catalog-v0.1.json",
    "reports/p2/synthetic-shadow-regression-v0.1.json",
    "reports/p2/dsh-conformance-report-v0.1.json",
    "reports/p2/synthetic-shadow-regression-freeze-v0.1.json",
    "reports/p2/d12-sidecar-validation-v0.1.json",
    "docs/p2/p2-candidate-stop-sidecar-contract-v0.1.md",
    "docs/p2/p2-human-decision-pack-d13-d18-v0.1.md",
]
FORBIDDEN_IMPORTS = {"requests", "httpx", "socket", "urllib"}


def load_json(path: str | Path) -> dict:
    target = ROOT / path if isinstance(path, str) else path
    value = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{target}: expected JSON object")
    return value


def import_roots(source: str) -> set[str]:
    tree = ast.parse(source)
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def validate() -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"missing active P2 artifact: {relative}")
    if errors:
        return errors

    approval = load_json("governance/p2-human-approval-d01-d12-v0.1.json")
    if approval.get("status") != "COMPLETE":
        errors.append("D01-D12 approval record is not COMPLETE")
    if set(approval.get("approved_options", {})) != DECISIONS:
        errors.append("D01-D12 approval set mismatch")
    if set(approval.get("approved_options", {}).values()) != {"A"}:
        errors.append("D01-D12 selected options are not all A")

    register = load_json("governance/p2-decision-register-v0.2.json")
    approved_records = {
        item.get("decision_id"): item
        for item in register.get("decisions", [])
        if item.get("status") == "APPROVED"
    }
    if set(approved_records) != DECISIONS:
        errors.append("active decision register does not contain D01-D12 approvals")
    for decision_id, record in approved_records.items():
        if record.get("selected_option") != "A":
            errors.append(f"{decision_id} record is not approved option A")

    policy = load_json("governance/p2-shadow-policy-v0.1.json")
    if policy.get("status") != "FROZEN":
        errors.append("active Shadow policy is not FROZEN")
    if set(policy.get("approved_decision_ids", [])) != DECISIONS:
        errors.append("active Shadow policy does not bind D01-D12")
    if policy.get("mode") != "SHADOW" or policy.get("applied_to_runtime") is not False:
        errors.append("active Shadow policy authority boundary is invalid")
    for field in (
        "online_intervention_authorized",
        "worker_behavior_change_authorized",
        "natural_task_shadow_measurement_authorized",
        "private_runtime_trace_collection_authorized",
        "reference_evaluator_opening_authorized",
        "effectiveness_claim_allowed",
    ):
        if policy.get(field) is not False:
            errors.append(f"active policy must keep {field}=false")
    if policy.get("semantic_auditor", {}).get("enabled") is not False:
        errors.append("semantic auditor must remain disabled")
    metadata_policy = policy.get("candidate_stop_metadata_policy", {})
    if metadata_policy.get("source") != "EXPLICIT_READ_ONLY_SIDECAR":
        errors.append("D12 sidecar policy source mismatch")
    if metadata_policy.get("infer_from_assistant_prose") is not False:
        errors.append("D12 policy must prohibit inference from assistant prose")

    status = load_json("governance/p2-status-v0.2.json")
    if set(status.get("approved_decision_ids", [])) != DECISIONS:
        errors.append("active P2 status approved decision set mismatch")
    if set(status.get("open_normative_gate_ids", [])) != OPEN:
        errors.append("active P2 status must open D13-D18")
    for field in (
        "natural_task_shadow_measurement_authorized",
        "live_worker_model_calls_authorized",
        "semantic_audit_agent_authorized",
        "private_runtime_trace_collection_authorized",
        "reference_evaluator_opening_authorized",
        "online_intervention_authorized",
        "worker_behavior_change_authorized",
        "effectiveness_claim_allowed",
    ):
        if status.get(field) is not False:
            errors.append(f"P2 status must keep {field}=false")

    incident = load_json("governance/p2-state-reconciliation-record-v0.1.json")
    if incident.get("history_rewritten") is not False or incident.get("force_push_used") is not False:
        errors.append("state reconciliation must preserve history")

    for path in sorted((ROOT / "schemas").glob("pct-p2-*.schema.json")):
        schema = load_json(path)
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            errors.append(f"{path.name}: wrong JSON Schema dialect")
        if not schema.get("$id"):
            errors.append(f"{path.name}: missing $id")

    for path in sorted((ROOT / "pct/shadow").glob("*.py")):
        source = path.read_text(encoding="utf-8")
        for line, name in find_forbidden_calls(source):
            errors.append(f"{path.relative_to(ROOT)}:{line}: forbidden runtime call {name}")
        unexpected = import_roots(source) & FORBIDDEN_IMPORTS
        if unexpected:
            errors.append(f"{path.relative_to(ROOT)} imports network modules: {sorted(unexpected)}")

    # D12 positive binding and missing-metadata behavior.
    sidecar = CandidateStopSidecar(
        sidecar_id="validation-sidecar", source="TEST_FIXTURE", session_id="validation-session",
        turn=1, goal_id="validation-goal", goal_revision=1, snapshot_id="validation-snapshot",
        stop_scope="GOAL_COMPLETION_PROPOSAL", recovery_authority="NOT_APPLICABLE",
        worker_claim="COMPLETE", claims_goal_complete=True, created_at="2026-08-26T03:30:00Z",
    )
    observer = ReadOnlyCandidateStopObserver()
    complete_event, complete_stop, complete_value = observer.observe_turn_stopping(
        sequence=1, session_id="validation-session", turn=1, goal_id="validation-goal",
        goal_revision=1, snapshot_id="validation-snapshot", created_at="2026-08-26T03:30:00Z",
        sidecar=sidecar,
    )
    if complete_stop.get("sidecar_digest") != sidecar.digest() or complete_value is None:
        errors.append("explicit sidecar was not digest-bound")
    missing_event, missing_stop, missing_value = observer.observe_turn_stopping(
        sequence=1, session_id="validation-session", turn=1, goal_id="validation-goal",
        goal_revision=1, snapshot_id="validation-snapshot", created_at="2026-08-26T03:30:00Z",
        sidecar=None,
    )
    if missing_value is not None or missing_stop.get("stop_scope") != "UNKNOWN" or missing_stop.get("recovery_authority") != "UNKNOWN":
        errors.append("missing sidecar did not preserve UNKNOWN metadata")
    if complete_event.payload.get("observer_id") != missing_event.payload.get("observer_id"):
        errors.append("sidecar observer identity is unstable")

    expected_catalog = catalog()
    committed_catalog = load_json("data/p2/fixtures/synthetic-regression-catalog-v0.1.json")
    if expected_catalog != committed_catalog:
        errors.append("synthetic regression catalog is stale")
    recomputed = run_regression(policy)
    committed = load_json("reports/p2/synthetic-shadow-regression-v0.1.json")
    if recomputed != committed:
        errors.append("synthetic regression report is not reproducible from active code/policy")
    if committed.get("status") != "PASS" or committed.get("passed") != 30 or committed.get("failed") != 0:
        errors.append("20+10 synthetic regression did not pass 30/30")
    if committed.get("live_model_calls") != 0 or committed.get("applied_to_runtime") is not False:
        errors.append("synthetic regression crossed the Shadow authority boundary")
    metrics = committed.get("accepted_bundle_metrics", {})
    if metrics.get("deterministic_replay_equality_rate") != 1.0:
        errors.append("synthetic accepted-bundle replay equality is not 100%")
    if metrics.get("applied_to_runtime_count") != 0:
        errors.append("a synthetic bundle was applied to runtime")

    freeze = load_json("reports/p2/synthetic-shadow-regression-freeze-v0.1.json")
    import hashlib
    for item in freeze.get("files", []):
        path = ROOT / item.get("path", "")
        if not path.is_file():
            errors.append(f"regression freeze references missing file: {item.get('path')}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != item.get("sha256"):
            errors.append(f"regression freeze hash mismatch: {item.get('path')}")

    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    for target in ("validate-p2-active", "validate-p2-dsh-conformance"):
        if target not in makefile:
            errors.append(f"Makefile is missing {target}")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("P2 active-state validation failed:", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1
    print(
        "P2 active-state validation passed: D01-D12 are materialized, the read-only "
        "sidecar is replay-bound, 20+10 regression is 30/30, and natural/model/" 
        "reference/online authorities remain disabled."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
