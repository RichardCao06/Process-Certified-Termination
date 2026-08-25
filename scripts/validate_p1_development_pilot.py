#!/usr/bin/env python3
"""Validate the frozen P1 Pass A and released 12-case Pass B participant package."""
from __future__ import annotations

import base64
import csv
from datetime import datetime, timezone
import hashlib
import json
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "data" / "p1" / "development-pilot"
PASS_A = PILOT / "pass-a"
PASS_B = PILOT / "pass-b"

EXPECTED_COMPLETED = [
    "dev-023", "dev-014", "dev-026", "dev-020", "dev-013",
    "dev-024", "dev-011", "dev-001", "dev-005", "dev-008",
    "dev-006", "dev-019", "dev-012", "dev-010", "dev-003",
    "dev-027", "dev-028", "dev-021", "dev-009", "dev-025",
    "dev-015", "dev-016", "dev-017", "dev-004", "dev-022",
]
EXPECTED_RESERVE = ["dev-030", "dev-007", "dev-002", "dev-029", "dev-018"]
EXPECTED_ALL = EXPECTED_COMPLETED + EXPECTED_RESERVE
EXPECTED_PASS_B_ORDER = [
    "dev-014", "dev-006", "dev-023", "dev-010", "dev-016", "dev-012",
    "dev-021", "dev-027", "dev-028", "dev-017", "dev-009", "dev-026",
]
EXPECTED_ANNOTATION_SHA256 = "d561b442053293c94c13db6ff5c49af6ef187fa12cff351f0e94dbb1e92364b8"
EXPECTED_TIMING_SHA256 = "c484a8813598ffcc0b3eac40867b6d9c89c4e342b152d7c01756747b4c0fc413"
EXPECTED_PASS_B_COMMITMENT = "1465d1b21da860660a90a24b5e9c1bc8673c49f4052fbf8d647c15f55e026e86"
EXPECTED_PASS_A_FREEZE_TIME = "2026-08-24T07:48:20Z"
EXPECTED_ORIGINAL_RELEASE = "2026-08-27T07:48:20Z"
EXPECTED_AMENDED_RELEASE = "2026-08-24T19:48:20Z"
EXPECTED_MINIMUM_DELAY_HOURS = 12
EXPECTED_PASS_B_ZIP_SHA256 = "264064f716d1a4b734a54afba9679869a832b90826ac8e0ee63dd224921765f6"
EXPECTED_PASS_B_HTML_SHA256 = "5ef9766d326b0bb8a84cceb3decc2e57ccd709005b533507053d8e63e384e462"
EXPECTED_PASS_B_EPISODES_SHA256 = "d5f5bc3dc0172d1e3f860037d178306d87f1514048835272fb326d69e3769e90"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_order_sha(values: list[str]) -> str:
    return sha256_bytes(json.dumps(values, separators=(",", ":")).encode("utf-8"))


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
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


def decode_base64_parts(root: Path, manifest: dict) -> bytes:
    encoded = "".join(
        "".join((root / part).read_text(encoding="utf-8").split())
        for part in manifest["parts"]
    )
    return base64.b64decode(encoded, validate=True)


def extract_pass_a_bundle() -> tuple[tempfile.TemporaryDirectory[str], Path]:
    manifest = load_json(PASS_A / "bundle-manifest.json")
    archive = decode_base64_parts(PASS_A, manifest)
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


def _validate_commitment_common(commitment: dict, label: str, errors: list[str]) -> None:
    if commitment.get("source_pass_a_sha256") != EXPECTED_ANNOTATION_SHA256:
        errors.append(f"{label} points to the wrong Pass-A file")
    if commitment.get("selected_count") != 12:
        errors.append(f"{label} must preserve a 12-case subset")
    if commitment.get("ordered_subset_sha256") != EXPECTED_PASS_B_COMMITMENT:
        errors.append(f"{label} ordered-subset commitment mismatch")
    if commitment.get("identifiers_disclosed_before_pass_b") is not False:
        errors.append(f"{label} must record that identifiers were not disclosed before release")
    if any(key in commitment for key in ("selected_trajectory_ids", "ordered_trajectory_ids")):
        errors.append(f"{label} historical commitment must not contain selected IDs")
    if commitment.get("fixture_author_expectations_used") is not False:
        errors.append(f"{label} must not use Fixture Author Expectations")


