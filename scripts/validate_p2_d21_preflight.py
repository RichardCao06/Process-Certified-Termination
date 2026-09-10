#!/usr/bin/env python3
"""Validate the D21 no-model evidence freeze and pending human gate."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "reports/p2/cordis-config-boot-diagnostic-v0.1.json",
    "reports/p2/official-patch-no-model-validation-v0.1.json",
    "config/p2/dsh-engineering-smoke.patch-v0.2.yml",
    "docs/p2/archives/p2-engineering-smoke-d19-workflow-v0.1.yml",
    ".github/workflows/p2-engineering-smoke.yml",
    "governance/p2-incident-PCT-P2-I04-v0.1.json",
    "governance/p2-no-model-config-diagnostic-freeze-v0.1.json",
    "governance/p2-official-patch-validation-freeze-v0.1.json",
    "governance/p2-decision-register-v0.6.json",
    "governance/p2-status-v0.7.json",
    "docs/p2/p2-human-decision-pack-d21-v0.2.md",
]

EXPECTED = {
    "diagnostic_file_sha256": "1609a6195f0599522bd42cbf850894c13795b0d875c894e286787ef94d573487",
    "diagnostic_report_digest": "1997cc79cd4e28ac3cd12ba9e75ea7efef472d33a802bd5ece6520cf5ff2240b",
    "official_file_sha256": "fe8e0e24c1ad702428ec75e19771668057a839492882429bc1d47102041e3613",
    "official_report_digest": "d363f4f2f7bc776f800135531ea9136176eaafbb4cac4c4323238f0cd5004a2a",
    "old_workflow_git_blob": "c36d6e16c28cedd04d325ac5a0b168458fc2362b",
    "patch_git_blob": "a5334a2d5ae57f67ef3f0df2d7a6eddb466169b9",
}


def load(relative: str) -> dict:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{relative}: expected object")
    return value


def sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def git_blob(relative: str) -> str:
    return subprocess.check_output(["git", "hash-object", relative], cwd=ROOT, text=True).strip()


def canonical_digest(value: dict, field: str) -> str:
    material = deepcopy(value)
    material.pop(field, None)
    return hashlib.sha256(json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def uncommented_yaml(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))


def zero_boundary(boundary: dict) -> bool:
    zero_fields = (
        "model_turns_executed",
        "provider_requests_executed",
        "engineering_fixture_runs",
        "primary_schedule_runs",
        "reference_packets_opened",
        "semantic_auditor_calls",
    )
    return (
        boundary.get("deepseek_environment_secret_used") is False
        and boundary.get("real_provider_credential_available") is False
        and all(boundary.get(field) == 0 for field in zero_fields)
        and boundary.get("runtime_application") is False
    )


def validate() -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"missing {relative}")
    if errors:
        return errors

    diagnostic = load("reports/p2/cordis-config-boot-diagnostic-v0.1.json")
    if sha256("reports/p2/cordis-config-boot-diagnostic-v0.1.json") != EXPECTED["diagnostic_file_sha256"]:
        errors.append("diagnostic file SHA mismatch")
    if diagnostic.get("report_digest") != EXPECTED["diagnostic_report_digest"]:
        errors.append("diagnostic report digest mismatch")
    scenarios = {item.get("scenario"): item for item in diagnostic.get("scenarios", [])}
    if diagnostic.get("classification") != "OVERLAY_CONTENT_OR_PATCH_SEMANTICS_FAILURE":
        errors.append("diagnostic classification mismatch")
    if scenarios.get("base", {}).get("status") != "PASS":
        errors.append("frozen DSH base did not pass")
    if scenarios.get("external-overlay", {}).get("status") != "FAIL" or scenarios.get("in-tree-overlay", {}).get("status") != "FAIL":
        errors.append("failed overlay was not reproduced in both locations")
    if not zero_boundary(diagnostic.get("safety_boundary", {})):
        errors.append("diagnostic escaped the zero-model safety boundary")

    official = load("reports/p2/official-patch-no-model-validation-v0.1.json")
    if sha256("reports/p2/official-patch-no-model-validation-v0.1.json") != EXPECTED["official_file_sha256"]:
        errors.append("official patch report file SHA mismatch")
    if official.get("report_digest") != EXPECTED["official_report_digest"] or official.get("status") != "PASS":
        errors.append("official patch validation is not frozen PASS")
    if official.get("model_facing_tool_names") != ["edit", "read", "write"] or official.get("exact_tool_boundary") is not True:
        errors.append("official patch tool boundary mismatch")
    if official.get("missing_or_unmounted_required_ids") != [] or official.get("missing_or_mounted_disabled_ids") != []:
        errors.append("official patch plugin boundary mismatch")
    if not all(official.get("hardening_checks", {}).values()) or not all(official.get("adapter_checks", {}).values()):
        errors.append("official patch hardening/profile checks incomplete")
    if not zero_boundary(official.get("safety_boundary", {})):
        errors.append("official patch validation escaped the zero-model safety boundary")

    if git_blob("config/p2/dsh-engineering-smoke.patch-v0.2.yml") != EXPECTED["patch_git_blob"]:
        errors.append("official patch blob changed")
    if git_blob("docs/p2/archives/p2-engineering-smoke-d19-workflow-v0.1.yml") != EXPECTED["old_workflow_git_blob"]:
        errors.append("archived D19 workflow changed")

    active = uncommented_yaml((ROOT / ".github/workflows/p2-engineering-smoke.yml").read_text(encoding="utf-8"))
    for forbidden in ("pull_request:", "environment: p2-natural-pilot", "secrets.DEEPSEEK_API_KEY", "run_p2_engineering_smoke.py", "pnpm install"):
        if forbidden in active:
            errors.append(f"active D19 tombstone still exposes {forbidden}")
    for required in ("workflow_dispatch:", "authorization-consumed", "exit 1", "PCT-P2-D21"):
        if required not in active:
            errors.append(f"active D19 tombstone missing {required}")

    for relative, field in (
        ("governance/p2-incident-PCT-P2-I04-v0.1.json", "incident_digest"),
        ("governance/p2-no-model-config-diagnostic-freeze-v0.1.json", "freeze_digest"),
        ("governance/p2-official-patch-validation-freeze-v0.1.json", "freeze_digest"),
        ("governance/p2-decision-register-v0.6.json", "register_digest"),
        ("governance/p2-status-v0.7.json", "status_digest"),
    ):
        value = load(relative)
        if value.get(field) != canonical_digest(value, field):
            errors.append(f"{relative}: digest mismatch")

    incident = load("governance/p2-incident-PCT-P2-I04-v0.1.json")
    if incident.get("status") != "DIAGNOSED_NO_MODEL_REPAIR_CANDIDATE_VALIDATED_D21_PENDING":
        errors.append("I04 status mismatch")
    if incident.get("root_cause", {}).get("classification") != "ROOT_INCLUDE_OWN_PATH_JS_EXPRESSION_NOT_EVALUATED":
        errors.append("I04 root-cause classification mismatch")

    register = load("governance/p2-decision-register-v0.6.json")
    if register.get("approved_decision_ids") != [f"PCT-P2-D{i:02d}" for i in range(1, 21)]:
        errors.append("D01-D20 approval lineage changed")
    if register.get("open_normative_gate_ids") != ["PCT-P2-D21"]:
        errors.append("D21 is not the sole open normative gate")

    status = load("governance/p2-status-v0.7.json")
    if status.get("status") != "D21_BOUNDED_OFFICIAL_PATCH_RERUN_DECISION_PENDING":
        errors.append("active P2 status mismatch")
    for field in (
        "additional_engineering_worker_calls_authorized",
        "natural_task_shadow_measurement_authorized",
        "live_primary_worker_model_calls_authorized",
        "semantic_audit_agent_authorized",
        "reference_evaluator_opening_authorized",
        "online_intervention_authorized",
        "worker_behavior_change_authorized",
        "effectiveness_claim_allowed",
    ):
        if status.get(field) is not False:
            errors.append(f"{field} must remain false before D21")
    if status.get("primary_schedule_runs_completed") != 0:
        errors.append("primary schedule run count changed")

    pack = (ROOT / "docs/p2/p2-human-decision-pack-d21-v0.2.md").read_text(encoding="utf-8")
    for needle in ("方案 A", "方案 B", "方案 C", "PCT-P2-D21: A", "60 条正式"):
        if needle not in pack:
            errors.append(f"D21 decision pack missing {needle}")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("P2 D21 preflight validation failed:", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1
    print("P2 D21 preflight passed: no-model root cause and official patch boundary are frozen; D19 is fail-closed; D21 remains the sole human gate; primary/model/reference/online authorities remain closed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
