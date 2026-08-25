#!/usr/bin/env python3
"""Validate final PCT P1 closure artifacts while preserving historical snapshots."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

FILES = {
    "decision": ROOT / "governance/p1-d15-decision-record-v0.1.json",
    "correction": ROOT / "data/p1/development-pilot/pass-b/human-adjudication-codebook-correction-v0.1.json",
    "final_adjudication": ROOT / "data/p1/development-pilot/pass-b/adjudicated-material-fields-final-v0.1.json",
    "matrix": ROOT / "reports/p1/pass-b/reliability-matrix-final-v0.1.json",
    "migration": ROOT / "docs/p1/p1-taxonomy-migration-v0.1.md",
    "approval": ROOT / "docs/p1/p1-closure-approval-record-v0.1.md",
    "report": ROOT / "docs/p1/p1-closure-report-v0.1.md",
    "exit_gate": ROOT / "docs/p1/p1-exit-gate-v0.2-final.md",
    "status": ROOT / "governance/p1-closure-status-v0.1.json",
    "summary": ROOT / "reports/p1/p1-final-output-summary-v0.1.json",
    "html": ROOT / "docs/p1/p1-final-output-summary-v0.1.html",
    "manifest": ROOT / "reports/p1/p1-final-delivery-manifest-v0.1.json",
}

RAW_ADJUDICATION_SHA = "03b8a87b61cce8ef5e0a1d5b07b0df909562a142c83d30898fab594d1856e3ce"
D15_SOURCE = "https://github.com/RichardCao06/Process-Certified-Termination/pull/2#issuecomment-5407303134"
EXPECTED_CORRECTIONS = {
    "dev-023": ("FAIL", "UNKNOWN"),
    "dev-012": ("FAIL", "UNKNOWN"),
    "dev-017": ("FAIL", "PASS"),
}
PRIMARY = {"accept_decision", "process_verdict", "stop_scope", "recovery_authority"}
REVIEW = {
    "outcome_verdict", "certification_recommendation", "fit_status", "fit_locator",
    "hard_gate_presence", "certification_effects",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def validate() -> list[str]:
    errors: list[str] = []
    for name, path in FILES.items():
        if not path.is_file():
            errors.append(f"missing final P1 artifact {name}: {path.relative_to(ROOT)}")
    if errors:
        return errors

    decision = load_json(FILES["decision"])
    if decision.get("decision_id") != "PCT-P1-D15":
        errors.append("final decision record must be PCT-P1-D15")
    if decision.get("status") != "APPROVED" or decision.get("human_decision") != "A":
        errors.append("PCT-P1-D15 must preserve approved option A")
    if decision.get("approval_source") != D15_SOURCE:
        errors.append("PCT-P1-D15 approval source mismatch")
    if decision.get("raw_adjudication_overwrite_authorized") is not False:
        errors.append("D15 must prohibit overwriting raw adjudication")
    if decision.get("p2_authorized") is not False:
        errors.append("D15 must not authorize P2")

    correction = load_json(FILES["correction"])
    if correction.get("status") != "FINAL_APPEND_ONLY_CORRECTION":
        errors.append("correction record must be final and append-only")
    if correction.get("source_raw_adjudication_sha256") != RAW_ADJUDICATION_SHA:
        errors.append("correction points to wrong raw adjudication")
    if correction.get("raw_adjudication_preserved_unchanged") is not True:
        errors.append("correction must preserve raw adjudication")
    actual = {
        item.get("trajectory_id"): (item.get("submitted_value"), item.get("corrected_value"))
        for item in correction.get("corrections", [])
    }
    if actual != EXPECTED_CORRECTIONS:
        errors.append(f"D15 correction set mismatch: {actual}")

    final = load_json(FILES["final_adjudication"])
    if final.get("status") != "FINAL_DEVELOPMENTAL_P1":
        errors.append("final adjudication has wrong status")
    if final.get("raw_adjudication_sha256") != RAW_ADJUDICATION_SHA:
        errors.append("final adjudication points to wrong raw source")
    if final.get("correction_record_sha256") != sha256(FILES["correction"]):
        errors.append("final adjudication correction hash mismatch")
    if final.get("raw_adjudication_preserved_unchanged") is not True:
        errors.append("final adjudication must preserve raw source")
    if final.get("unresolved_required_fields") != 0:
        errors.append("final adjudication cannot retain unresolved required fields")
    cases = {item.get("trajectory_id"): item for item in final.get("cases", [])}
    if len(cases) != 12:
        errors.append("final adjudication must contain all 12 paired cases")
    for tid, (_, expected) in EXPECTED_CORRECTIONS.items():
        value = cases.get(tid, {}).get("final_material_fields", {}).get("outcome_verdict")
        if value != expected:
            errors.append(f"{tid} final Outcome expected {expected}, got {value}")

    matrix = load_json(FILES["matrix"])
    if matrix.get("status") != "FINAL_APPROVED_WITH_LIMITATIONS":
        errors.append("final Reliability Matrix has wrong status")
    rows = {row.get("layer"): row for row in matrix.get("rows", [])}
    primary_actual = {
        layer for layer, row in rows.items()
        if row.get("classification") == "PILOT_STABLE_ENOUGH_FOR_SHADOW_MEASUREMENT"
    }
    if primary_actual != PRIMARY:
        errors.append(f"primary Shadow layer set mismatch: {primary_actual}")
    for layer in REVIEW:
        if rows.get(layer, {}).get("classification") != "USABLE_WITH_HUMAN_REVIEW":
            errors.append(f"{layer} must remain USABLE_WITH_HUMAN_REVIEW")
    if rows.get("valid_alternative_path", {}).get("classification") != (
        "NOT_RELIABLY_ANNOTATABLE_IN_CURRENT_FORM"
    ):
        errors.append("Valid Alternative Path must remain excluded pending repair")
    p2 = matrix.get("p2_recommendation", {})
    if p2.get("online_intervention_authorized") is not False:
        errors.append("matrix must not authorize online intervention")
    if p2.get("p2_work_order_authorized") is not False:
        errors.append("matrix must not authorize P2 Work Order")

    status = load_json(FILES["status"])
    if status.get("status") != "APPROVED_WITH_LIMITATIONS":
        errors.append("P1 closure status must be APPROVED_WITH_LIMITATIONS")
    if status.get("p1_closed") is not True or status.get("p1_exit_gate_passed") is not True:
        errors.append("P1 must be recorded closed with passed Exit Gate")
    if status.get("open_normative_gate_ids") != []:
        errors.append("no P1 normative gate may remain open")
    if status.get("p2_authorized") is not False:
        errors.append("P1 closure must not authorize P2")
    if status.get("online_intervention_authorized") is not False:
        errors.append("P1 closure must not authorize online intervention")
    if status.get("effectiveness_claim_allowed") is not False:
        errors.append("P1 closure cannot allow effectiveness claims")
    if status.get("provenance_incident_ids") != ["PCT-P1-I01"]:
        errors.append("P1-I01 must remain an accepted provenance limitation")
    if status.get("final_adjudication_sha256") != sha256(FILES["final_adjudication"]):
        errors.append("closure status final adjudication hash mismatch")
    if status.get("final_reliability_matrix_sha256") != sha256(FILES["matrix"]):
        errors.append("closure status Reliability Matrix hash mismatch")
    if status.get("closure_report_sha256") != sha256(FILES["report"]):
        errors.append("closure status report hash mismatch")

    report = FILES["report"].read_text(encoding="utf-8")
    for phrase in (
        "APPROVED WITH LIMITATIONS",
        "Repeatability is not correctness",
        "PCT-P1-I01",
        "P2 authorized: NO",
        "Effectiveness claim allowed: NO",
    ):
        if phrase not in report:
            errors.append(f"final Closure Report missing boundary: {phrase}")

    exit_gate = FILES["exit_gate"].read_text(encoding="utf-8")
    if "PASSED — P1 CLOSED" not in exit_gate:
        errors.append("final Exit Gate must state P1 closed")
    if "- [ ] P2 Shadow Work Order separately approved." not in exit_gate:
        errors.append("final Exit Gate must leave P2 authorization unchecked")

    manifest = load_json(FILES["manifest"])
    if manifest.get("status") != "FINAL":
        errors.append("final delivery manifest has wrong status")
    for item in manifest.get("files", []):
        path = ROOT / item["path"]
        if not path.is_file():
            errors.append(f"manifest file missing: {item['path']}")
            continue
        if sha256(path) != item["sha256"]:
            errors.append(f"manifest hash mismatch: {item['path']}")
        if path.stat().st_size != item["bytes"]:
            errors.append(f"manifest byte count mismatch: {item['path']}")
    if manifest.get("p2_authorized") is not False:
        errors.append("delivery manifest must not authorize P2")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("P1 final closure validation failed:", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1
    print(
        "P1 final closure validation passed: D15-A is recorded, raw adjudication is "
        "preserved, the append-only correction and final Reliability Matrix are "
        "consistent, P1 is closed with limitations, and P2 remains unauthorized."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
