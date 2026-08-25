#!/usr/bin/env python3
"""Validate P1 closure-readiness artifacts without approving P1 closure."""
from __future__ import annotations

import base64
import csv
import hashlib
import json
import tarfile
import tempfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PASS_B = ROOT / "data" / "p1" / "development-pilot" / "pass-b"

PASS_A_SHA = "d561b442053293c94c13db6ff5c49af6ef187fa12cff351f0e94dbb1e92364b8"
PASS_B_SHA = "ff5bb76b5b168dd546f61f2dd065f2091ed841e6a2335c014e2a3f1441a5ed5f"
PASS_B_TIMING_SHA = "6b614fbda006995cbd90b80e1a928207084b29dbb6ab86032b38e194fa88c023"
EPISODES_SHA = "d5f5bc3dc0172d1e3f860037d178306d87f1514048835272fb326d69e3769e90"
ADJUDICATION_SHA = "03b8a87b61cce8ef5e0a1d5b07b0df909562a142c83d30898fab594d1856e3ce"
AUTHOR_PLAINTEXT_SHA = "fea1de6361b5821bd817f2787a1a27b85b6066671bfbc36d628c2555ace27a44"
BUNDLE_SHA = "9e4c39107a746e54360214d71ef0d03d025b9c5324e06411dbdc71fecb306691"
CONFLICT_IDS = {"dev-023", "dev-012", "dev-017"}

DIRECT_REQUIRED = [
    PASS_B / "closure-readiness-bundle-manifest-v0.1.json",
    PASS_B / "bundle-parts" / "closure-readiness-part-00",
    ROOT / "governance" / "p1-closure-readiness-status-v0.1.json",
    ROOT / "governance" / "p1-outcome-semantics-gate-v0.1.json",
    ROOT / "docs" / "p1" / "human-decision-pack-d15.md",
    ROOT / "docs" / "p1" / "p1-taxonomy-migration-provisional-v0.1.md",
    ROOT / "docs" / "p1" / "p1-closure-report-v0.1-draft.md",
    ROOT / "docs" / "p1" / "incident-record-PCT-P1-I01.md",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected object")
    return value


def read_jsonl(path: Path) -> list[dict]:
    result: list[dict] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_no}: expected object")
        result.append(value)
    return result


def extract_bundle() -> tuple[tempfile.TemporaryDirectory[str], Path]:
    manifest = load_json(PASS_B / "closure-readiness-bundle-manifest-v0.1.json")
    if manifest.get("sha256") != BUNDLE_SHA:
        raise ValueError("closure-readiness manifest points to the wrong bundle hash")
    encoded = "".join(
        "".join((PASS_B / part).read_text(encoding="utf-8").split())
        for part in manifest["parts"]
    )
    archive = base64.b64decode(encoded, validate=True)
    if hashlib.sha256(archive).hexdigest() != manifest["sha256"]:
        raise ValueError("closure-readiness bundle SHA-256 mismatch")
    temp = tempfile.TemporaryDirectory(prefix="pct-p1-closure-")
    root = Path(temp.name).resolve()
    archive_path = root / manifest["decoded_filename"]
    archive_path.write_bytes(archive)
    with tarfile.open(archive_path, "r:gz") as tf:
        for member in tf.getmembers():
            target = (root / member.name).resolve()
            if target != root and root not in target.parents:
                raise ValueError(f"unsafe archive path: {member.name}")
        tf.extractall(root, filter="data")
    for item in manifest.get("files", []):
        path = root / item["path"]
        if not path.is_file():
            raise ValueError(f"bundle missing {item['path']}")
        if sha256(path) != item["sha256"]:
            raise ValueError(f"bundle file hash mismatch: {item['path']}")
    if manifest.get("contains_custody_key_material") is not False:
        raise ValueError("closure bundle must not contain custody key material")
    if manifest.get("contains_full_30_case_author_plaintext") is not False:
        raise ValueError("closure bundle must not publish full author plaintext")
    return temp, root


