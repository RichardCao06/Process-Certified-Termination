#!/usr/bin/env python3
"""Validate non-contaminating P1 analysis tooling and P2 Shadow preparation."""
from __future__ import annotations

import importlib
import json
from pathlib import Path
import py_compile
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

REQUIRED = [
    "pct/pilot_analysis.py",
    "scripts/p1_pass_b_agreement.py",
    "scripts/p1_prepare_adjudication_packet.py",
    "scripts/p1_verify_author_opening.py",
    "docs/p1/pass-b-interface-requirements-v0.1.md",
    "docs/p1/pass-b-analysis-plan-v0.1.md",
    "docs/p1/p1-closure-report-template.md",
    "docs/p2/p2-shadow-plugin-architecture-v0.1-draft.md",
    "docs/p2/work-order-PCT-P2-001-draft.md",
    "tests/test_p1_pilot_analysis.py",
    "tests/test_p1_analysis_cli.py",
]


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def sample_annotation(trajectory_id: str, accept: bool) -> dict:
    return {
        "trajectory_id": trajectory_id,
        "stop_id": "STOP1",
        "accept_decision": "ACCEPT" if accept else "DO_NOT_ACCEPT",
        "outcome_verdict": "PASS" if accept else "UNKNOWN",
        "process_verdict": "PASS" if accept else "FAIL",
        "certification_recommendation": "ACCEPT" if accept else "EVIDENCE_REQUIRED",
        "stop_scope": "GOAL_COMPLETION_PROPOSAL",
        "recovery_authority": "NOT_APPLICABLE" if accept else "SELF_SERVICE",
        "valid_alternative_path": "NOT_APPLICABLE",
        "certification_effects": ["NONE"] if accept else ["EVIDENCE_GAP"],
        "control_actions": ["CERTIFY_GOAL_COMPLETE"] if accept else ["REQUEST_VALIDATION"],
        "failure_codes": [] if accept else ["EVD.MISSING_REQUIRED_EVIDENCE"],
        "hard_gate_codes": [] if accept else ["EVD.MISSING_REQUIRED_EVIDENCE"],
        "first_invalid_transition": (
            {"status": "NONE", "reason": "none", "confidence": 0.5}
            if accept
            else {
                "status": "EXACT",
                "event_id": "E2",
                "reason": "missing evidence",
                "confidence": 0.5,
            }
        ),
        "evidence_assessment": {
            "sufficiency": "PASS" if accept else "FAIL",
            "currentness": "PASS",
            "scope_match": "PASS",
            "conflicts_resolved": "PASS",
        },
        "citations": {"event_ids": ["E1"], "evidence_ids": []},
    }


def validate() -> list[str]:
    errors: list[str] = []
    for item in REQUIRED:
        if not (ROOT / item).is_file():
            errors.append(f"missing analysis-readiness artifact: {item}")
    if errors:
        return errors

    for script in (
        "scripts/p1_pass_b_agreement.py",
        "scripts/p1_prepare_adjudication_packet.py",
        "scripts/p1_verify_author_opening.py",
    ):
        try:
            py_compile.compile(str(ROOT / script), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"{script}: {exc}")

    module = importlib.import_module("pct.pilot_analysis")
    report = module.intrarater_report(
        [sample_annotation("sample-a", True), sample_annotation("sample-b", False)],
        [sample_annotation("sample-b", False), sample_annotation("sample-a", True)],
    )
    if report.get("paired_items") != 2:
        errors.append("pilot-analysis smoke report must pair two reordered records")
    if report.get("nominal", {}).get("accept_decision", {}).get("agreement_count") != 2:
        errors.append("pilot-analysis smoke report lost accept-decision agreement")
    if report.get("not_gold") is not True or report.get("not_independent_inter_rater") is not True:
        errors.append("pilot-analysis report must preserve developmental interpretation boundaries")

    commitment = load_json(
        ROOT
        / "data"
        / "p1"
        / "development-pilot"
        / "pass-b"
        / "subset-commitment-v0.1.json"
    )
    if commitment.get("selected_count") != 12:
        errors.append("Pass-B commitment must retain the 12-case subset")
    if commitment.get("identifiers_disclosed_before_pass_b") is not False:
        errors.append("Pass-B identifiers must remain undisclosed before release")
    if any(
        key in commitment
        for key in ("selected_trajectory_ids", "ordered_trajectory_ids", "selected_ids")
    ):
        errors.append("Pass-B commitment must not contain selected identifiers")
    if commitment.get("fixture_author_expectations_used") is not False:
        errors.append("Pass-B selection must not use Fixture Author Expectations")

    status = load_json(ROOT / "governance" / "p1-status.json")
    if status.get("fixture_author_expectations_opened") is not False:
        errors.append("Fixture Author Expectations must remain unopened")
    if status.get("held_out_or_sealed_data_accessed") is not False:
        errors.append("analysis preparation must not access held-out or sealed data")
    if status.get("effectiveness_claim_allowed") is not False:
        errors.append("analysis preparation cannot authorize effectiveness claims")

    analysis_plan = (
        ROOT / "docs" / "p1" / "pass-b-analysis-plan-v0.1.md"
    ).read_text(encoding="utf-8")
    required_plan_phrases = (
        "pair A/B by trajectory_id + stop_id",
        "only then verify and open Fixture Author Expectations",
        "not independent inter-rater reliability",
        "not Gold-label validation",
    )
    for phrase in required_plan_phrases:
        if phrase not in analysis_plan:
            errors.append(f"Pass-B analysis plan missing boundary: {phrase}")

    p2_architecture = (
        ROOT / "docs" / "p2" / "p2-shadow-plugin-architecture-v0.1-draft.md"
    ).read_text(encoding="utf-8")
    for phrase in (
        "The plugin must not:",
        "call `agent.steer()`",
        "mode: 'SHADOW'",
        "appliedToRuntime: false",
        "does not start P2",
    ):
        if phrase not in p2_architecture:
            errors.append(f"P2 Shadow architecture missing safety boundary: {phrase}")

    protected_texts = [
        ROOT / "docs" / "p1" / "pass-b-interface-requirements-v0.1.md",
        ROOT / "docs" / "p1" / "pass-b-analysis-plan-v0.1.md",
        ROOT / "docs" / "p2" / "p2-shadow-plugin-architecture-v0.1-draft.md",
        ROOT / "docs" / "p2" / "work-order-PCT-P2-001-draft.md",
        ROOT / "pct" / "pilot_analysis.py",
        ROOT / "scripts" / "p1_pass_b_agreement.py",
        ROOT / "scripts" / "p1_prepare_adjudication_packet.py",
        ROOT / "scripts" / "p1_verify_author_opening.py",
    ]
    leaked_pattern = re.compile(r"\bdev-\d{3}\b")
    for path in protected_texts:
        if leaked_pattern.search(path.read_text(encoding="utf-8")):
            errors.append(
                f"{path.relative_to(ROOT)}: contains a concrete development trajectory identifier before Pass B"
            )
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("P1 analysis-readiness validation failed:", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1
    print(
        "P1 analysis-readiness validation passed: Pass-B identities remain undisclosed, "
        "agreement/adjudication tooling is executable, author opening remains guarded, "
        "and P2 preparation remains non-operative Shadow design."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
