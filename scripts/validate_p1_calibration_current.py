#!/usr/bin/env python3
"""Validate preserved Calibration artifacts under the current approved P1 decision state.

The historical validator remains unchanged as provenance for the post-calibration
revision gate. This adapter replaces only its obsolete assumption that D11-D14
must forever remain pending; all trajectory, hash, adjudication, regression,
evidence, and blinding checks continue to run through the historical validator.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY_PATH = ROOT / "scripts" / "validate_p1_calibration.py"
spec = importlib.util.spec_from_file_location("validate_p1_calibration_legacy", LEGACY_PATH)
legacy = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(legacy)

# Re-export the read-only helpers used by the Calibration unit tests.
CAL = legacy.CAL
REG = legacy.REG
load_json = legacy.load_json
validate_inputs = legacy.validate_inputs
validate_adjudication = legacy.validate_adjudication
validate_records_and_regression = legacy.validate_records_and_regression


def validate_current_decision_state() -> list[str]:
    errors: list[str] = []
    register = legacy.load_json(ROOT / "governance" / "p1-decision-register.json")
    status = legacy.load_json(ROOT / "governance" / "p1-status.json")
    decisions = register.get("decisions", [])
    ids = [item.get("id") for item in decisions]
    expected = [f"PCT-P1-D{i:02d}" for i in range(1, 15)]
    if ids != expected:
        errors.append(f"P1 decisions must be D01-D14 in order: got {ids}")

    for item in decisions:
        did = item.get("id")
        if item.get("status") != "approved" or item.get("human_decision") != "A":
            errors.append(f"{did}: all D01-D14 decisions must preserve the approved A disposition")
        for field in ("approver_identity", "rationale", "effective_from"):
            if not item.get(field):
                errors.append(f"{did}: approved decision is missing {field}")
        if not item.get("rejected_options_and_reasons"):
            errors.append(f"{did}: rejected options and reasons must be preserved")

    pending = [
        item["id"]
        for item in decisions
        if item.get("blocks_p1") and item.get("status") == "pending-human"
    ]
    if pending:
        errors.append(f"no P1 method decision should remain pending: {pending}")
    if status.get("blocking_decision_ids") != []:
        errors.append("p1-status blocking_decision_ids must be empty after D01-D14 approval")
    if status.get("status") != "pilot-authorized":
        errors.append("P1 status must be pilot-authorized after D01-D14 approval")
    if status.get("human_pass1_frozen") is not True or status.get("agent_blind_pass1_frozen") is not True:
        errors.append("Human and Agent Calibration passes must remain recorded as frozen")
    if status.get("held_out_or_sealed_data_accessed") is not False:
        errors.append("P1 Calibration must record no held-out or sealed data access")
    if status.get("effectiveness_claim_allowed") is not False:
        errors.append("P1 Calibration cannot allow effectiveness claims")
    return errors


def main() -> int:
    # The preserved adjudication bundle still records the four questions as
    # provisional at the time it was created. Current governance approval is
    # checked separately above; the historical data are not rewritten.
    legacy.validate_decision_state = validate_current_decision_state
    result = legacy.main()
    if result == 0:
        print(
            "P1 Calibration current-state validation passed: original passes and "
            "historical adjudication are preserved, while D01-D14 approval is "
            "validated against the current governance state."
        )
    return result


if __name__ == "__main__":
    raise SystemExit(main())
