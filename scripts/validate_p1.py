#!/usr/bin/env python3
"""Deterministic integrity checks for the PCT P1 development foundation."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pct.agreement import agreement_report  # noqa: E402
from pct.validation import (  # noqa: E402
    TaxonomyIndex,
    lint_trajectory,
    load_json,
    validate_annotation,
    validate_taxonomy,
    validate_trajectory,
)

REQUIRED_FILES = [
    "docs/p1/README.md",
    "docs/p1/work-order-PCT-P1-001.md",
    "docs/p1/human-decision-pack.md",
    "docs/p1/decision-register.md",
    "docs/p1/failure-taxonomy-v0.1-draft.md",
    "docs/p1/annotation-codebook-v0.1-draft.md",
    "docs/p1/annotation-feasibility-protocol-v0.1-draft.md",
    "docs/p1/trace-observation-model-v0.1-draft.md",
    "docs/p1/deepseek-harness-event-mapping.md",
    "docs/p1/synthetic-fixture-catalog.md",
    "docs/p1/red-team-review.md",
    "docs/p1/p1-exit-gate.md",
    "governance/p1-decision-register.json",
    "governance/p1-status.json",
    "taxonomy/process-failure-taxonomy-v0.1-draft.json",
    "schemas/pct-trajectory.schema.json",
    "schemas/pct-annotation.schema.json",
    "schemas/pct-taxonomy.schema.json",
    "schemas/pct-adjudication.schema.json",
    "schemas/p1-decision-register.schema.json",
    "schemas/p1-status.schema.json",
    "pct/validation.py",
    "pct/agreement.py",
    "pct/dsh_mapping.py",
    "scripts/lint_trajectory.py",
    "scripts/annotation_agreement.py",
    "data/p1/README.md",
    "data/p1/annotations/fixture-author.jsonl",
    "tests/fixtures/p1/expected-lints.json",
    "docs/templates/p1-annotation-adjudication.md",
    "docs/templates/p1-taxonomy-change-record.md",
    "reports/p1/synthetic-smoke-report.json",
    "reports/p1/agreement-smoke-report.json",
]
ALLOWED_DECISION_STATUS = {"pending-human", "approved", "rejected", "deferred"}
AGENT_ROLE_WORDS = {"Agent", "Builder", "Auditor", "Red-Team", "Experimental"}


def read_jsonl(path: Path) -> list[dict]:
    items: list[dict] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_no}: expected object")
        items.append(value)
    return items


def validate_required_files() -> list[str]:
    return [f"missing required P1 artifact: {path}" for path in REQUIRED_FILES if not (ROOT / path).is_file()]


def validate_decisions(register: dict) -> list[str]:
    errors: list[str] = []
    if register.get("project_id") != "PCT" or register.get("phase") != "P1":
        errors.append("P1 decision register must identify project PCT and phase P1")
    decisions = register.get("decisions")
    if not isinstance(decisions, list) or not decisions:
        return errors + ["P1 decision register requires decisions"]
    ids = []
    for item in decisions:
        did = item.get("id") if isinstance(item, dict) else None
        ids.append(did)
        if not isinstance(did, str) or not re.fullmatch(r"PCT-P1-D\d{2}", did):
            errors.append(f"invalid P1 decision id: {did!r}")
            continue
        if item.get("status") not in ALLOWED_DECISION_STATUS:
            errors.append(f"{did}: invalid status")
        owner = item.get("owner_role")
        if item.get("normative") is True and (
            not isinstance(owner, str) or any(word in owner for word in AGENT_ROLE_WORDS)
        ):
            errors.append(f"{did}: normative decision must have a human owner role")
        options = item.get("options")
        if not isinstance(options, list) or len(options) < 2:
            errors.append(f"{did}: at least two options are required")
            continue
        option_ids = {option.get("id") for option in options if isinstance(option, dict)}
        if item.get("agent_recommendation") not in option_ids:
            errors.append(f"{did}: recommendation must reference a declared option")
        if item.get("status") in {"approved", "rejected"}:
            if item.get("human_decision") not in option_ids:
                errors.append(f"{did}: resolved decision must select a declared option")
            for field in ("rationale", "approver_identity", "effective_from"):
                if not item.get(field):
                    errors.append(f"{did}: resolved decision missing {field}")
            if not item.get("rejected_options_and_reasons"):
                errors.append(f"{did}: resolved decision must preserve rejected options and reasons")
        elif item.get("human_decision") is not None:
            errors.append(f"{did}: unresolved decision cannot contain an effective human_decision")
    expected = [f"PCT-P1-D{i:02d}" for i in range(1, len(decisions) + 1)]
    if ids != expected:
        errors.append(f"P1 decision ids must be contiguous and ordered: expected {expected}, got {ids}")
    return errors


def validate_status(status: dict, register: dict, p0_status: dict) -> list[str]:
    errors: list[str] = []
    if p0_status.get("status") != "approved" or p0_status.get("next_phase_authorized") is not True:
        errors.append("P1 cannot exist unless P0 is approved and P1 is authorized")
    if status.get("project_id") != "PCT" or status.get("phase") != "P1":
        errors.append("P1 status must identify project PCT and phase P1")
    commit = status.get("selected_configuration", {}).get("harness_commit")
    if commit != "141eb6fef83422698aef7a981029e843e8161534":
        errors.append("P1 selected harness commit differs from approved P0 configuration")
    pending = [item["id"] for item in register["decisions"] if item.get("blocks_p1") and item.get("status") == "pending-human"]
    if status.get("blocking_decision_ids") != pending:
        errors.append("P1 status blocker list must match pending blocking decisions")
    expected = "agent-foundation-complete-human-gate-pending" if pending else "pilot-authorized"
    if status.get("status") != expected:
        errors.append(f"P1 status must be {expected!r} for current decisions")
    if status.get("held_out_or_sealed_data_accessed") is not False:
        errors.append("P1 foundation must record no held-out or sealed data access")
    if status.get("effectiveness_claim_allowed") is not False:
        errors.append("P1 foundation cannot allow effectiveness claims")
    return errors


def validate_taxonomy_and_data() -> list[str]:
    errors: list[str] = []
    taxonomy_data = load_json(ROOT / "taxonomy/process-failure-taxonomy-v0.1-draft.json")
    for issue in validate_taxonomy(taxonomy_data):
        errors.append(f"taxonomy {issue.code} at {issue.location}: {issue.message}")
    taxonomy = TaxonomyIndex.from_data(taxonomy_data)
    fixture_dir = ROOT / "data/p1/synthetic"
    fixtures = sorted(fixture_dir.glob("*.json"))
    if len(fixtures) < 5:
        errors.append("P1 requires at least five controlled synthetic fixtures")
    expected = load_json(ROOT / "tests/fixtures/p1/expected-lints.json")
    trajectories: dict[str, dict] = {}
    filenames = {path.name for path in fixtures}
    if set(expected) != filenames:
        errors.append(f"expected-lints keys must match fixture files: expected={sorted(expected)}, files={sorted(filenames)}")
    for path in fixtures:
        trajectory = load_json(path)
        trajectories[trajectory.get("trajectory_id", path.stem)] = trajectory
        structural = validate_trajectory(trajectory)
        for issue in structural:
            errors.append(f"{path.relative_to(ROOT)} {issue.code} at {issue.location}: {issue.message}")
        source_class = trajectory.get("task", {}).get("source_class")
        if source_class in {"HELD_OUT", "SEALED"}:
            errors.append(f"{path.relative_to(ROOT)}: P1 fixture may not use {source_class}")
        visibility = trajectory.get("run", {}).get("visibility_policy", {})
        if any(visibility.get(field) is True for field in ("hidden_evaluator_visible", "gold_labels_visible", "other_condition_outputs_visible")):
            errors.append(f"{path.relative_to(ROOT)}: prohibited evaluator visibility")
        actual_codes = sorted(item.code for item in lint_trajectory(trajectory)) if not structural else []
        expected_codes = sorted(expected.get(path.name, []))
        if actual_codes != expected_codes:
            errors.append(f"{path.name}: lint mismatch expected={expected_codes}, actual={actual_codes}")
    valid_path = load_json(fixture_dir / "valid-alternative-path.json")
    if lint_trajectory(valid_path):
        errors.append("valid alternate-path negative control must not produce deterministic findings")

    annotations = read_jsonl(ROOT / "data/p1/annotations/fixture-author.jsonl")
    if len(annotations) != len(fixtures):
        errors.append("fixture-author annotations must cover every synthetic fixture exactly once")
    seen_pairs = set()
    for annotation in annotations:
        pair = (annotation.get("trajectory_id"), annotation.get("stop_id"))
        if pair in seen_pairs:
            errors.append(f"duplicate fixture annotation pair: {pair}")
        seen_pairs.add(pair)
        trajectory = trajectories.get(annotation.get("trajectory_id"))
        if trajectory is None:
            errors.append(f"annotation references unknown trajectory {annotation.get('trajectory_id')!r}")
            continue
        for issue in validate_annotation(annotation, trajectory, taxonomy):
            errors.append(f"annotation {annotation.get('annotation_id')} {issue.code} at {issue.location}: {issue.message}")
        if annotation.get("annotator", {}).get("role") != "FIXTURE_AUTHOR":
            errors.append("engineering fixture expectations must be explicitly labeled FIXTURE_AUTHOR")

    left = read_jsonl(ROOT / "tests/fixtures/p1/annotator-a.jsonl")
    right = read_jsonl(ROOT / "tests/fixtures/p1/annotator-b.jsonl")
    report = agreement_report(left, right)
    if report.get("paired_items") != len(fixtures):
        errors.append("agreement smoke test must pair every fixture")
    return errors


def validate_research_boundaries() -> list[str]:
    errors: list[str] = []
    codebook = (ROOT / "docs/p1/annotation-codebook-v0.1-draft.md").read_text(encoding="utf-8")
    if "not independent proof" not in codebook:
        errors.append("codebook must state that Worker checkpoints are not independent proof")
    readme = (ROOT / "docs/p1/README.md").read_text(encoding="utf-8")
    if "does not make an effectiveness claim" not in readme:
        errors.append("P1 README must preserve the no-effectiveness-claim boundary")
    gate = (ROOT / "docs/p1/p1-exit-gate.md").read_text(encoding="utf-8")
    if "P1 is not complete" not in gate:
        errors.append("P1 Exit Gate must explicitly state that P1 is not complete")
    if "independent inter-rater reliability" not in gate or "Gold-label validation" not in gate:
        errors.append("P1 Exit Gate must preserve intra-rater and non-Gold interpretation boundaries")
    return errors


def main() -> int:
    errors = validate_required_files()
    try:
        register = load_json(ROOT / "governance/p1-decision-register.json")
        status = load_json(ROOT / "governance/p1-status.json")
        p0_status = load_json(ROOT / "governance/p0-status.json")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(str(exc))
    else:
        errors.extend(validate_decisions(register))
        errors.extend(validate_status(status, register, p0_status))
    try:
        errors.extend(validate_taxonomy_and_data())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(str(exc))
    errors.extend(validate_research_boundaries())
    if errors:
        print("P1 validation failed:", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1
    print("P1 validation passed: development foundation is internally consistent; human Gate remains pending.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
