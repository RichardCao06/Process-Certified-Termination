#!/usr/bin/env python3
"""One-shot safe materializer for the P2 D12 append-only payload.

This bootstrap file deletes itself, its payload, and its temporary workflow
before the materialized commit is created.
"""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD_PARTS = [
    ROOT / f"data/p2/bootstrap/p2-d12-payload-v0.1.part-{index:02d}.b64"
    for index in range(4)
]
EXPECTED_ARCHIVE_SHA256 = "08e9c5923f3a6499689040d7cfceb661991c6cea5e230a61af39e5687361ad78"
EXPECTED_FILES = {
  ".github/workflows/p0-validate.yml": "704348e69152ef94bfb30d018ce2ed0a3a030d67ff91ff1eaea1adc844b12019",
  "data/p2/conformance/dsh-contract-manifest-v0.1.json": "fe0fedfb804d30a2a60ae601656d82c2e884f6a53313ccd8bb3147da6ba81372",
  "data/p2/conformance/dsh-durable-envelope-v0.1.json": "c2dd08ad03ddd74b452d0ec621aa3ef0660eac2a0c549f1df8c23a292441397d",
  "data/p2/fixtures/synthetic-regression-catalog-v0.1.json": "7513a3269ec49e93808f3eee4ecd3e22a71f523fb3b1e25681b04073807d4e82",
  "docs/p2/README.md": "986a7ca7e3e65e9c7b4f64acb85273f7fe67ff5f325617370f7eefab6432c8e9",
  "docs/p2/p2-candidate-stop-sidecar-contract-v0.1.md": "baf8b3f98bfc936a1c949450de7c6dcbf7bb7852b08fc76b5c96dc76d9f4dbb7",
  "docs/p2/p2-data-and-isolation-boundary-v0.1.md": "ecec97faa8a23bc1bea9e2d03e16cd7ae0b1ff29ba862a91efa812b08f8f8df0",
  "docs/p2/p2-dsh-conformance-report-v0.1.md": "c381ce25d456e56f48321d95cbfc5800e66b3d5f4643997e7a598cff4ac8ca32",
  "docs/p2/p2-human-decision-pack-d12-v0.1.md": "e5740ac997b732192d9da4e1b80cbae216c346bba3ae1d7a748729253818435e",
  "docs/p2/p2-human-decision-pack-d13-d18-v0.1.md": "6fbe0f48d3c476b1ca9554f98b836e54e7f012484ce37ae62fe39fe2d775488c",
  "docs/p2/p2-state-reconciliation-record-v0.1.md": "963412f4302a4ce3cd300fa8e0d8b788afa86c650412cb0cfc166d6d3a2ffc14",
  "docs/p2/p2-synthetic-shadow-regression-v0.1.md": "2bef32ee5b94392a3f3671e02f5d7a78371be5f4338bb7747518865171ce679d",
  "docs/p2/work-order-PCT-P2-001-v0.2.md": "89a687c7317b64c422e99d6abfe7cfe3c03f72de24503167bdcf3545c66b9b69",
  "governance/p2-decision-register-v0.2.json": "503b2d14e3e3ae2713e97bcc5919240eaa60b38beeb06952caa2a2d9aea6cd91",
  "governance/p2-dsh-freeze-v0.1.json": "c0a8de474c0d0c4fce0946e688ef6892fe6e3a95ecf244ccec2a9b6f4c6d136b",
  "governance/p2-human-approval-d01-d12-v0.1.json": "0178a4292e465b603112414ec3b33d98374d95b0a489a6b91cda58e11b3153dc",
  "governance/p2-shadow-policy-v0.1.json": "2473990406811f8d84a7d0d6dac438b1a1ad553ed73ec15857f151f9b85676f9",
  "governance/p2-state-reconciliation-record-v0.1.json": "6c84050ea05a4410c848b514caab249efda7069b06116f6928228a9d40b24758",
  "governance/p2-status-v0.2.json": "7c683afb77220482d5fda70930f48c25b7146d5805aced1709cddaaed7b91abc",
  "pct/shadow/__init__.py": "02e4dd154ccf593f43c94cae49ae465ede74e36b893131161ef750f6c56e66dd",
  "pct/shadow/adapter.py": "ed4893a14174266944c143d3da11e8740aef6be4ea564b0afb942fb13baf5206",
  "pct/shadow/auditor.py": "4f825bf570295b1eb1ccad7da2828c2cb91209e78b38fdc5e71227a84b0c6654",
  "pct/shadow/checks.py": "3389160c9eef59eccf830bbad94d18140de2f143d45857f32b79b898c6ab765e",
  "pct/shadow/metrics.py": "c24022a8535fcb46279442cf8c5eb28b452f8826d9fea54f6fd4109205b083ec",
  "pct/shadow/models.py": "57e0a6f4e7cc17ca6dd5e0c35b1630e0ec47ab23e07da53229e9c3bd104f56e8",
  "pct/shadow/regression.py": "bb8b7f21f88841a8d5cb4f539b9a154966513b6a0d6aeb14b4d8efd5641c2b31",
  "pct/shadow/replay.py": "b9c0a89e7384561d374eac92fab1e4c0bb875c9a38c3b3062b24536e4c4884c4",
  "pct/shadow/sidecar.py": "2461c25c86e5722d784a46564608ae7939f5e37b91b88aefcf48352694f4973d",
  "pct/shadow/snapshot.py": "421c960fedc02eb92dc3377c3a15f16f49dfa530403f7693110ae6a5b69faa13",
  "reports/p2/d12-sidecar-validation-v0.1.json": "87f878d4cd84fa2d766268372b1e44a93f7aef3e128c44d045f8eb9c34b22e85",
  "reports/p2/dsh-conformance-report-v0.1.json": "855713298ad273a26e2d8d1592755d65b02eb46e40ddd02add8f42be6aab3fec",
  "reports/p2/synthetic-shadow-regression-freeze-v0.1.json": "983a33cf63d8864b66566d4a5b21c0a239509f3c5e3fad780cbda2ad29da695a",
  "reports/p2/synthetic-shadow-regression-v0.1.json": "66a33baaa378c50c6b86928c061ee7133519d170723462720af1b0c20cc00e98",
  "schemas/pct-p2-candidate-stop-sidecar-v0.1.schema.json": "5bffa58bf138894abba2ee275e536ac4c55b1ff661e3952077b1746dd55f7464",
  "schemas/pct-p2-candidate-stop-snapshot-v0.1.schema.json": "2b5334a359557b6f70fcb01fa1cd8982d3eeb1e83e1fcf9df8287362510f7946",
  "schemas/pct-p2-replay-bundle-v0.1.schema.json": "e242d8bc600909d107c70d2502e408141d80c0d4026d9e6cd808f9aa32d88a39",
  "schemas/pct-p2-shadow-verdict-v0.1.schema.json": "a8e32985751f38ac38ce125c776ee2041a37c0fd1563b13c3220bc8f2cacb518",
  "scripts/run_p2_synthetic_regression.py": "493abe9aa6a3fdad8864bfe44787c56e5279cee933487feef2f87d2359206b17",
  "scripts/validate_p2_active.py": "b2c80289b7411fd23a94048a104444715ce77a4eb92f095afde0f94cd0e5abfc",
  "scripts/validate_p2_dsh_conformance.py": "ab0a4cb72fda2b9389d26cd66cf4dd0f68d0750f3f84884ab7cf33d4d0ce4acc",
  "tests/test_p2_regression.py": "4356c0fca32b98f0deab5dfce890da0fa7b7b34478bdb4c81bd4b0ae2d0765b9",
  "tests/test_p2_shadow_foundation.py": "87ef7a025e931f1e3db215c8fddd151658845c4980b63a5bdfef8eca7a810968",
  "tests/test_p2_sidecar.py": "b3e414aa718813bb71fb672e9d9b6dfba165de1d734c91b9a059970958768f08"
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_member(name: str) -> Path:
    path = Path(name)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError(f"unsafe archive member: {name}")
    return path


def main() -> int:
    encoded = "".join(path.read_text(encoding="ascii") for path in PAYLOAD_PARTS)
    raw = base64.b64decode(encoded, validate=True)
    if hashlib.sha256(raw).hexdigest() != EXPECTED_ARCHIVE_SHA256:
        raise ValueError("bootstrap archive SHA-256 mismatch")
    archive_path = ROOT / ".p2-d12-payload.tar.gz"
    archive_path.write_bytes(raw)
    try:
        with tarfile.open(archive_path, "r:gz") as archive:
            members = archive.getmembers()
            actual_names = {member.name for member in members}
            if actual_names != set(EXPECTED_FILES):
                raise ValueError("bootstrap archive file set mismatch")
            for member in members:
                safe_member(member.name)
                if not member.isfile():
                    raise ValueError(f"non-regular archive member: {member.name}")
            archive.extractall(ROOT, filter="data")
    finally:
        archive_path.unlink(missing_ok=True)
    for relative, expected in EXPECTED_FILES.items():
        target = ROOT / relative
        if not target.is_file() or sha256(target) != expected:
            raise ValueError(f"materialized file hash mismatch: {relative}")
    for relative in (
        ".github/workflows/p2-materialize-d12.yml",
        "scripts/materialize_p2_d12_bundle.py",
        "data/p2/bootstrap/p2-d12-payload-v0.1.part-00.b64",
        "data/p2/bootstrap/p2-d12-payload-v0.1.part-01.b64",
        "data/p2/bootstrap/p2-d12-payload-v0.1.part-02.b64",
        "data/p2/bootstrap/p2-d12-payload-v0.1.part-03.b64",
    ):
        (ROOT / relative).unlink(missing_ok=True)
    bootstrap_dir = ROOT / "data/p2/bootstrap"
    if bootstrap_dir.exists() and not any(bootstrap_dir.iterdir()):
        bootstrap_dir.rmdir()
    print(json.dumps({"status":"PASS","archive_sha256":EXPECTED_ARCHIVE_SHA256,"materialized_files":len(EXPECTED_FILES)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
