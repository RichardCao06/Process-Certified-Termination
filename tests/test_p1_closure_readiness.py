from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_p1_closure_readiness.py"


class P1ClosureReadinessTests(unittest.TestCase):
    def test_closure_readiness_artifacts_validate(self) -> None:
        spec = importlib.util.spec_from_file_location("validate_p1_closure_readiness", SCRIPT)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual([], module.validate())

    def test_d15_is_the_only_open_normative_gate(self) -> None:
        import json
        status = json.loads(
            (ROOT / "governance" / "p1-closure-readiness-status-v0.1.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(["PCT-P1-D15"], status["open_normative_gate_ids"])
        self.assertFalse(status["p1_closed"])
        self.assertFalse(status["p2_authorized"])


if __name__ == "__main__":
    unittest.main()
