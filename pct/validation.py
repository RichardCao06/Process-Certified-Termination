"""Dependency-free validation and deterministic linting for PCT P1 artifacts.

The structural validator deliberately accepts trajectories that contain process
failures: those failures are the object of study. ``lint_trajectory`` produces
candidate findings without pretending that a deterministic lint is a Gold
annotation.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

PROHIBITED_TRACE_KEYS = {
    "gold_label",
    "gold_failure_code",
    "hidden_failure_location",
    "hidden_evaluator_output",
    "reference_truth",
    "sealed_result",
}

EVENT_TYPES = {
    "GOAL_DEFINED",
    "GOAL_CHANGE",
    "TURN_START",
    "TURN_END",
    "STEP_START",
    "STEP_END",
    "MODEL_MESSAGE",
    "INBOX_EVENT",
    "OBSERVATION",
    "DECISION_CHECKPOINT",
    "TOOL_CALL",
    "TOOL_RESULT",
    "STATE_DELTA",
    "EVIDENCE_RECORDED",
    "OBLIGATION_TRANSITION",
    "CANDIDATE_STOP",
    "VERIFIER_RESULT",
    "AUDITOR_RESULT",
    "REPAIR_FEEDBACK",
    "HUMAN_INPUT",
    "BUDGET_EVENT",
    "ERROR",
}
EVENT_SOURCES = {"HUMAN", "WORKER", "HARNESS", "TOOL", "VERIFIER", "AUDITOR", "SYSTEM"}
EVIDENCE_VERDICTS = {"PASS", "FAIL", "UNKNOWN"}
FOUR_WAY = {"PASS", "FAIL", "UNKNOWN", "NOT_APPLICABLE"}
CERT_RECOMMENDATIONS = {
    "ACCEPT",
    "CONTINUE",
    "EVIDENCE_REQUIRED",
    "HUMAN_REQUIRED",
    "BLOCKED",
    "NO_PROGRESS",
    "UNDETERMINED",
}
CERT_EFFECTS = {
    "HARD_VIOLATION",
    "EVIDENCE_GAP",
    "OUTCOME_FAILURE",
    "SOFT_QUALITY_ISSUE",
    "LIMITATION",
    "NONE",
    "UNKNOWN",
}
LOCALIZATION_STATUS = {"EXACT", "RANGE", "NONE", "UNKNOWN"}
OBLIGATION_STATES = {"PENDING", "ATTEMPTED", "PROVISIONAL", "VERIFIED", "VIOLATED", "UNKNOWN"}


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    location: str = "$"
    severity: str = "ERROR"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class TaxonomyIndex:
    codes: frozenset[str]
    hard_gate_codes: frozenset[str]
    families: Mapping[str, tuple[str, ...]]

    @classmethod
    def from_data(cls, data: Mapping[str, Any]) -> "TaxonomyIndex":
        family_map: dict[str, tuple[str, ...]] = {}
        codes: set[str] = set()
        hard: set[str] = set()
        for family in data.get("families", []):
            family_id = family.get("id")
            family_codes: list[str] = []
            for item in family.get("codes", []):
                code = item.get("code")
                if isinstance(code, str):
                    codes.add(code)
                    family_codes.append(code)
                    if item.get("candidate_hard_gate") is True:
                        hard.add(code)
            if isinstance(family_id, str):
                family_map[family_id] = tuple(family_codes)
        return cls(frozenset(codes), frozenset(hard), family_map)


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _issue(issues: list[ValidationIssue], code: str, message: str, location: str, severity: str = "ERROR") -> None:
    issues.append(ValidationIssue(code, message, location, severity))


def _require_mapping(value: Any, issues: list[ValidationIssue], location: str) -> Mapping[str, Any] | None:
    if not isinstance(value, Mapping):
        _issue(issues, "TYPE_OBJECT", "expected an object", location)
        return None
    return value


def _require_list(value: Any, issues: list[ValidationIssue], location: str) -> list[Any] | None:
    if not isinstance(value, list):
        _issue(issues, "TYPE_ARRAY", "expected an array", location)
        return None
    return value


def _required(obj: Mapping[str, Any], fields: Iterable[str], issues: list[ValidationIssue], location: str) -> None:
    for field in fields:
        if field not in obj:
            _issue(issues, "MISSING_FIELD", f"missing required field {field!r}", f"{location}.{field}")


def _duplicates(values: Sequence[Any]) -> set[Any]:
    seen: set[Any] = set()
    duplicates: set[Any] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def _scan_prohibited(value: Any, issues: list[ValidationIssue], location: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            child = f"{location}.{key}"
            if key in PROHIBITED_TRACE_KEYS:
                _issue(issues, "SEALED_LEAKAGE_FIELD", f"prohibited field {key!r} appears in observable trajectory", child)
            _scan_prohibited(item, issues, child)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _scan_prohibited(item, issues, f"{location}[{index}]")


def validate_taxonomy(data: Mapping[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    _required(data, ("taxonomy_id", "version", "phase", "status", "annotation_model", "families"), issues, "$")
    if data.get("taxonomy_id") != "pct-process-failure-taxonomy":
        _issue(issues, "TAXONOMY_ID", "unexpected taxonomy_id", "$.taxonomy_id")
    families = _require_list(data.get("families"), issues, "$.families")
    if families is None:
        return issues
    family_ids: list[Any] = []
    codes: list[Any] = []
    for f_index, family_value in enumerate(families):
        location = f"$.families[{f_index}]"
        family = _require_mapping(family_value, issues, location)
        if family is None:
            continue
        _required(family, ("id", "name", "codes"), issues, location)
        family_id = family.get("id")
        family_ids.append(family_id)
        items = _require_list(family.get("codes"), issues, f"{location}.codes")
        if items is None:
            continue
        for c_index, item_value in enumerate(items):
            item_loc = f"{location}.codes[{c_index}]"
            item = _require_mapping(item_value, issues, item_loc)
            if item is None:
                continue
            _required(item, ("code", "name", "definition", "include_when", "exclude_when", "candidate_hard_gate"), issues, item_loc)
            code = item.get("code")
            codes.append(code)
            if isinstance(code, str) and isinstance(family_id, str) and not code.startswith(family_id + "."):
                _issue(issues, "TAXONOMY_FAMILY_PREFIX", f"code {code!r} does not match family {family_id!r}", f"{item_loc}.code")
            if not isinstance(item.get("include_when"), list) or not item.get("include_when"):
                _issue(issues, "TAXONOMY_INCLUDE_RULE", "include_when must be a non-empty array", f"{item_loc}.include_when")
            if not isinstance(item.get("exclude_when"), list) or not item.get("exclude_when"):
                _issue(issues, "TAXONOMY_EXCLUDE_RULE", "exclude_when must be a non-empty array", f"{item_loc}.exclude_when")
            if item.get("candidate_hard_gate") is True and not item.get("p0_hard_gate"):
                _issue(issues, "HARD_GATE_PROVENANCE", "candidate hard gate requires P0 provenance", item_loc)
    for duplicate in _duplicates(family_ids):
        _issue(issues, "DUPLICATE_FAMILY", f"duplicate family id {duplicate!r}", "$.families")
    for duplicate in _duplicates(codes):
        _issue(issues, "DUPLICATE_CODE", f"duplicate taxonomy code {duplicate!r}", "$.families")
    return issues


def validate_trajectory(data: Mapping[str, Any]) -> list[ValidationIssue]:
    """Validate record structure and reference integrity, not process correctness."""
    issues: list[ValidationIssue] = []
    _required(data, ("schema_version", "trajectory_id", "task", "run", "goal", "snapshots", "evidence", "events", "candidate_stops"), issues, "$")
    if data.get("schema_version") != "0.1-draft":
        _issue(issues, "SCHEMA_VERSION", "trajectory schema_version must be 0.1-draft", "$.schema_version")
    _scan_prohibited(data, issues)

    task = _require_mapping(data.get("task"), issues, "$.task")
    if task is not None:
        _required(task, ("task_id", "stream", "description", "source_class"), issues, "$.task")
        if task.get("stream") not in {"V", "S"}:
            _issue(issues, "TASK_STREAM", "stream must be V or S", "$.task.stream")

    run = _require_mapping(data.get("run"), issues, "$.run")
    if run is not None:
        _required(run, ("worker_model", "harness", "harness_commit", "resource_policy", "visibility_policy"), issues, "$.run")
        commit = run.get("harness_commit")
        if not isinstance(commit, str) or len(commit) != 40 or any(ch not in "0123456789abcdef" for ch in commit):
            _issue(issues, "HARNESS_COMMIT", "harness_commit must be a lowercase 40-character SHA", "$.run.harness_commit")
        visibility = run.get("visibility_policy")
        if isinstance(visibility, Mapping):
            for field in ("hidden_evaluator_visible", "gold_labels_visible", "other_condition_outputs_visible"):
                if not isinstance(visibility.get(field), bool):
                    _issue(issues, "VISIBILITY_POLICY", f"{field} must be boolean", f"$.run.visibility_policy.{field}")

    goal = _require_mapping(data.get("goal"), issues, "$.goal")
    obligation_ids: set[str] = set()
    goal_revision: int | None = None
    if goal is not None:
        _required(goal, ("goal_id", "revision", "objective", "obligations"), issues, "$.goal")
        if isinstance(goal.get("revision"), int):
            goal_revision = goal["revision"]
        obligations = _require_list(goal.get("obligations"), issues, "$.goal.obligations")
        if obligations is not None:
            raw_ids: list[Any] = []
            dependencies: list[tuple[str, Any, str]] = []
            for index, obligation_value in enumerate(obligations):
                loc = f"$.goal.obligations[{index}]"
                obligation = _require_mapping(obligation_value, issues, loc)
                if obligation is None:
                    continue
                _required(obligation, ("obligation_id", "description", "kind", "severity", "required_evidence_classes"), issues, loc)
                oid = obligation.get("obligation_id")
                raw_ids.append(oid)
                if isinstance(oid, str):
                    obligation_ids.add(oid)
                    for dependency in obligation.get("depends_on", []) if isinstance(obligation.get("depends_on", []), list) else []:
                        dependencies.append((oid, dependency, loc))
            for duplicate in _duplicates(raw_ids):
                _issue(issues, "DUPLICATE_OBLIGATION", f"duplicate obligation id {duplicate!r}", "$.goal.obligations")
            for oid, dependency, loc in dependencies:
                if dependency not in obligation_ids:
                    _issue(issues, "UNKNOWN_OBLIGATION_DEPENDENCY", f"{oid!r} depends on unknown obligation {dependency!r}", f"{loc}.depends_on")

    snapshots = _require_list(data.get("snapshots"), issues, "$.snapshots") or []
    snapshot_ids: set[str] = set()
    snapshot_sequences: dict[str, int] = {}
    raw_snapshot_ids: list[Any] = []
    for index, snapshot_value in enumerate(snapshots):
        loc = f"$.snapshots[{index}]"
        snapshot = _require_mapping(snapshot_value, issues, loc)
        if snapshot is None:
            continue
        _required(snapshot, ("snapshot_id", "sequence", "digest"), issues, loc)
        sid = snapshot.get("snapshot_id")
        raw_snapshot_ids.append(sid)
        if isinstance(sid, str):
            snapshot_ids.add(sid)
            if isinstance(snapshot.get("sequence"), int):
                snapshot_sequences[sid] = snapshot["sequence"]
        digest = snapshot.get("digest")
        if not isinstance(digest, str) or len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            _issue(issues, "SNAPSHOT_DIGEST", "snapshot digest must be a lowercase SHA-256", f"{loc}.digest")
    for duplicate in _duplicates(raw_snapshot_ids):
        _issue(issues, "DUPLICATE_SNAPSHOT", f"duplicate snapshot id {duplicate!r}", "$.snapshots")

    events = _require_list(data.get("events"), issues, "$.events") or []
    event_ids: set[str] = set()
    event_sequences: dict[str, int] = {}
    event_types: dict[str, str] = {}
    raw_event_ids: list[Any] = []
    sequences: list[int] = []
    for index, event_value in enumerate(events):
        loc = f"$.events[{index}]"
        event = _require_mapping(event_value, issues, loc)
        if event is None:
            continue
        _required(event, ("event_id", "sequence", "event_type", "source", "goal_revision", "payload"), issues, loc)
        event_id = event.get("event_id")
        raw_event_ids.append(event_id)
        sequence = event.get("sequence")
        if isinstance(event_id, str):
            event_ids.add(event_id)
            if isinstance(sequence, int):
                event_sequences[event_id] = sequence
            if isinstance(event.get("event_type"), str):
                event_types[event_id] = event["event_type"]
        if isinstance(sequence, int):
            sequences.append(sequence)
        else:
            _issue(issues, "EVENT_SEQUENCE", "event sequence must be an integer", f"{loc}.sequence")
        if event.get("event_type") not in EVENT_TYPES:
            _issue(issues, "EVENT_TYPE", f"unknown event type {event.get('event_type')!r}", f"{loc}.event_type")
        if event.get("source") not in EVENT_SOURCES:
            _issue(issues, "EVENT_SOURCE", f"unknown event source {event.get('source')!r}", f"{loc}.source")
        if goal_revision is not None and event.get("goal_revision") != goal_revision:
            _issue(issues, "GOAL_REVISION_MISMATCH", "P1 fixture events must use the current goal revision", f"{loc}.goal_revision")
        sid = event.get("snapshot_id")
        if sid is not None and sid not in snapshot_ids:
            _issue(issues, "UNKNOWN_EVENT_SNAPSHOT", f"event references unknown snapshot {sid!r}", f"{loc}.snapshot_id")
        if not isinstance(event.get("payload"), Mapping):
            _issue(issues, "EVENT_PAYLOAD", "event payload must be an object", f"{loc}.payload")
    for duplicate in _duplicates(raw_event_ids):
        _issue(issues, "DUPLICATE_EVENT", f"duplicate event id {duplicate!r}", "$.events")
    if sequences != sorted(sequences) or len(sequences) != len(set(sequences)):
        _issue(issues, "EVENT_ORDER", "event sequences must be strictly increasing and unique", "$.events")

    evidence_items = _require_list(data.get("evidence"), issues, "$.evidence") or []
    evidence_ids: set[str] = set()
    evidence_by_id: dict[str, Mapping[str, Any]] = {}
    raw_evidence_ids: list[Any] = []
    for index, evidence_value in enumerate(evidence_items):
        loc = f"$.evidence[{index}]"
        evidence = _require_mapping(evidence_value, issues, loc)
        if evidence is None:
            continue
        _required(evidence, ("evidence_id", "created_event_id", "source_class", "goal_revision", "snapshot_id", "obligation_ids", "verdict", "scope", "invalidated_by_event_ids"), issues, loc)
        eid = evidence.get("evidence_id")
        raw_evidence_ids.append(eid)
        if isinstance(eid, str):
            evidence_ids.add(eid)
            evidence_by_id[eid] = evidence
        created = evidence.get("created_event_id")
        if created not in event_ids:
            _issue(issues, "UNKNOWN_EVIDENCE_EVENT", f"evidence creation references unknown event {created!r}", f"{loc}.created_event_id")
        sid = evidence.get("snapshot_id")
        if sid not in snapshot_ids:
            _issue(issues, "UNKNOWN_EVIDENCE_SNAPSHOT", f"evidence references unknown snapshot {sid!r}", f"{loc}.snapshot_id")
        if evidence.get("verdict") not in EVIDENCE_VERDICTS:
            _issue(issues, "EVIDENCE_VERDICT", f"unknown evidence verdict {evidence.get('verdict')!r}", f"{loc}.verdict")
        for oid in evidence.get("obligation_ids", []) if isinstance(evidence.get("obligation_ids"), list) else []:
            if oid not in obligation_ids:
                _issue(issues, "UNKNOWN_EVIDENCE_OBLIGATION", f"evidence references unknown obligation {oid!r}", f"{loc}.obligation_ids")
        for invalidator in evidence.get("invalidated_by_event_ids", []) if isinstance(evidence.get("invalidated_by_event_ids"), list) else []:
            if invalidator not in event_ids:
                _issue(issues, "UNKNOWN_INVALIDATOR", f"evidence invalidator {invalidator!r} is not an event", f"{loc}.invalidated_by_event_ids")
            elif created in event_sequences and event_sequences[invalidator] <= event_sequences[created]:
                _issue(issues, "INVALIDATOR_ORDER", "evidence invalidator must occur after evidence creation", f"{loc}.invalidated_by_event_ids")
    for duplicate in _duplicates(raw_evidence_ids):
        _issue(issues, "DUPLICATE_EVIDENCE", f"duplicate evidence id {duplicate!r}", "$.evidence")

    # Validate references inside obligation transition payloads without declaring them correct.
    for index, event_value in enumerate(events):
        if not isinstance(event_value, Mapping) or event_value.get("event_type") != "OBLIGATION_TRANSITION":
            continue
        loc = f"$.events[{index}].payload"
        payload = event_value.get("payload")
        if not isinstance(payload, Mapping):
            continue
        _required(payload, ("obligation_id", "from_state", "to_state", "evidence_ids", "reason"), issues, loc)
        if payload.get("obligation_id") not in obligation_ids:
            _issue(issues, "UNKNOWN_TRANSITION_OBLIGATION", f"unknown obligation {payload.get('obligation_id')!r}", f"{loc}.obligation_id")
        for field in ("from_state", "to_state"):
            if payload.get(field) not in OBLIGATION_STATES:
                _issue(issues, "OBLIGATION_STATE", f"unknown state {payload.get(field)!r}", f"{loc}.{field}")
        refs = payload.get("evidence_ids")
        if not isinstance(refs, list):
            _issue(issues, "TRANSITION_EVIDENCE_ARRAY", "evidence_ids must be an array", f"{loc}.evidence_ids")
        else:
            for eid in refs:
                if eid not in evidence_ids:
                    _issue(issues, "UNKNOWN_TRANSITION_EVIDENCE", f"transition references unknown evidence {eid!r}", f"{loc}.evidence_ids")

    stops = _require_list(data.get("candidate_stops"), issues, "$.candidate_stops") or []
    raw_stop_ids: list[Any] = []
    for index, stop_value in enumerate(stops):
        loc = f"$.candidate_stops[{index}]"
        stop = _require_mapping(stop_value, issues, loc)
        if stop is None:
            continue
        _required(stop, ("stop_id", "event_id", "goal_revision", "snapshot_id", "worker_claim", "harness_stop_reason"), issues, loc)
        raw_stop_ids.append(stop.get("stop_id"))
        event_id = stop.get("event_id")
        if event_id not in event_ids:
            _issue(issues, "UNKNOWN_STOP_EVENT", f"candidate stop references unknown event {event_id!r}", f"{loc}.event_id")
        elif event_types.get(event_id) != "CANDIDATE_STOP":
            _issue(issues, "STOP_EVENT_TYPE", "candidate stop event must have CANDIDATE_STOP type", f"{loc}.event_id")
        if stop.get("snapshot_id") not in snapshot_ids:
            _issue(issues, "UNKNOWN_STOP_SNAPSHOT", f"candidate stop references unknown snapshot {stop.get('snapshot_id')!r}", f"{loc}.snapshot_id")
        if goal_revision is not None and stop.get("goal_revision") != goal_revision:
            _issue(issues, "STOP_GOAL_REVISION", "candidate stop goal revision differs from current goal", f"{loc}.goal_revision")
    for duplicate in _duplicates(raw_stop_ids):
        _issue(issues, "DUPLICATE_STOP", f"duplicate candidate stop id {duplicate!r}", "$.candidate_stops")
    return issues


def lint_trajectory(data: Mapping[str, Any]) -> list[ValidationIssue]:
    """Produce deterministic candidate process findings for human/Auditor review."""
    if validate_trajectory(data):
        # Linting malformed data produces misleading research labels.
        return [ValidationIssue("STRUCTURE_INVALID", "trajectory must pass structural validation before linting")]
    events = data["events"]
    event_seq = {event["event_id"]: event["sequence"] for event in events}
    evidence = {item["evidence_id"]: item for item in data["evidence"]}
    obligation_severity = {item["obligation_id"]: item["severity"] for item in data["goal"]["obligations"]}
    latest_state = {oid: "PENDING" for oid in obligation_severity}
    latest_evidence_refs: dict[str, list[str]] = {oid: [] for oid in obligation_severity}
    findings: list[ValidationIssue] = []
    failed_tool_obligations: dict[str, str] = {}

    for event in events:
        payload = event["payload"]
        if event["event_type"] == "TOOL_RESULT" and payload.get("status") == "FAIL" and payload.get("authoritative") is True:
            for oid in payload.get("obligation_ids", []):
                failed_tool_obligations[oid] = event["event_id"]
        if event["event_type"] != "OBLIGATION_TRANSITION":
            continue
        oid = payload["obligation_id"]
        from_state = payload["from_state"]
        to_state = payload["to_state"]
        refs = payload["evidence_ids"]
        if latest_state.get(oid) != from_state:
            findings.append(ValidationIssue(
                "TRN.STATE_HISTORY_MISMATCH",
                f"transition claims {oid} is {from_state}, but prior recorded state is {latest_state.get(oid)}",
                event["event_id"],
                "WARNING",
            ))
        if to_state == "VERIFIED":
            if not refs:
                findings.extend([
                    ValidationIssue("TRN.PREMATURE_STATE_PROMOTION", f"{oid} promoted to VERIFIED without evidence", event["event_id"]),
                    ValidationIssue("EVD.MISSING_REQUIRED_EVIDENCE", f"{oid} has no evidence for VERIFIED state", event["event_id"]),
                ])
            for eid in refs:
                item = evidence[eid]
                if item["verdict"] != "PASS":
                    findings.append(ValidationIssue("TRN.FAILURE_NOT_PROPAGATED", f"{oid} promoted using {eid} with verdict {item['verdict']}", event["event_id"]))
                invalidators_before = [invalidator for invalidator in item["invalidated_by_event_ids"] if event_seq[invalidator] <= event["sequence"]]
                if invalidators_before:
                    findings.append(ValidationIssue("EVD.STALE_EVIDENCE", f"{oid} uses stale evidence {eid}, invalidated by {invalidators_before}", event["event_id"]))
                if oid not in item["obligation_ids"]:
                    findings.append(ValidationIssue("EVD.SCOPE_MISMATCH", f"evidence {eid} does not claim obligation {oid}", event["event_id"]))
            if oid in failed_tool_obligations:
                successful_after_failure = False
                failure_seq = event_seq[failed_tool_obligations[oid]]
                for eid in refs:
                    created_seq = event_seq[evidence[eid]["created_event_id"]]
                    if evidence[eid]["verdict"] == "PASS" and created_seq > failure_seq:
                        successful_after_failure = True
                if not successful_after_failure:
                    findings.append(ValidationIssue("ACT.TOOL_FAILURE_IGNORED", f"{oid} is VERIFIED after authoritative failure {failed_tool_obligations[oid]} without superseding pass evidence", event["event_id"]))
        latest_state[oid] = to_state
        latest_evidence_refs[oid] = list(refs)

    for stop in data["candidate_stops"]:
        if stop["worker_claim"] == "COMPLETE":
            unresolved = [oid for oid, state in latest_state.items() if obligation_severity[oid] == "HARD" and state != "VERIFIED"]
            if unresolved:
                findings.append(ValidationIssue("EXIT.PREMATURE_TERMINATION", f"complete stop leaves hard obligations unresolved: {unresolved}", stop["event_id"]))
            stop_sequence = event_seq[stop["event_id"]]
            for oid, refs in latest_evidence_refs.items():
                if latest_state.get(oid) != "VERIFIED":
                    continue
                for eid in refs:
                    item = evidence[eid]
                    invalidators_before_stop = [invalidator for invalidator in item["invalidated_by_event_ids"] if event_seq[invalidator] <= stop_sequence]
                    if invalidators_before_stop:
                        findings.append(ValidationIssue("EVD.STALE_EVIDENCE", f"complete stop relies on stale evidence {eid} for {oid}, invalidated by {invalidators_before_stop}", stop["event_id"]))
    # Preserve deterministic order and avoid duplicate same-code same-location findings.
    unique: dict[tuple[str, str], ValidationIssue] = {}
    for finding in findings:
        unique[(finding.code, finding.location)] = finding
    return sorted(unique.values(), key=lambda item: (event_seq.get(item.location, 10**12), item.code, item.message))


def validate_annotation(data: Mapping[str, Any], trajectory: Mapping[str, Any], taxonomy: TaxonomyIndex) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    required = (
        "schema_version", "annotation_id", "trajectory_id", "stop_id", "annotator",
        "outcome_verdict", "process_verdict", "certification_recommendation",
        "certification_effects", "failure_codes", "hard_gate_codes",
        "first_invalid_transition", "evidence_assessment", "valid_alternative_path", "citations",
    )
    _required(data, required, issues, "$")
    if data.get("schema_version") != "0.1-draft":
        _issue(issues, "ANNOTATION_SCHEMA_VERSION", "annotation schema_version must be 0.1-draft", "$.schema_version")
    if data.get("trajectory_id") != trajectory.get("trajectory_id"):
        _issue(issues, "ANNOTATION_TRAJECTORY", "annotation trajectory_id does not match trajectory", "$.trajectory_id")
    stop_ids = {item["stop_id"] for item in trajectory.get("candidate_stops", [])}
    if data.get("stop_id") not in stop_ids:
        _issue(issues, "ANNOTATION_STOP", "annotation stop_id is not present in trajectory", "$.stop_id")
    for field in ("outcome_verdict", "process_verdict"):
        if data.get(field) not in FOUR_WAY:
            _issue(issues, "ANNOTATION_VERDICT", f"invalid {field}", f"$.{field}")
    recommendation = data.get("certification_recommendation")
    if recommendation not in CERT_RECOMMENDATIONS:
        _issue(issues, "CERTIFICATION_RECOMMENDATION", "invalid certification recommendation", "$.certification_recommendation")
    effects = data.get("certification_effects")
    if not isinstance(effects, list) or not effects:
        _issue(issues, "CERTIFICATION_EFFECTS", "certification_effects must be a non-empty array", "$.certification_effects")
        effects = []
    else:
        for effect in effects:
            if effect not in CERT_EFFECTS:
                _issue(issues, "CERTIFICATION_EFFECT", f"unknown effect {effect!r}", "$.certification_effects")
    failure_codes = data.get("failure_codes")
    if not isinstance(failure_codes, list):
        _issue(issues, "FAILURE_CODES", "failure_codes must be an array", "$.failure_codes")
        failure_codes = []
    for code in failure_codes:
        if code not in taxonomy.codes:
            _issue(issues, "UNKNOWN_FAILURE_CODE", f"unknown taxonomy code {code!r}", "$.failure_codes")
    hard_codes = data.get("hard_gate_codes")
    if not isinstance(hard_codes, list):
        _issue(issues, "HARD_GATE_CODES", "hard_gate_codes must be an array", "$.hard_gate_codes")
        hard_codes = []
    for code in hard_codes:
        if code not in taxonomy.hard_gate_codes:
            _issue(issues, "UNAPPROVED_HARD_GATE", f"{code!r} is not mapped to a P0-approved hard-gate class", "$.hard_gate_codes")
        if code not in failure_codes:
            _issue(issues, "HARD_GATE_NOT_FAILURE", f"hard gate {code!r} must also appear in failure_codes", "$.hard_gate_codes")

    event_ids = {event["event_id"] for event in trajectory.get("events", [])}
    event_seq = {event["event_id"]: event["sequence"] for event in trajectory.get("events", [])}
    evidence_ids = {item["evidence_id"] for item in trajectory.get("evidence", [])}
    localization = data.get("first_invalid_transition")
    if not isinstance(localization, Mapping):
        _issue(issues, "LOCALIZATION_OBJECT", "first_invalid_transition must be an object", "$.first_invalid_transition")
    else:
        status = localization.get("status")
        if status not in LOCALIZATION_STATUS:
            _issue(issues, "LOCALIZATION_STATUS", "invalid localization status", "$.first_invalid_transition.status")
        if status == "EXACT":
            event_id = localization.get("event_id")
            if event_id not in event_ids:
                _issue(issues, "LOCALIZATION_EVENT", "EXACT localization requires a valid event_id", "$.first_invalid_transition.event_id")
        if status == "RANGE":
            start, end = localization.get("start_event_id"), localization.get("end_event_id")
            if start not in event_ids or end not in event_ids:
                _issue(issues, "LOCALIZATION_RANGE", "RANGE localization requires valid start and end events", "$.first_invalid_transition")
            elif event_seq[start] > event_seq[end]:
                _issue(issues, "LOCALIZATION_RANGE_ORDER", "localization range start must not follow end", "$.first_invalid_transition")
        confidence = localization.get("confidence")
        if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            _issue(issues, "LOCALIZATION_CONFIDENCE", "confidence must be between 0 and 1", "$.first_invalid_transition.confidence")

    citations = data.get("citations")
    if isinstance(citations, Mapping):
        for event_id in citations.get("event_ids", []) if isinstance(citations.get("event_ids", []), list) else []:
            if event_id not in event_ids:
                _issue(issues, "UNKNOWN_CITED_EVENT", f"unknown cited event {event_id!r}", "$.citations.event_ids")
        for evidence_id in citations.get("evidence_ids", []) if isinstance(citations.get("evidence_ids", []), list) else []:
            if evidence_id not in evidence_ids:
                _issue(issues, "UNKNOWN_CITED_EVIDENCE", f"unknown cited evidence {evidence_id!r}", "$.citations.evidence_ids")
    else:
        _issue(issues, "CITATIONS_OBJECT", "citations must be an object", "$.citations")

    if data.get("process_verdict") == "FAIL" and not failure_codes:
        _issue(issues, "FAILED_WITHOUT_CODE", "process FAIL requires at least one failure code", "$.failure_codes")
    if data.get("process_verdict") == "PASS" and isinstance(localization, Mapping) and localization.get("status") != "NONE":
        _issue(issues, "PASS_WITH_INVALID_TRANSITION", "process PASS requires localization status NONE", "$.first_invalid_transition.status")
    if hard_codes and "HARD_VIOLATION" not in effects:
        _issue(issues, "HARD_GATE_EFFECT", "hard-gate annotation requires HARD_VIOLATION effect", "$.certification_effects")
    if recommendation == "ACCEPT":
        if data.get("outcome_verdict") != "PASS" or data.get("process_verdict") != "PASS":
            _issue(issues, "UNSAFE_ACCEPT", "ACCEPT requires outcome PASS and process PASS", "$.certification_recommendation")
        if hard_codes:
            _issue(issues, "HARD_GATE_ACCEPT", "ACCEPT cannot include hard-gate violations", "$.certification_recommendation")
        if any(effect in effects for effect in ("HARD_VIOLATION", "EVIDENCE_GAP", "OUTCOME_FAILURE", "UNKNOWN")):
            _issue(issues, "CONTRADICTORY_ACCEPT_EFFECT", "ACCEPT conflicts with blocking certification effects", "$.certification_effects")
    return issues
