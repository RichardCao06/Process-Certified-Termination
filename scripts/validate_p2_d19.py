#!/usr/bin/env python3
"""Validate D19 approval, caps, least privilege, append-only provenance, and runtime boundaries."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "governance/p2-human-approval-d19-v0.1.json",
    "governance/p2-incident-PCT-P2-I02-v0.1.json",
    "governance/p2-operational-caps-v0.1.json",
    "governance/p2-worker-profile-freeze-v0.2.json",
    "governance/p2-engineering-smoke-authorization-v0.1.json",
    "governance/p2-decision-register-v0.4.json",
    "governance/p2-status-v0.4.json",
    "reports/p2/natural-pilot-preflight-v0.2.json",
    "data/p2/engineering-smoke/fixture-catalog-v0.1.json",
    "config/p2/deepseek-v4-pro-operational-profile-v0.2.json",
    "config/p2/d19-runtime-tool-catalog-v0.1.json",
    "config/p2/dsh-engineering-smoke.cordis.yml",
    "schemas/pct-p2-engineering-smoke-report-v0.2.schema.json",
    ".github/workflows/p2-engineering-smoke.yml",
]
DIGESTS = {
    "p2-human-approval-d19-v0.1.json": "approval_digest",
    "p2-incident-PCT-P2-I02-v0.1.json": "incident_digest",
    "p2-operational-caps-v0.1.json": "caps_digest",
    "p2-worker-profile-freeze-v0.2.json": "profile_freeze_digest",
    "p2-engineering-smoke-authorization-v0.1.json": "authorization_digest",
    "p2-decision-register-v0.4.json": "register_digest",
    "p2-status-v0.4.json": "status_digest",
    "natural-pilot-preflight-v0.2.json": "preflight_digest",
    "fixture-catalog-v0.1.json": "catalog_digest",
    "deepseek-v4-pro-operational-profile-v0.2.json": "profile_digest",
    "d19-runtime-tool-catalog-v0.1.json": "catalog_digest",
}


def load(relative: str) -> dict:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{relative}: expected object")
    return value


def digest(value: dict, field: str) -> str:
    material = deepcopy(value); material.pop(field, None)
    return hashlib.sha256(json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def sha(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def validate() -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"missing {relative}")
    if errors:
        return errors
    for relative in REQUIRED:
        field = DIGESTS.get(Path(relative).name)
        if field:
            value = load(relative)
            if value.get(field) != digest(value, field):
                errors.append(f"{relative}: digest mismatch")
    approval = load("governance/p2-human-approval-d19-v0.1.json")
    source = approval.get("approval_source", {})
    if approval.get("approved_options") != {"PCT-P2-D19": "A"} or source.get("comment_id") != 5423290038 or source.get("created_at") != "2026-08-26T09:26:28Z":
        errors.append("D19 approval source mismatch")
    values = approval.get("approved_operational_values", {})
    if [values.get(key) for key in ("operational_context_window_tokens", "operational_max_output_tokens", "per_trajectory_cumulative_token_cap", "per_trajectory_monetary_cap")] != [128000, 16000, 200000, 30]:
        errors.append("D19 approved caps mismatch")
    caps = load("governance/p2-operational-caps-v0.1.json")
    limits = caps["per_trajectory_caps"]
    retry = caps["retry_policy"]
    if [limits[key] for key in ("context_window_tokens", "max_output_tokens_per_request", "cumulative_tokens", "monetary_cap")] != [128000, 16000, 200000, 30]:
        errors.append("operational caps mismatch")
    if retry.get("maximum_retries_after_original") != 2 or retry.get("delay_seconds") != [2, 8] or retry.get("quality_based_retry") is not False or retry.get("dsh_internal_max_retries") != 0:
        errors.append("retry policy mismatch")
    if caps["monetary_guard"].get("token_cap_implies_monetary_cap") is not True:
        errors.append("token cap does not conservatively dominate monetary cap")
    tool_catalog = load("config/p2/d19-runtime-tool-catalog-v0.1.json")
    expected = ["edit", "read", "write"]
    if tool_catalog.get("model_facing_tool_names") != expected or tool_catalog.get("network_access_for_model_tools") is not False or tool_catalog.get("runtime_secret_access_for_worker") is not False:
        errors.append("runtime tool catalog is not exact least privilege")
    config_text = (ROOT / "config/p2/dsh-engineering-smoke.cordis.yml").read_text(encoding="utf-8")
    for required in ("maxRetries: 0", "contextWindow: 128000", "maxTokens: 16000", "id: bash", "id: tool-subagent", "id: tool-workflow", "id: tool-ralph", "id: tool-todo"):
        if required not in config_text:
            errors.append(f"runtime config missing {required}")
    if config_text.count("disabled: true") < 7:
        errors.append("runtime config did not disable the expected excess capabilities")
    profile = load("config/p2/deepseek-v4-pro-operational-profile-v0.2.json")
    freeze = load("governance/p2-worker-profile-freeze-v0.2.json")
    bindings = freeze["artifact_bindings"]
    checks = {
        "operational_profile_sha256": sha("config/p2/deepseek-v4-pro-operational-profile-v0.2.json"),
        "system_prompt_sha256": sha("config/p2/natural-pilot-system-prompt-v0.1.txt"),
        "intended_capability_catalog_sha256": sha("config/p2/natural-pilot-tool-catalog-v0.1.json"),
        "runtime_tool_catalog_sha256": sha("config/p2/d19-runtime-tool-catalog-v0.1.json"),
        "engineering_runtime_config_sha256": sha("config/p2/dsh-engineering-smoke.cordis.yml"),
    }
    for key, actual in checks.items():
        if bindings.get(key) != actual:
            errors.append(f"profile freeze binding mismatch: {key}")
    if profile.get("profile_digest") != digest(profile, "profile_digest"):
        errors.append("operational profile digest mismatch")
    fixtures = load("data/p2/engineering-smoke/fixture-catalog-v0.1.json")
    if fixtures.get("fixture_count") != 2 or len(fixtures.get("fixtures", [])) != 2 or fixtures.get("excluded_from_60_trajectory_schedule") is not True or fixtures.get("primary_analysis_denominator") is not False:
        errors.append("engineering fixture isolation mismatch")
    expected_proposal = {"stop_scope": "GOAL_COMPLETION_PROPOSAL", "recovery_authority": "NOT_APPLICABLE", "worker_claim": "COMPLETE", "claims_goal_complete": True}
    if any(item.get("expected_candidate_stop_proposal") != expected_proposal for item in fixtures["fixtures"]):
        errors.append("fixture Candidate-Stop proposal mismatch")
    status = load("governance/p2-status-v0.4.json")
    if status.get("engineering_smoke_scoped_worker_calls_authorized") is not True or status.get("engineering_smoke_trajectory_cap") != 2:
        errors.append("engineering smoke authorization mismatch")
    for field in ("natural_task_shadow_measurement_authorized", "live_primary_worker_model_calls_authorized", "semantic_audit_agent_authorized", "reference_evaluator_opening_authorized", "online_intervention_authorized", "worker_behavior_change_authorized", "effectiveness_claim_allowed"):
        if status.get(field) is not False:
            errors.append(f"{field} must remain false")
    raw = load("reports/p2/deepseek-provider-introspection-v0.1.json")
    actual_candidate = sha("config/p2/deepseek-v4-pro-profile-candidate-v0.1.json")
    if raw["frozen_input_artifacts"]["profile_candidate_sha256"] != actual_candidate:
        errors.append("historical provider-introspection profile binding mismatch")
    incident = load("governance/p2-incident-PCT-P2-I02-v0.1.json")
    facts = incident.get("facts", {})
    if incident.get("status") != "RESOLVED_BY_REPLACEMENT_PACKAGE_BEFORE_COMMIT":
        errors.append("PCT-P2-I02 replacement-package resolution status mismatch")
    if facts.get("profile_hashes_match") is not True or facts.get("original_v0_2_validator_incorrectly_required_a_mismatch") is not True:
        errors.append("PCT-P2-I02 corrected facts are incomplete")
    runner = (ROOT / "scripts/run_p2_engineering_smoke.py").read_text(encoding="utf-8")
    for needle in ("os.environ.pop(\"DEEPSEEK_API_KEY\", None)", "local_proxy_token", "real DeepSeek key reached Worker subprocess environment", "RUNTIME_TOOL_CATALOG_MISMATCH", "MISSING_USAGE", "read_exact_proposal"):
        if needle not in runner:
            errors.append(f"runner missing protection: {needle}")
    workflow = (ROOT / ".github/workflows/p2-engineering-smoke.yml").read_text(encoding="utf-8")
    for needle in ("pull_request:", "workflow_dispatch:", "environment: p2-natural-pilot", "DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}", "make validate", "--dsh-source _vendor/deepseek-harness", "11d5960a326750d5838078e36cf38b85af677262", "a26af69be951a213d495a4c3e4e4022e16d87065", "49933ea5288caeca8642d1e84afbd3f7d6820020", "ea165f8d65b6e75b540449e92b4886f43607fa02"):
        if needle not in workflow:
            errors.append(f"workflow missing {needle}")
    if workflow.index("make validate") > workflow.index("pnpm install"):
        errors.append("full repository validation must precede DSH install and model access")
    if workflow.count("make validate") < 2:
        errors.append("workflow must run full validation both before model access and after generated evidence")
    # Repository leakage is evaluated over Git-tracked files only. Ignored local
    # files (for example .venv or a developer-only .env) are not commit content.
    # The left boundary prevents ordinary words such as risk-assessment from
    # being interpreted as credentials merely because they contain ``sk-``.
    secret_pattern = re.compile(r"(?<![A-Za-z0-9_])sk-[A-Za-z0-9_-]{20,}")
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).split(b"\0")
    secret_paths: list[str] = []
    for raw_path in tracked:
        if not raw_path:
            continue
        relative = raw_path.decode("utf-8", errors="strict")
        candidate = ROOT / relative
        if not candidate.is_file():
            continue
        content = candidate.read_text(encoding="utf-8", errors="ignore")
        if secret_pattern.search(content):
            secret_paths.append(relative)
    if secret_paths:
        errors.append(f"secret-like token present in tracked files: {sorted(secret_paths)}")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("P2 D19 validation failed:", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1
    print("P2 D19 validation passed: D19-A is frozen, the Worker secret and tool surfaces are isolated, two engineering-only trajectories are authorized, and the primary 60-run pilot remains unauthorized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
