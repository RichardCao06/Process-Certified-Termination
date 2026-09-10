#!/usr/bin/env python3
"""Validate the non-intervening P2 Shadow foundation and open Human Gate."""
from __future__ import annotations

import ast
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pct.shadow.mutation_guard import find_forbidden_calls, forbidden_payload_paths  # noqa: E402
from pct.shadow.replay import run_replay, verify_replay  # noqa: E402

DECISIONS = {f"PCT-P2-D0{i}" for i in range(1, 8)}
REQUIRED = [
    "docs/p2/README.md",
    "docs/p2/work-order-PCT-P2-001-v0.1.md",
    "docs/p2/p2-human-decision-pack-v0.1.md",
    "docs/p2/p2-shadow-foundation-spec-v0.1.md",
    "docs/p2/p2-data-and-isolation-boundary-v0.1-draft.md",
    "docs/p2/p2-exit-gate-v0.1-draft.md",
    "governance/p2-status-v0.1.json",
    "governance/p2-decision-register-v0.1.json",
    "governance/p2-shadow-policy-v0.1-draft.json",
    "schemas/pct-p2-event-v0.1.schema.json",
    "schemas/pct-p2-evidence-record-v0.1.schema.json",
    "schemas/pct-p2-candidate-stop-snapshot-v0.1.schema.json",
    "schemas/pct-p2-shadow-verdict-v0.1.schema.json",
    "schemas/pct-p2-replay-bundle-v0.1.schema.json",
    "data/p2/fixtures/replay-clean-success-v0.1.json",
    "data/p2/fixtures/replay-stale-evidence-v0.1.json",
]
FORBIDDEN_IMPORTS = {"requests", "httpx", "socket", "urllib", "subprocess"}


def load_json(path: str | Path) -> dict:
    target = ROOT / path if isinstance(path, str) else path
    value = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{target}: expected JSON object")
    return value


def _import_roots(source: str) -> set[str]:
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
            errors.append(f"missing P2 foundation artifact: {relative}")
    if errors:
        return errors

    p1 = load_json("governance/p1-closure-status-v0.1.json")
    if p1.get("p1_closed") is not True:
        errors.append("P2 foundation requires closed P1")
    if p1.get("p2_shadow_eligible_for_separate_human_decision") is not True:
        errors.append("P1 did not record eligibility for a separate P2 decision")

    status = load_json("governance/p2-status-v0.1.json")
    if status.get("status") != "FOUNDATION_ACTIVE_HUMAN_GATES_PENDING":
        errors.append("P2 status must remain foundation-active with Human Gates pending")
    if status.get("p2_foundation_authorized") is not True:
        errors.append("Research Owner foundation authorization is missing")
    if set(status.get("open_normative_gate_ids", [])) != DECISIONS:
        errors.append("P2 open decision set must be D01-D07")
    for field in (
        "live_shadow_measurement_authorized",
        "semantic_audit_agent_authorized",
        "private_runtime_trace_collection_authorized",
        "reference_evaluator_opening_authorized",
        "online_intervention_authorized",
        "worker_behavior_change_authorized",
        "effectiveness_claim_allowed",
        "sealed_or_hidden_data_accessed",
    ):
        if status.get(field) is not False:
            errors.append(f"{field} must remain false before Human decisions")

    register = load_json("governance/p2-decision-register-v0.1.json")
    items = register.get("decisions", [])
    actual = {item.get("decision_id") for item in items}
    if actual != DECISIONS:
        errors.append(f"decision register mismatch: {actual}")
    for item in items:
        if item.get("status") != "PENDING_HUMAN":
            errors.append(f"{item.get('decision_id')} must remain PENDING_HUMAN")
        if item.get("recommended_option") not in item.get("options", {}):
            errors.append(f"{item.get('decision_id')} recommendation is invalid")

    policy = load_json("governance/p2-shadow-policy-v0.1-draft.json")
    if policy.get("status") != "PENDING_HUMAN_DECISIONS":
        errors.append("draft Shadow policy must remain pending")
    if policy.get("approved_decision_ids") != []:
        errors.append("draft policy cannot claim approved P2 decisions")
    if policy.get("hard_check_ids") != []:
        errors.append("draft policy cannot activate hard checks")
    if policy.get("primary_label_layers") != []:
        errors.append("draft policy cannot activate primary labels")
    if policy.get("labels_may_be_emitted") is not False:
        errors.append("draft policy must disable labels")
    if policy.get("applied_to_runtime") is not False:
        errors.append("draft policy cannot apply to runtime")
    if policy.get("online_intervention_authorized") is not False:
        errors.append("draft policy cannot authorize intervention")

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
        imports = _import_roots(source)
        unexpected = imports & FORBIDDEN_IMPORTS
        if unexpected:
            errors.append(
                f"{path.relative_to(ROOT)} imports runtime/network modules: "
                + ", ".join(sorted(unexpected))
            )

    clean_input = load_json("data/p2/fixtures/replay-clean-success-v0.1.json")
    stale_input = load_json("data/p2/fixtures/replay-stale-evidence-v0.1.json")
    for name, fixture in (("clean", clean_input), ("stale", stale_input)):
        forbidden = forbidden_payload_paths(fixture)
        if forbidden:
            errors.append(f"{name} fixture leaks prohibited fields: {forbidden}")

    clean = run_replay(clean_input)
    if verify_replay(clean):
        errors.append("clean replay is not deterministic")
    if clean["verdict"].get("verdict_status") != "POLICY_PENDING":
        errors.append("clean fixture must remain policy-pending")
    if clean["verdict"].get("labels_emitted") is not False:
        errors.append("foundation cannot emit labels before P2 decisions")
    if clean["verdict"].get("findings") != []:
        errors.append("clean fixture unexpectedly produced findings")

    stale = run_replay(stale_input)
    if verify_replay(stale):
        errors.append("stale-evidence replay is not deterministic")
    check_ids = {item["check_id"] for item in stale["verdict"]["findings"]}
    expected = {
        "P2.CHK.VERIFIED_WITHOUT_VALID_EVIDENCE",
        "P2.CHK.STALE_EVIDENCE_REFERENCED",
    }
    if not expected <= check_ids:
        errors.append(f"stale fixture missing expected checks: {expected - check_ids}")
    if stale["verdict"].get("labels_emitted") is not False:
        errors.append("adverse fixture cannot emit labels before policy freeze")

    work_order = (ROOT / "docs/p2/work-order-PCT-P2-001-v0.1.md").read_text(encoding="utf-8")
    for phrase in ("PARTIALLY AUTHORIZED", "no online controller", "PCT-P2-D01", "PCT-P2-D07"):
        if phrase not in work_order:
            errors.append(f"P2 Work Order missing boundary: {phrase}")

    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    if "validate-p2-foundation" not in makefile:
        errors.append("Makefile does not include P2 foundation validation")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("P2 foundation validation failed:", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1
    print(
        "P2 foundation validation passed: P1 is closed, A2 reversible Shadow "
        "scaffolding is replayable and non-intervening, D01-D07 remain Human "
        "Gates, labels and live measurement remain disabled."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