def validate() -> list[str]:
    errors: list[str] = []
    for path in DIRECT_REQUIRED:
        if not path.is_file():
            errors.append(f"missing closure-readiness artifact: {path.relative_to(ROOT)}")
    if errors:
        return errors

    try:
        temp, data_root = extract_bundle()
    except Exception as exc:
        return [str(exc)]
    try:
        pass_b_dir = data_root / "data" / "p1" / "development-pilot" / "pass-b"
        reports = data_root / "reports" / "p1" / "pass-b"

        pass_b_raw = pass_b_dir / "human-pass-b-raw.jsonl"
        timing_raw = pass_b_dir / "timing-raw.csv"
        episodes = pass_b_dir / "episodes-v0.1.json"
        adjudication_raw = pass_b_dir / "human-developmental-adjudication-raw-v0.1.json"

        if sha256(pass_b_raw) != PASS_B_SHA:
            errors.append("Pass-B raw annotation SHA-256 mismatch")
        if sha256(timing_raw) != PASS_B_TIMING_SHA:
            errors.append("Pass-B timing SHA-256 mismatch")
        if sha256(episodes) != EPISODES_SHA:
            errors.append("Pass-B episodes SHA-256 mismatch")
        if sha256(adjudication_raw) != ADJUDICATION_SHA:
            errors.append("raw adjudication SHA-256 mismatch")

        pass_b = read_jsonl(pass_b_raw)
        if len(pass_b) != 12:
            errors.append("Pass B must contain 12 raw annotations")
        with timing_raw.open(newline="", encoding="utf-8-sig") as handle:
            timing = list(csv.DictReader(handle))
        if len(timing) != 12 or any(int(row["seconds"]) <= 0 for row in timing):
            errors.append("Pass-B timing must contain 12 positive rows")

        adjudication = load_json(adjudication_raw)
        if adjudication.get("status") != "COMPLETE":
            errors.append("human adjudication must be COMPLETE")
        if adjudication.get("required_case_count") != 8:
            errors.append("human adjudication must cover eight required cases")
        if adjudication.get("required_field_count") != 20:
            errors.append("human adjudication must require 20 fields")
        if adjudication.get("completed_required_field_count") != 20:
            errors.append("human adjudication must complete all 20 fields")
        if adjudication.get("missing_required_fields") != []:
            errors.append("human adjudication cannot retain missing required fields")
        source = adjudication.get("source_hashes", {})
        if source.get("pass_a_annotations_sha256") != PASS_A_SHA:
            errors.append("adjudication points to the wrong Pass-A source")
        if source.get("pass_b_annotations_sha256") != PASS_B_SHA:
            errors.append("adjudication points to the wrong Pass-B source")
        if source.get("pass_b_episodes_sha256") != EPISODES_SHA:
            errors.append("adjudication points to the wrong episode source")
        if source.get("fixture_author_expectations_plaintext_sha256") != AUTHOR_PLAINTEXT_SHA:
            errors.append("adjudication points to the wrong author commitment")

        provisional = load_json(
            pass_b_dir / "adjudicated-material-fields-provisional-v0.1.json"
        )
        if provisional.get("status") != "PROVISIONAL_AWAITING_PCT_P1_D15":
            errors.append("adjudicated layer must remain provisional until D15")
        if set(provisional.get("codebook_consistency_conflict_case_ids", [])) != CONFLICT_IDS:
            errors.append("D15 conflict set must be dev-023, dev-012, and dev-017")
        if provisional.get("unresolved_required_fields") != 0:
            errors.append("submitted required adjudication fields should not remain unresolved")

        raw = load_json(reports / "raw-ab-intrarater-report-v0.1.json")
        if raw.get("paired_items") != 12:
            errors.append("raw A/B report denominator must be 12")
        if raw.get("administrative_reserve_excluded") != 5:
            errors.append("raw A/B report must exclude five reserve cases")
        expected = {
            "accept_decision": 11,
            "outcome_verdict": 12,
            "process_verdict": 11,
            "certification_recommendation": 8,
            "stop_scope": 12,
            "recovery_authority": 12,
            "valid_alternative_path": 3,
        }
        metrics = raw.get("nominal_and_layer_metrics", {})
        for field, count in expected.items():
            if metrics.get(field, {}).get("agree") != count:
                errors.append(f"raw A/B agreement mismatch for {field}")
        if raw.get("status") != "DETERMINISTIC_RECONSTRUCTION_FROM_FROZEN_A_B_AFTER_AUTHOR_OPENING":
            errors.append("raw report must disclose reconstructed provenance")
        if not raw.get("provenance_limitations"):
            errors.append("raw report must preserve the missing-persistence limitation")

        opening = load_json(reports / "author-opening-verification-v0.1.json")
        if opening.get("verified") is not True or opening.get("plaintext_hash_match") is not True:
            errors.append("author opening must be cryptographically verified")
        if opening.get("plaintext_sha256_actual") != AUTHOR_PLAINTEXT_SHA:
            errors.append("opened author plaintext hash mismatch")
        if opening.get("not_gold") is not True:
            errors.append("Author Intent must remain non-Gold")
        audit = opening.get("historical_order_audit", {})
        if audit.get("claimed_pre_author_order_independently_verified") is not False:
            errors.append("opening record must not overclaim historical pre-opening proof")
        if audit.get("raw_ab_metrics_reconstructed_after_opening") is not True:
            errors.append("opening record must disclose post-opening A/B reconstruction")

        subset = load_json(
            pass_b_dir / "opened-author-expectations-subset-v0.1.json"
        )
        if subset.get("subset_count") != 12 or subset.get("not_gold") is not True:
            errors.append("opened author subset must contain 12 non-Gold records")
        subset_text = json.dumps(subset)
        if "key_b64" in subset_text or "nonce_b64" in subset_text:
            errors.append("author subset must not contain custody key material")

        reliability = load_json(
            reports / "reliability-matrix-provisional-v0.1.json"
        )
        if reliability.get("status") != (
            "PROVISIONAL_AWAITING_PCT_P1_D15_AND_RESEARCH_OWNER_CLOSURE_APPROVAL"
        ):
            errors.append("reliability matrix must remain provisional")
        if reliability.get("p2_recommendation", {}).get(
            "online_intervention_authorized"
        ) is not False:
            errors.append("P1 may not authorize online intervention")
    finally:
        temp.cleanup()

    gate = load_json(ROOT / "governance" / "p1-outcome-semantics-gate-v0.1.json")
    if gate.get("decision_id") != "PCT-P1-D15" or gate.get("status") != "PENDING_HUMAN":
        errors.append("D15 must remain a pending human decision")
    if gate.get("agent_recommendation") != "A":
        errors.append("D15 agent recommendation must be A")
    if set(item["trajectory_id"] for item in gate.get("affected_cases", [])) != CONFLICT_IDS:
        errors.append("D15 affected cases mismatch")

    status = load_json(
        ROOT / "governance" / "p1-closure-readiness-status-v0.1.json"
    )
    if status.get("p1_closed") is not False:
        errors.append("P1 cannot be closed before D15 and final approval")
    if status.get("p2_authorized") is not False:
        errors.append("P2 cannot be authorized by closure preparation")
    if status.get("effectiveness_claim_allowed") is not False:
        errors.append("P1 cannot permit effectiveness claims")
    if status.get("open_normative_gate_ids") != ["PCT-P1-D15"]:
        errors.append("closure status must expose D15 as the only normative gate")
    if status.get("provenance_incident_ids") != ["PCT-P1-I01"]:
        errors.append("closure status must expose the persistence incident")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("P1 closure-readiness validation failed:", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1
    print(
        "P1 closure-readiness validation passed: frozen Pass B and adjudication "
        "are reproducibly materialized, A/B metrics were reconstructed, the author "
        "commitment matches, PCT-P1-I01 is disclosed, and D15 remains the sole blocker."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