def validate_pass_a(errors: list[str]) -> None:
    temp, data_root = extract_pass_a_bundle()
    try:
        annotations_path = data_root / "data/p1/development-pilot/pass-a/human-pass-a-raw.jsonl"
        timing_path = data_root / "data/p1/development-pilot/pass-a/timing-raw.csv"
        freeze_path = data_root / "data/p1/development-pilot/pass-a/freeze-manifest-v0.1.json"
        qc_path = data_root / "reports/p1/development-pilot-pass-a-structural-qc-v0.1.json"
        for path in (annotations_path, timing_path, freeze_path, qc_path):
            if not path.is_file():
                errors.append(f"Pass-A archive missing {path.relative_to(data_root)}")
        if errors:
            return
        if sha256_bytes(annotations_path.read_bytes()) != EXPECTED_ANNOTATION_SHA256:
            errors.append("raw Pass-A annotation SHA-256 mismatch")
        if sha256_bytes(timing_path.read_bytes()) != EXPECTED_TIMING_SHA256:
            errors.append("raw Pass-A timing SHA-256 mismatch")
        annotations = read_jsonl(annotations_path)
        if [item.get("trajectory_id") for item in annotations] != EXPECTED_COMPLETED:
            errors.append("Pass-A completed trajectory order mismatch")
        if [item.get("display_id") for item in annotations] != [f"P1-DEV-A-{i:02d}" for i in range(1, 26)]:
            errors.append("Pass-A display IDs mismatch")
        with timing_path.open(newline="", encoding="utf-8") as handle:
            timing = list(csv.DictReader(handle))
        if [row["trajectory_id"] for row in timing] != EXPECTED_ALL:
            errors.append("Pass-A timing order mismatch")
        if any(int(row["seconds"]) <= 0 for row in timing[:25]):
            errors.append("completed Pass-A episodes require positive timing")
        if [int(row["seconds"]) for row in timing[25:]] != [0, 0, 0, 0, 0]:
            errors.append("five reserve cases must remain zero/unannotated")
        freeze = load_json(freeze_path)
        if freeze.get("completed_trajectory_ids") != EXPECTED_COMPLETED:
            errors.append("Pass-A freeze completed IDs mismatch")
        if freeze.get("unannotated_trajectory_ids") != EXPECTED_RESERVE:
            errors.append("Pass-A reserve IDs mismatch")
        if freeze.get("missingness_treatment", {}).get("imputation") != "NONE":
            errors.append("Pass-A reserve cases must not be imputed")
        qc = load_json(qc_path)
        if qc.get("fixture_author_expectations_used") is not False:
            errors.append("Pass-A structural QC must not use author expectations")
        if qc.get("case_level_semantic_adjudication_performed") is not False:
            errors.append("Pass-A case-level semantic feedback must remain embargoed before Pass B")
    finally:
        temp.cleanup()


def validate_pass_b_release(errors: list[str]) -> None:
    release = load_json(PASS_B / "release-record-v0.1.json")
    delivery = load_json(PASS_B / "release-delivery-manifest-v0.1.json")
    if release.get("ordered_trajectory_ids") != EXPECTED_PASS_B_ORDER:
        errors.append("released Pass-B order differs from precommitted order")
    if canonical_order_sha(EXPECTED_PASS_B_ORDER) != EXPECTED_PASS_B_COMMITMENT:
        errors.append("internal expected Pass-B order no longer matches commitment")
    if release.get("ordered_subset_sha256") != EXPECTED_PASS_B_COMMITMENT:
        errors.append("Pass-B release record commitment mismatch")
    if release.get("commitment_verified") is not True:
        errors.append("Pass-B release record must state commitment verified")
    if release.get("selection_or_order_changed_at_release") is not False:
        errors.append("Pass-B selection/order changed at release")
    if parse_time(release["released_at"]) < parse_time(EXPECTED_AMENDED_RELEASE):
        errors.append("Pass B was released before the A02 gate")
    blinding = release.get("blinding", {})
    for key in (
        "pass_a_annotations_in_package",
        "pass_a_qc_in_package",
        "fixture_author_expectations_opened",
        "fixture_author_expectations_in_package",
        "hidden_evaluator_or_gold_in_package",
        "case_specific_semantic_feedback_in_package",
    ):
        if blinding.get(key) is not False:
            errors.append(f"Pass-B release blinding field must be false: {key}")

    if delivery.get("episode_count") != 12:
        errors.append("Pass-B delivery manifest must record 12 episodes")
    if delivery.get("ordered_trajectory_ids") != EXPECTED_PASS_B_ORDER:
        errors.append("Pass-B delivery manifest order mismatch")
    if delivery.get("ordered_subset_sha256") != EXPECTED_PASS_B_COMMITMENT:
        errors.append("Pass-B delivery manifest commitment mismatch")
    if delivery.get("commitment_verified") is not True:
        errors.append("Pass-B delivery manifest must record commitment verification")
    if delivery.get("contains_pass_a_annotations") is not False or delivery.get("contains_pass_a_qc") is not False:
        errors.append("Pass-B delivery manifest must exclude Pass-A labels and QC")
    if delivery.get("contains_fixture_author_expectations") is not False:
        errors.append("Pass-B delivery manifest must exclude Fixture Author Expectations")
    if delivery.get("held_out_or_sealed_data") is not False:
        errors.append("Pass-B delivery manifest must exclude held-out/sealed data")
    files = delivery.get("files", {})
    expected_files = {
        "PCT_P1_Development_Pilot_Pass_B_Bilingual_v0.1.html": EXPECTED_PASS_B_HTML_SHA256,
        "PCT_P1_Development_Pilot_Pass_B_Episodes_v0.1.json": EXPECTED_PASS_B_EPISODES_SHA256,
        "PCT_P1_Development_Pilot_Pass_B_v0.1.zip": EXPECTED_PASS_B_ZIP_SHA256,
    }
    for name, expected_hash in expected_files.items():
        if files.get(name, {}).get("sha256") != expected_hash:
            errors.append(f"Pass-B delivery file hash mismatch: {name}")
    release_files = release.get("participant_package", {})
    for name, expected_hash in expected_files.items():
        if release_files.get(name, {}).get("sha256") != expected_hash:
            errors.append(f"Pass-B release record file hash mismatch: {name}")


