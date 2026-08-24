#!/usr/bin/env python3
"""Validate the frozen 25-case P1 Development Pilot Pass A package."""
from __future__ import annotations

import base64
import csv
import hashlib
import json
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "data" / "p1" / "development-pilot"
PASS_A = PILOT / "pass-a"

EXPECTED_COMPLETED = [
    "dev-023", "dev-014", "dev-026", "dev-020", "dev-013",
    "dev-024", "dev-011", "dev-001", "dev-005", "dev-008",
    "dev-006", "dev-019", "dev-012", "dev-010", "dev-003",
    "dev-027", "dev-028", "dev-021", "dev-009", "dev-025",
    "dev-015", "dev-016", "dev-017", "dev-004", "dev-022",
]
EXPECTED_RESERVE = ["dev-030", "dev-007", "dev-002", "dev-029", "dev-018"]
EXPECTED_ALL = EXPECTED_COMPLETED + EXPECTED_RESERVE
EXPECTED_ANNOTATION_SHA256 = "d561b442053293c94c13db6ff5c49af6ef187fa12cff351f0e94dbb1e92364b8"
EXPECTED_TIMING_SHA256 = "c484a8813598ffcc0b3eac40867b6d9c89c4e342b152d7c01756747b4c0fc413"
EXPECTED_PASS_B_COMMITMENT = "1465d1b21da860660a90a24b5e9c1bc8673c49f4052fbf8d647c15f55e026e86"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def extract_bundle() -> tuple[tempfile.TemporaryDirectory[str], Path]:
    manifest = load_json(PASS_A / "bundle-manifest.json")
    encoded = "".join(
        "".join((PASS_A / part).read_text(encoding="utf-8").split())
        for part in manifest["parts"]
    )
    archive = base64.b64decode(encoded, validate=True)
    if sha256_bytes(archive) != manifest["sha256"]:
        raise ValueError("Pass-A archive SHA-256 mismatch")
    temp = tempfile.TemporaryDirectory(prefix="pct-p1-dev-pass-a-")
    root = Path(temp.name).resolve()
    archive_path = root / manifest["decoded_filename"]
    archive_path.write_bytes(archive)
    with tarfile.open(archive_path, "r:gz") as tf:
        for member in tf.getmembers():
            target = (root / member.name).resolve()
            if target != root and root not in target.parents:
                raise ValueError(f"unsafe archive path: {member.name}")
        tf.extractall(root, filter="data")
    return temp, root


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


