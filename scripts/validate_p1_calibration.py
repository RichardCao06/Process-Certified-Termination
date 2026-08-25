#!/usr/bin/env python3
"""Validate P1 calibration, blind-pass, adjudication, and v0.2 regression artifacts."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_BUNDLE_TEMP: tempfile.TemporaryDirectory[str] | None = None


def _prepare_data_root() -> Path:
    expanded = ROOT / "data" / "p1" / "calibration" / "calibration-inputs-v0.1.json"
    if expanded.is_file() and os.environ.get("PCT_FORCE_CALIBRATION_BUNDLE") != "1":
        return ROOT
    bundle_dir = ROOT / "data" / "p1" / "calibration"
    manifest = json.loads((bundle_dir / "bundle-manifest.json").read_text(encoding="utf-8"))
    encoded = "".join(
        "".join((bundle_dir / part).read_text(encoding="utf-8").split())
        for part in manifest["parts"]
    )
    archive = base64.b64decode(encoded, validate=True)
    if hashlib.sha256(archive).hexdigest() != manifest["sha256"]:
        raise ValueError("calibration data bundle SHA-256 mismatch")
    global _BUNDLE_TEMP
    _BUNDLE_TEMP = tempfile.TemporaryDirectory(prefix="pct-p1-calibration-")
    archive_path = Path(_BUNDLE_TEMP.name) / manifest["decoded_filename"]
    archive_path.write_bytes(archive)
    with tarfile.open(archive_path, "r:gz") as tf:
        root = Path(_BUNDLE_TEMP.name).resolve()
        for member in tf.getmembers():
            target = (root / member.name).resolve()
            if root not in target.parents and target != root:
                raise ValueError(f"unsafe bundle path: {member.name}")
        tf.extractall(root, filter="data")
    return root


DATA_ROOT = _prepare_data_root()
CAL = DATA_ROOT / "data" / "p1" / "calibration"
REG = DATA_ROOT / "data" / "p1" / "regression"

REQUIRED = [
    "docs/p1/calibration-recommendation-acceptance-record.md",
    "docs/p1/calibration-adjudication-report-v0.1.md",
    "docs/p1/post-calibration-human-decision-pack.md",
    "docs/p1/annotation-codebook-v0.2-draft.md",
    "docs/p1/trace-observation-model-v0.2-draft.md",
    "docs/p1/taxonomy-migration-v0.1-to-v0.2.md",
    "data/p1/calibration/bundle-manifest.json",
    "data/p1/calibration/bundle-parts/part-00",
    "data/p1/calibration/bundle-parts/part-01",
    "data/p1/calibration/bundle-parts/part-02",
    "data/p1/calibration/bundle-parts/part-03",
    "data/p1/calibration/bundle-parts/part-04",
    "schemas/pct-annotation-v0.2.schema.json",
    "schemas/pct-adjudication-v0.2.schema.json",
    "schemas/pct-trace-extension-v0.2.schema.json",
]

EFFECTS = {
    "HARD_VIOLATION", "EVIDENCE_GAP", "OUTCOME_FAILURE",
    "SOFT_QUALITY_ISSUE", "LIMITATION", "NONE", "UNKNOWN",
}
RECOMMENDATIONS = {
    "ACCEPT", "CONTINUE", "EVIDENCE_REQUIRED", "HUMAN_REQUIRED",
    "BLOCKED", "NO_PROGRESS", "UNDETERMINED",
}
VERDICTS = {"PASS", "FAIL", "UNKNOWN", "NOT_APPLICABLE"}
ALT_PATH = {"YES", "NO", "UNKNOWN", "NOT_APPLICABLE"}
STOP_SCOPES = {
    "TURN_STOP", "GOAL_COMPLETION_PROPOSAL", "HUMAN_ESCALATION",
    "NO_FURTHER_ACTION_PROPOSAL", "BLOCKER_PROPOSAL", "BUDGET_STOP", "OTHER",
}
CONTROL_ACTIONS = {
    "CERTIFY_GOAL_COMPLETE", "CLOSE_GOAL", "WITHHOLD_CERTIFICATION",
    "KEEP_GOAL_ACTIVE", "KEEP_O1_ATTEMPTED", "REOPEN_O1", "REOPEN_O2", "REQUEST_VALIDATION",
    "REQUEST_FRESH_VALIDATION", "REQUEST_SYSTEM_WIDE_VALIDATION",
    "CONTINUE_REPAIR", "CONTINUE_DIAGNOSIS_AND_REPAIR", "REVALIDATE",
    "REQUEST_HUMAN_DECISION", "PAUSE_GATED_ACTION",
    "REQUEST_RECOVERY_AUTHORITY_METADATA", "PRESERVE_ADVERSE_EVIDENCE",
    "PRESERVE_INCIDENT_RECORD", "ESCALATE_TO_HUMAN",
}


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected object")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_required() -> list[str]:
    return [f"missing calibration artifact: {item}" for item in REQUIRED if not (ROOT / item).is_file()]


def taxonomy_index() -> tuple[set[str], set[str]]:
    data = load_json(ROOT / "taxonomy/process-failure-taxonomy-v0.1-draft.json")
    codes: set[str] = set()
    hard: set[str] = set()
    for family in data.get("families", []):
        for item in family.get("codes", []):
            code = item.get("code")
            if isinstance(code, str):
                codes.add(code)
                if item.get("candidate_hard_gate") is True:
                    hard.add(code)
    return codes, hard


def validate_decision_state() -> list[str]:
    errors: list[str] = []
    register = load_json(ROOT / "governance/p1-decision-register.json")
    status = load_json(ROOT / "governance/p1-status.json")
    decisions = register.get("decisions", [])
    ids = [item.get("id") for item in decisions]
    expected = [f"PCT-P1-D{i:02d}" for i in range(1, 15)]
    if ids != expected:
        errors.append(f"P1 decisions must be D01-D14 in order: got {ids}")
    for item in decisions[:10]:
        if item.get("status") != "approved" or item.get("human_decision") != "A":
            errors.append(f"{item.get('id')}: D01-D10 must preserve the approved A decision")
        if not item.get("approver_identity") or not item.get("rationale"):
            errors.append(f"{item.get('id')}: approved decision is missing provenance")
    for item in decisions[10:]:
        if item.get("status") != "pending-human" or item.get("human_decision") is not None:
            errors.append(f"{item.get('id')}: D11-D14 must remain pending until a human disposition")
    pending = [item["id"] for item in decisions if item.get("blocks_p1") and item.get("status") == "pending-human"]
    if status.get("blocking_decision_ids") != pending:
        errors.append("p1-status blocker list must match pending P1 decisions")
    if status.get("status") != "agent-foundation-complete-human-gate-pending":
        errors.append("P1 status must remain human-gate-pending while D11-D14 are unresolved")
    if status.get("human_pass1_frozen") is not True or status.get("agent_blind_pass1_frozen") is not True:
        errors.append("Human and Agent passes must be recorded as frozen")
    if status.get("held_out_or_sealed_data_accessed") is not False:
        errors.append("P1 calibration must record no held-out or sealed data access")
    if status.get("effectiveness_claim_allowed") is not False:
        errors.append("P1 calibration cannot allow effectiveness claims")
    return errors


def validate_inputs() -> tuple[list[str], dict[str, dict], dict[str, dict], dict[str, dict]]:
    errors: list[str] = []
    bundle = load_json(CAL / "episodes-v0.1.json")
    inputs = load_json(CAL / "calibration-inputs-v0.1.json")
    manifest = inputs.get("agent_manifest", {})
    human = inputs.get("human_pass1", [])
    agent = inputs.get("agent_blind_pass1", [])
    episodes = bundle.get("episodes", [])
    if len(episodes) != 12 or len(human) != 12 or len(agent) != 12:
        errors.append(f"expected 12 episodes/human/agent items, got {len(episodes)}/{len(human)}/{len(agent)}")
    if bundle.get("contains_fixture_author_expectations") is not False:
        errors.append("observable calibration bundle must not contain Fixture Author Expectations")
    if manifest.get("episodes_completed") != 12:
        errors.append("Agent manifest must record 12 completed episodes")
    for flag in (
        "human_annotations_seen", "human_timing_seen", "human_pass1_qc_seen",
        "fixture_author_expectations_seen", "calibration_reference_answers_seen",
        "hidden_evaluator_seen", "gold_or_sealed_data_seen",
        "other_annotator_answers_seen", "project_memory_used", "web_used",
        "input_leakage_detected",
    ):
        if manifest.get(flag) is not False:
            errors.append(f"Agent manifest blinding flag must be false: {flag}")
    canonical_agent = "\n".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) for item in agent) + "\n"
    canonical_human = "\n".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) for item in human) + "\n"
    if hashlib.sha256(canonical_agent.encode("utf-8")).hexdigest() != inputs.get("agent_blind_pass1_source_sha256"):
        errors.append("Consolidated Agent records do not reproduce the preserved source SHA-256")
    if hashlib.sha256(canonical_human.encode("utf-8")).hexdigest() != inputs.get("human_pass1_source_sha256"):
        errors.append("Consolidated Human records do not reproduce the preserved source SHA-256")
    if inputs.get("agent_blind_pass1_source_sha256") != manifest.get("output_sha256"):
        errors.append("Agent blind-pass SHA-256 does not match its manifest")
    if bundle.get("source_packet_sha256") != manifest.get("packet_sha256"):
        errors.append("Episode bundle and Agent manifest disagree on packet SHA-256")
    hmap = {item.get("trajectory_id"): item for item in human}
    amap = {item.get("trajectory_id"): item for item in agent}
    emap = {item.get("trajectory_id"): item.get("episode") for item in episodes}
    if None in hmap or None in amap or None in emap:
        errors.append("trajectory_id is missing from an input record")
    if set(hmap) != set(amap) or set(hmap) != set(emap):
        errors.append("Human, Agent, and Episode trajectory sets must match")
    return errors, hmap, amap, emap


def validate_fit(fit: dict, event_ids: set[str], prefix: str) -> list[str]:
    errors: list[str] = []
    status = fit.get("status")
    if status == "EXACT":
        event_id = fit.get("event_id")
        if event_id not in event_ids:
            errors.append(f"{prefix}: EXACT FIT requires a valid event_id")
        if "start_event_id" in fit or "end_event_id" in fit:
            errors.append(f"{prefix}: EXACT FIT cannot contain range locators")
    elif status == "RANGE":
        if fit.get("start_event_id") not in event_ids or fit.get("end_event_id") not in event_ids:
            errors.append(f"{prefix}: RANGE FIT requires valid start/end event IDs")
        if "event_id" in fit:
            errors.append(f"{prefix}: RANGE FIT cannot contain event_id")
    elif status in {"NONE", "UNKNOWN"}:
        if any(key in fit for key in ("event_id", "start_event_id", "end_event_id")):
            errors.append(f"{prefix}: {status} FIT cannot contain locator fields")
    else:
        errors.append(f"{prefix}: invalid FIT status {status!r}")
    confidence = fit.get("confidence")
    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        errors.append(f"{prefix}: FIT confidence must be in [0,1]")
    return errors


def validate_adjudication(hmap: dict[str, dict], amap: dict[str, dict], emap: dict[str, dict]) -> tuple[list[str], dict[str, dict]]:
    errors: list[str] = []
    adjudication_data = load_json(CAL / "calibration-adjudication-v0.1.json")
    annotations = adjudication_data.get("annotations", [])
    if len(annotations) != 12:
        errors.append(f"adjudication must contain 12 records, got {len(annotations)}")
    codes, hard_codes = taxonomy_index()
    dmap: dict[str, dict] = {}
    for item in annotations:
        tid = item.get("trajectory_id")
        prefix = f"adjudication {tid}"
        if tid in dmap:
            errors.append(f"duplicate adjudication trajectory: {tid}")
        dmap[tid] = item
        if tid not in emap:
            errors.append(f"{prefix}: unknown trajectory")
            continue
        if item.get("schema_version") != "0.2-draft":
            errors.append(f"{prefix}: wrong schema version")
        if set(item.get("source_annotation_ids", [])) != {
            hmap[tid].get("annotation_id"), amap[tid].get("annotation_id")
        }:
            errors.append(f"{prefix}: source annotation IDs do not preserve Human and Agent inputs")
        if item.get("outcome_verdict") not in VERDICTS or item.get("process_verdict") not in VERDICTS:
            errors.append(f"{prefix}: invalid verdict")
        if item.get("certification_recommendation") not in RECOMMENDATIONS:
            errors.append(f"{prefix}: invalid recommendation")
        effects = set(item.get("certification_effects", []))
        if not effects or not effects <= EFFECTS:
            errors.append(f"{prefix}: invalid certification effects")
        actions = set(item.get("control_actions", []))
        if not actions or not actions <= CONTROL_ACTIONS:
            errors.append(f"{prefix}: invalid control actions")
        failures = set(item.get("failure_codes", []))
        hard = set(item.get("hard_gate_codes", []))
        if not failures <= codes:
            errors.append(f"{prefix}: unknown failure code(s) {sorted(failures - codes)}")
        if not hard <= failures:
            errors.append(f"{prefix}: hard gates must be a subset of failure codes")
        if not hard <= hard_codes:
            errors.append(f"{prefix}: unapproved hard gate(s) {sorted(hard - hard_codes)}")
        if hard and "HARD_VIOLATION" not in effects:
            errors.append(f"{prefix}: hard gate requires HARD_VIOLATION effect")
        if item.get("process_verdict") == "PASS" and hard:
            errors.append(f"{prefix}: Process PASS cannot coexist with hard gates")
        if item.get("certification_recommendation") == "ACCEPT":
            if item.get("process_verdict") != "PASS" or hard:
                errors.append(f"{prefix}: ACCEPT requires Process PASS and no hard gate")
            if item.get("outcome_verdict") not in {"PASS", "NOT_APPLICABLE"}:
                errors.append(f"{prefix}: ACCEPT requires Outcome PASS or approved N/A semantics")
        if item.get("stop_scope") not in STOP_SCOPES:
            errors.append(f"{prefix}: invalid stop_scope")
        if item.get("valid_alternative_path") not in ALT_PATH:
            errors.append(f"{prefix}: invalid valid_alternative_path")
        episode = emap[tid]
        event_ids = {event.get("event_id") for event in episode.get("events", [])}
        evidence_ids = {ev.get("evidence_id") for ev in episode.get("evidence", [])}
        errors.extend(validate_fit(item.get("first_invalid_transition", {}), event_ids, prefix))
        cited_events = set(item.get("citations", {}).get("event_ids", []))
        cited_evidence = set(item.get("citations", {}).get("evidence_ids", []))
        if not cited_events <= event_ids:
            errors.append(f"{prefix}: invalid event citation(s) {sorted(cited_events - event_ids)}")
        if not cited_evidence <= evidence_ids:
            errors.append(f"{prefix}: invalid evidence citation(s) {sorted(cited_evidence - evidence_ids)}")
        if evidence_ids and not cited_evidence:
            errors.append(f"{prefix}: existing material Evidence object must be cited in v0.2 adjudication")
        pending = item.get("pending_decision_ids", [])
        if item.get("adjudication_status") == "PROVISIONAL_PENDING_HUMAN_DECISION" and not pending:
            errors.append(f"{prefix}: provisional adjudication must name a pending decision")
        if item.get("adjudication_status") != "PROVISIONAL_PENDING_HUMAN_DECISION" and pending:
            errors.append(f"{prefix}: non-provisional adjudication cannot have pending decisions")
        if len(item.get("rationale", "")) < 20:
            errors.append(f"{prefix}: rationale is too short")
    if set(dmap) != set(emap):
        errors.append("adjudication trajectory set must match episode set")
    taught = dmap.get("cal-006", {})
    if taught.get("adjudication_status") != "TAUGHT_CALIBRATION_EXAMPLE_EXCLUDED_FROM_BLIND_METRICS":
        errors.append("cal-006 must remain marked as a taught example excluded from blind metrics")
    return errors, dmap


def validate_records_and_regression(dmap: dict[str, dict]) -> list[str]:
    errors: list[str] = []
    record_data = load_json(CAL / "calibration-adjudication-v0.1.json")
    records = record_data.get("records", [])
    if record_data.get("fixture_author_expectations_used") is not False:
        errors.append("adjudication must record that Fixture Author Expectations were not used")
    if len(records) != 12:
        errors.append("adjudication-records must contain 12 records")
    record_map = {item.get("trajectory_id"): item for item in records}
    if set(record_map) != set(dmap):
        errors.append("adjudication records must cover the same trajectories")
    for tid, item in record_map.items():
        if item.get("adjudicated_annotation_id") != dmap[tid].get("annotation_id"):
            errors.append(f"{tid}: adjudication record points to the wrong derived annotation")
        if bool(item.get("pending_decision_ids")) != bool(item.get("retained_ambiguity")):
            errors.append(f"{tid}: retained_ambiguity must match pending decision presence")
    reg = load_json(REG / "regression-set-v0.2.json")
    entries = reg.get("entries", [])
    if reg.get("fixture_author_expectations_used") is not False:
        errors.append("regression set must not use Fixture Author Expectations")
    if len(entries) != 12:
        errors.append("regression set must contain 12 entries")
    rmap = {item.get("trajectory_id"): item for item in entries}
    if set(rmap) != set(dmap):
        errors.append("regression set must cover the same trajectories")
    for tid, item in rmap.items():
        expected = item.get("expected_core", {})
        ann = dmap[tid]
        for field in ("outcome_verdict", "process_verdict", "certification_recommendation", "valid_alternative_path"):
            if expected.get(field) != ann.get(field):
                errors.append(f"{tid}: regression {field} differs from adjudication")
        fit = ann.get("first_invalid_transition", {})
        if expected.get("first_invalid_transition_status") != fit.get("status"):
            errors.append(f"{tid}: regression FIT status differs from adjudication")
        if expected.get("first_invalid_transition_event_id") != fit.get("event_id"):
            errors.append(f"{tid}: regression FIT event differs from adjudication")
        if item.get("exclude_from_blind_metrics") != (tid == "cal-006"):
            errors.append(f"{tid}: taught-case exclusion flag is incorrect")
        ext = item.get("trace_extension", {})
        if ext.get("trajectory_id") != tid or ext.get("stop_id") != "STOP1":
            errors.append(f"{tid}: trace extension identity mismatch")
        if ext.get("stop_scope") not in STOP_SCOPES:
            errors.append(f"{tid}: invalid trace-extension stop_scope")
    return errors


def main() -> int:
    errors = validate_required()
    try:
        errors.extend(validate_decision_state())
        input_errors, hmap, amap, emap = validate_inputs()
        errors.extend(input_errors)
        adj_errors, dmap = validate_adjudication(hmap, amap, emap)
        errors.extend(adj_errors)
        errors.extend(validate_records_and_regression(dmap))
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        errors.append(str(exc))
    if errors:
        print("P1 calibration validation failed:", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1
    print("P1 calibration validation passed: original passes are preserved, core adjudication is consistent, and D11-D14 remain human-gated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