def validate() -> list[str]:
    errors: list[str] = []
    required = [
        PASS_A / "bundle-manifest.json",
        PASS_A / "bundle-parts" / "part-00",
        PASS_A / "delivery-manifest-v0.2.json",
        PASS_B / "subset-commitment-v0.1.json",
        PASS_B / "subset-commitment-v0.2.json",
        PASS_B / "release-record-v0.1.json",
        PASS_B / "release-delivery-manifest-v0.1.json",
        ROOT / "docs" / "p1" / "amendment-PCT-P1-A01.md",
        ROOT / "docs" / "p1" / "amendment-PCT-P1-A02.md",
        ROOT / "docs" / "p1" / "development-pilot-pass-b.md",
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"missing required Pilot artifact: {path.relative_to(ROOT)}")
    if errors:
        return errors

    validate_pass_a(errors)
    original = load_json(PASS_B / "subset-commitment-v0.1.json")
    amended = load_json(PASS_B / "subset-commitment-v0.2.json")
    _validate_commitment_common(original, "original Pass-B commitment", errors)
    _validate_commitment_common(amended, "amended Pass-B commitment", errors)
    if original.get("release_not_before") != EXPECTED_ORIGINAL_RELEASE:
        errors.append("historical v0.1 release condition must remain preserved")
    if amended.get("amendment_id") != "PCT-P1-A02":
        errors.append("effective Pass-B commitment must cite A02")
    if amended.get("pass_a_freeze_reference_time") != EXPECTED_PASS_A_FREEZE_TIME:
        errors.append("A02 uses the wrong Pass-A freeze time")
    if amended.get("minimum_delay_hours") != EXPECTED_MINIMUM_DELAY_HOURS:
        errors.append("A02 minimum delay must be 12 hours")
    if amended.get("release_not_before") != EXPECTED_AMENDED_RELEASE:
        errors.append("A02 release-not-before mismatch")
    if amended.get("selection_or_order_changed_by_amendment") is not False:
        errors.append("A02 must not change Pass-B selection/order")

    validate_pass_b_release(errors)

    status = load_json(ROOT / "governance" / "p1-status.json")
    if status.get("pilot_stage") != "development-pilot-pass-b-released-awaiting-human":
        errors.append("P1 status must record released Pass B awaiting human annotation")
    design = status.get("pilot_design", {})
    if design.get("pass_b_status") != "released-awaiting-human-annotation":
        errors.append("P1 status Pass-B status mismatch")
    if design.get("pass_b_released_at") != "2026-08-25T01:41:39Z":
        errors.append("P1 status Pass-B release timestamp mismatch")
    if design.get("pass_b_order_commitment_sha256") != EXPECTED_PASS_B_COMMITMENT:
        errors.append("P1 status commitment mismatch")
    if design.get("pass_b_commitment_verified_at_release") is not True:
        errors.append("P1 status must record release commitment verification")
    if status.get("fixture_author_expectations_opened") is not False:
        errors.append("Fixture Author Expectations must remain unopened")
    if status.get("held_out_or_sealed_data_accessed") is not False:
        errors.append("P1 status must record no held-out/sealed access")
    if status.get("effectiveness_claim_allowed") is not False:
        errors.append("P1 cannot allow effectiveness claims")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("P1 Development Pilot validation failed:")
        for error in errors:
            print(f" - {error}")
        return 1
    print(
        "P1 Development Pilot validation passed: Pass A remains frozen, the A02 gate elapsed, "
        "the released 12-case Pass-B package matches its precommitment, and author expectations remain unopened."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
