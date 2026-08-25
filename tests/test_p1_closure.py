from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_p1_closure.py"


class P1FinalClosureTests(unittest.TestCase):
    def _module(self):
        spec = importlib.util.spec_from_file_location("validate_p1_closure", SCRIPT)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_final_closure_validates(self) -> None:
        self.assertEqual([], self._module().validate())

    def test_p1_closed_but_p2_not_authorized(self) -> None:
        status = json.loads(
            (ROOT / "governance" / "p1-closure-status-v0.1.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertTrue(status["p1_closed"])
        self.assertEqual([], status["open_normative_gate_ids"])
        self.assertFalse(status["p2_authorized"])
        self.assertFalse(status["online_intervention_authorized"])
        self.assertFalse(status["effectiveness_claim_allowed"])

    def test_d15_corrections_are_append_only(self) -> None:
        record = json.loads(
            (
                ROOT
                / "data"
                / "p1"
                / "development-pilot"
                / "pass-b"
                / "human-adjudication-codebook-correction-v0.1.json"
            ).read_text(encoding="utf-8")
        )
        self.assertTrue(record["raw_adjudication_preserved_unchanged"])
        actual = {
            item["trajectory_id"]: item["corrected_value"]
            for item in record["corrections"]
        }
        self.assertEqual(
            {"dev-023": "UNKNOWN", "dev-012": "UNKNOWN", "dev-017": "PASS"},
            actual,
        )


if __name__ == "__main__":
    unittest.main()
