#!/usr/bin/env python3
"""Validate the D13-D18 protocol artifacts while requiring the pilot to remain blocked."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
NEW = {f"PCT-P2-D{i:02d}" for i in range(13, 19)}
ALL = {f"PCT-P2-D{i:02d}" for i in range(1, 19)}
BLOCKERS = {"PCT-P2-PF-IDENTITY-01", "PCT-P2-PF-BUDGET-01", "PCT-P2-PF-REFERENCE-01"}
REQUIRED = [
    "governance/p2-human-approval-d13-d18-v0.1.json",
    "governance/p2-decision-register-v0.3.json",
    "governance/p2-natural-pilot-protocol-v0.1.json",
    "governance/p2-worker-profile-freeze-v0.1.json",
    "governance/p2-reference-custody-v0.1.json",
    "governance/p2-status-v0.3.json",
    "data/p2/natural-pilot/public-task-catalog-v0.1.json",
    "data/p2/natural-pilot/deterministic-validator-catalog-v0.1.json",
    "data/p2/natural-pilot/run-schedule-v0.1.json",
    "reports/p2/natural-pilot-preflight-v0.1.json",
    "schemas/pct-p2-natural-task-catalog-v0.1.schema.json",
    "schemas/pct-p2-worker-profile-freeze-v0.1.schema.json",
    "schemas/pct-p2-natural-pilot-preflight-v0.1.schema.json",
    "docs/p2/p2-natural-task-shadow-pilot-protocol-v0.1.md",
    "docs/p2/p2-preflight-input-request-v0.1.md",
]


def load(relative: str) -> dict:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{relative}: expected object")
    return value


def digest_without(value: dict, field: str) -> str:
    base = deepcopy(value)
    base.pop(field, None)
    raw = json.dumps(base, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def validate() -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"missing natural-pilot preflight artifact: {relative}")
    if errors:
        return errors

    approval = load("governance/p2-human-approval-d13-d18-v0.1.json")
    if approval.get("status") != "COMPLETE" or set(approval.get("approved_options", {})) != NEW:
        errors.append("D13-D18 approval record mismatch")
    if set(approval.get("approved_options", {}).values()) != {"A"}:
        errors.append("D13-D18 are not all option A")
    if approval.get("approval_source", {}).get("comment_id") != 5420758863:
        errors.append("D13-D18 approval source comment mismatch")
    if approval.get("natural_task_worker_calls_authorized") is not False:
        errors.append("approval record must not directly authorize Worker calls")

    register = load("governance/p2-decision-register-v0.3.json")
    if set(register.get("approved_decision_ids", [])) != ALL:
        errors.append("v0.3 register must bind D01-D18")
    new_records = {item.get("decision_id"): item for item in register.get("new_decisions", [])}
    if set(new_records) != NEW or any(item.get("selected_option") != "A" or item.get("status") != "APPROVED" for item in new_records.values()):
        errors.append("v0.3 register D13-D18 records mismatch")
    if set(register.get("open_normative_gate_ids", [])):
        errors.append("D13-D18 approval should leave no open normative gate in this pack")
    if set(register.get("operational_preflight_blockers", [])) != BLOCKERS:
        errors.append("v0.3 operational blocker set mismatch")

    catalog = load("data/p2/natural-pilot/public-task-catalog-v0.1.json")
    if catalog.get("catalog_digest") != digest_without(catalog, "catalog_digest"):
        errors.append("task catalog digest mismatch")
    tasks = catalog.get("tasks", [])
    if len(tasks) != 20 or catalog.get("task_count") != 20:
        errors.append("task catalog is not exactly 20 tasks")
    ids = [item.get("task_id") for item in tasks]
    if len(ids) != len(set(ids)):
        errors.append("task IDs are not unique")
    strata = Counter(item.get("stratum") for item in tasks)
    if strata != Counter({"HIGHLY_VERIFIABLE": 10, "SEMI_OPEN": 10}):
        errors.append(f"task strata mismatch: {dict(strata)}")
    for item in tasks:
        if item.get("privacy_class") != "PUBLIC_NON_SENSITIVE_SYNTHETIC" or item.get("network_access") is not False:
            errors.append(f"{item.get('task_id')}: public/non-sensitive/no-network invariant failed")
        goal = item.get("goal_contract", {})
        if not goal.get("hard_obligations") or not goal.get("required_outputs"):
            errors.append(f"{item.get('task_id')}: incomplete Goal Contract")
        if item.get("stratum") == "HIGHLY_VERIFIABLE" and not item.get("deterministic_validator_id"):
            errors.append(f"{item.get('task_id')}: missing deterministic validator")
        if item.get("stratum") == "SEMI_OPEN" and (item.get("reference_lane") != "TWO_BLINDED_HUMANS" or len(item.get("human_reference_rubric", [])) < 4):
            errors.append(f"{item.get('task_id')}: semi-open Reference rubric mismatch")

    validators = load("data/p2/natural-pilot/deterministic-validator-catalog-v0.1.json")
    if validators.get("validator_catalog_digest") != digest_without(validators, "validator_catalog_digest"):
        errors.append("validator catalog digest mismatch")
    if len(validators.get("validators", [])) != 10 or validators.get("semantic_model_calls") != 0:
        errors.append("deterministic validator catalog mismatch")

    schedule = load("data/p2/natural-pilot/run-schedule-v0.1.json")
    if schedule.get("schedule_digest") != digest_without(schedule, "schedule_digest"):
        errors.append("run schedule digest mismatch")
    runs = schedule.get("runs", [])
    if len(runs) != 60 or [item.get("sequence") for item in runs] != list(range(1, 61)):
        errors.append("run schedule must contain ordered sequence 1..60")
    pair_counts = Counter((item.get("task_id"), item.get("repetition")) for item in runs)
    if set(pair_counts.values()) != {1} or Counter(item.get("task_id") for item in runs) != Counter({task_id: 3 for task_id in ids}):
        errors.append("run schedule does not contain exactly three unique repetitions per task")
    if any(runs[i].get("task_id") == runs[i-1].get("task_id") for i in range(1, len(runs))):
        errors.append("adjacent schedule entries repeat the same task")
    if any(item.get("primary_analysis_unit") != "FIRST_CANDIDATE_STOP" or item.get("candidate_stop_capture_cap") != 2 for item in runs):
        errors.append("analysis-unit or Candidate-Stop cap mismatch")

    protocol = load("governance/p2-natural-pilot-protocol-v0.1.json")
    if protocol.get("protocol_digest") != digest_without(protocol, "protocol_digest"):
        errors.append("protocol digest mismatch")
    design = protocol.get("design", {})
    if (design.get("task_count"), design.get("planned_trajectories"), design.get("repetitions_per_task")) != (20, 60, 3):
        errors.append("protocol design mismatch")
    caps = protocol.get("fixed_resource_caps", {})
    if (caps.get("wall_clock_seconds"), caps.get("model_request_cap"), caps.get("tool_call_cap"), caps.get("candidate_stop_cap")) != (1800, 20, 50, 2):
        errors.append("fixed base caps mismatch")
    for pending in ("retry_policy", "context_window_tokens", "max_output_tokens", "per_trajectory_token_cap", "per_trajectory_monetary_cap"):
        if caps.get(pending) is not None:
            errors.append(f"{pending} must remain pending until exact profile freeze")
    if protocol.get("mode") != "SHADOW" or protocol.get("applied_to_runtime") is not False:
        errors.append("protocol crossed Shadow authority boundary")
    if protocol.get("semantic_auditor", {}).get("enabled") is not False:
        errors.append("Semantic Auditor must remain disabled")

    profile = load("governance/p2-worker-profile-freeze-v0.1.json")
    if profile.get("profile_freeze_digest") != digest_without(profile, "profile_freeze_digest"):
        errors.append("Worker profile freeze digest mismatch")
    if profile.get("status") != "BLOCKED_EXACT_IDENTITY_PENDING" or profile.get("substitute_model_allowed") is not False:
        errors.append("Worker profile must be blocked with substitution prohibited")
    exact = profile.get("exact_identity", {})
    if any(value is not None for value in exact.values()):
        errors.append("exact Worker identity fields must remain unresolved in this preflight snapshot")
    if profile.get("live_worker_model_calls_performed") != 0 or profile.get("live_worker_model_calls_authorized") is not False:
        errors.append("Worker profile record reports an unauthorized call")

    custody = load("governance/p2-reference-custody-v0.1.json")
    if custody.get("custody_digest") != digest_without(custody, "custody_digest"):
        errors.append("Reference custody digest mismatch")
    semi = custody.get("semi_open_lane", {})
    if custody.get("status") != "BLOCKED_INDEPENDENT_RATERS_UNASSIGNED" or custody.get("reference_opening_authorized") is not False:
        errors.append("Reference custody must remain blocked and closed")
    if any(semi.get(key, {}).get("assigned") is not False for key in ("rater_a", "rater_b", "adjudicator")):
        errors.append("Reference roles were unexpectedly assigned")

    report = load("reports/p2/natural-pilot-preflight-v0.1.json")
    if report.get("preflight_digest") != digest_without(report, "preflight_digest"):
        errors.append("preflight report digest mismatch")
    if report.get("status") != "BLOCKED" or set(report.get("blocker_ids", [])) != BLOCKERS:
        errors.append("preflight must be BLOCKED on the frozen three blockers")
    for field in ("live_worker_model_calls", "natural_task_runs", "reference_packets_opened", "semantic_auditor_calls"):
        if report.get(field) != 0:
            errors.append(f"preflight {field} must be zero")

    status = load("governance/p2-status-v0.3.json")
    if set(status.get("approved_decision_ids", [])) != ALL or status.get("preflight_status") != "BLOCKED":
        errors.append("active v0.3 status mismatch")
    if set(status.get("preflight_blocker_ids", [])) != BLOCKERS:
        errors.append("active status blocker set mismatch")
    for field in ("natural_task_shadow_measurement_authorized", "live_worker_model_calls_authorized", "semantic_audit_agent_authorized", "private_runtime_trace_collection_authorized", "reference_evaluator_opening_authorized", "online_intervention_authorized", "worker_behavior_change_authorized", "effectiveness_claim_allowed"):
        if status.get(field) is not False:
            errors.append(f"v0.3 status must keep {field}=false")

    for path in sorted((ROOT / "schemas").glob("pct-p2-*.schema.json")):
        value = load(path.relative_to(ROOT).as_posix())
        if value.get("$schema") != "https://json-schema.org/draft/2020-12/schema" or not value.get("$id"):
            errors.append(f"{path.name}: invalid schema header")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("P2 natural-pilot preflight validation failed:", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1
    print("P2 natural-pilot protocol validation passed: D13-D18 are materialized, 20 tasks and 60 trajectories are frozen, and the pilot remains BLOCKED pending exact Worker identity, profile-derived caps, and independent Reference custody; live model calls=0.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