def validate() -> list[str]:
    errors: list[str] = []
    required = [
        PASS_A / "bundle-manifest.json",
        PASS_A / "bundle-parts" / "part-00",
        PASS_A / "delivery-manifest-v0.2.json",
        PILOT / "pass-b" / "subset-commitment-v0.1.json",
        ROOT / "docs" / "p1" / "amendment-PCT-P1-A01.md",
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"missing required Pilot artifact: {path.relative_to(ROOT)}")
    if errors:
        return errors

    temp, data_root = extract_bundle()
    try:
        annotations_path = data_root / "data/p1/development-pilot/pass-a/human-pass-a-raw.jsonl"
        timing_path = data_root / "data/p1/development-pilot/pass-a/timing-raw.csv"
        freeze_path = data_root / "data/p1/development-pilot/pass-a/freeze-manifest-v0.1.json"
        qc_path = data_root / "reports/p1/development-pilot-pass-a-structural-qc-v0.1.json"
        for path in (annotations_path, timing_path, freeze_path, qc_path):
            if not path.is_file():
                errors.append(f"archive missing {path.relative_to(data_root)}")
        if errors:
            return errors

        if sha256_bytes(annotations_path.read_bytes()) != EXPECTED_ANNOTATION_SHA256:
            errors.append("raw Pass-A annotation SHA-256 mismatch")
        if sha256_bytes(timing_path.read_bytes()) != EXPECTED_TIMING_SHA256:
            errors.append("raw Pass-A timing SHA-256 mismatch")

        annotations = read_jsonl(annotations_path)
        if len(annotations) != 25:
            errors.append(f"expected 25 completed annotations, got {len(annotations)}")
        ids = [item.get("trajectory_id") for item in annotations]
        displays = [item.get("display_id") for item in annotations]
        if ids != EXPECTED_COMPLETED:
            errors.append("completed trajectory order differs from the frozen first 25 positions")
        if displays != [f"P1-DEV-A-{i:02d}" for i in range(1, 26)]:
            errors.append("completed display IDs must be P1-DEV-A-01 through A-25")
        if len(set(ids)) != len(ids) or len(set(displays)) != len(displays):
            errors.append("completed annotation identifiers must be unique")

        with timing_path.open(newline="", encoding="utf-8") as handle:
            timing = list(csv.DictReader(handle))
        if len(timing) != 30:
            errors.append(f"expected 30 timing rows, got {len(timing)}")
        timing_ids = [row["trajectory_id"] for row in timing]
        if timing_ids != EXPECTED_ALL:
            errors.append("timing rows do not follow the fixed 30-episode order")
        first_seconds = [int(row["seconds"]) for row in timing[:25]]
        reserve_seconds = [int(row["seconds"]) for row in timing[25:]]
        if any(value <= 0 for value in first_seconds):
            errors.append("completed episodes must have positive timing values")
        if reserve_seconds != [0, 0, 0, 0, 0]:
            errors.append("unannotated reserve cases must remain zero in the raw timing export")

        freeze = load_json(freeze_path)
        if freeze.get("completed_episode_count") != 25 or freeze.get("planned_episode_count") != 30:
            errors.append("freeze manifest count mismatch")
        if freeze.get("completed_trajectory_ids") != EXPECTED_COMPLETED:
            errors.append("freeze manifest completed IDs mismatch")
        if freeze.get("unannotated_trajectory_ids") != EXPECTED_RESERVE:
            errors.append("freeze manifest reserve IDs mismatch")
        treatment = freeze.get("missingness_treatment", {})
        if treatment.get("classification") != "ADMINISTRATIVE_RIGHT_TRUNCATION_AFTER_FIXED_ORDER_POSITION_25":
            errors.append("missingness must be recorded as administrative right truncation")
        if treatment.get("imputation") != "NONE":
            errors.append("reserve cases must not be imputed")
        if freeze.get("blinding", {}).get("fixture_author_expectations_opened") is not False:
            errors.append("Fixture Author Expectations must remain unopened")
        if freeze.get("effectiveness_claim_allowed") is not False:
            errors.append("P1 Pilot cannot allow effectiveness claims")

        qc = load_json(qc_path)
        if qc.get("records_checked") != 25 or qc.get("input_sha256") != EXPECTED_ANNOTATION_SHA256:
            errors.append("structural QC provenance mismatch")
        if qc.get("fixture_author_expectations_used") is not False:
            errors.append("structural QC must not use Fixture Author Expectations")
        if qc.get("case_level_semantic_adjudication_performed") is not False:
            errors.append("case-level semantic feedback must remain embargoed before Pass B")
        if qc.get("results", {}).get("records_with_internal_hard_error") != 1:
            errors.append("aggregate structural-QC issue count changed unexpectedly")
        if qc.get("results", {}).get("records_with_empty_event_and_evidence_citations") != 25:
            errors.append("aggregate citation-gap count changed unexpectedly")

        delivery = load_json(PASS_A / "delivery-manifest-v0.2.json")
        if delivery.get("episode_count") != 30:
            errors.append("original Pass-A delivery manifest must record 30 source episodes")
        if "PCT_P1_Development_Pilot_Pass_A_v0.2.zip" not in delivery.get("files", {}):
            errors.append("delivery manifest is missing the original Pass-A ZIP commitment")
        if "PCT_P1_Development_Pilot_Author_Key_Custody_v0.2.zip" not in delivery.get("files", {}):
            errors.append("delivery manifest is missing the out-of-repository author-key custody commitment")

        commitment = load_json(PILOT / "pass-b" / "subset-commitment-v0.1.json")
        if commitment.get("source_pass_a_sha256") != EXPECTED_ANNOTATION_SHA256:
            errors.append("Pass-B subset commitment points to the wrong Pass-A file")
        if commitment.get("selected_count") != 12:
            errors.append("Pass B must remain a 12-case subset")
        if commitment.get("ordered_subset_sha256") != EXPECTED_PASS_B_COMMITMENT:
            errors.append("Pass-B ordered-subset commitment mismatch")
        if commitment.get("identifiers_disclosed_before_pass_b") is not False:
            errors.append("Pass-B identifiers must remain undisclosed before release")
        if "selected_trajectory_ids" in commitment or "ordered_trajectory_ids" in commitment:
            errors.append("Pass-B commitment must not disclose selected IDs")
        if commitment.get("fixture_author_expectations_used") is not False:
            errors.append("Pass-B selection must not use Fixture Author Expectations")

        status = load_json(ROOT / "governance" / "p1-status.json")
        if status.get("pilot_stage") != "development-pilot-pass-a-25-frozen":
            errors.append("P1 status must record the 25-case Pass-A freeze")
        design = status.get("pilot_design", {})
        if design.get("pass_a_completed_episodes") != 25 or design.get("pass_a_unannotated_reserve") != 5:
            errors.append("P1 status Pilot counts mismatch")
        if design.get("pass_b_selected_episodes") != 12:
            errors.append("P1 status must record the 12-case Pass-B subset")
        if status.get("fixture_author_expectations_opened") is not False:
            errors.append("P1 status must record unopened Fixture Author Expectations")
        if status.get("held_out_or_sealed_data_accessed") is not False:
            errors.append("P1 status must record no held-out or sealed data access")
        if status.get("effectiveness_claim_allowed") is not False:
            errors.append("P1 status cannot allow effectiveness claims")
    finally:
        temp.cleanup()
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("P1 Development Pilot Pass-A validation failed:")
        for error in errors:
            print(f" - {error}")
        return 1
    print(
        "P1 Development Pilot Pass-A validation passed: "
        "25 raw annotations are frozen, five reserve cases are excluded without imputation, "
        "and the 12-case delayed Pass-B subset remains hash-committed and undisclosed."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
