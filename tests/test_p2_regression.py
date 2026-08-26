from __future__ import annotations

import json
from pathlib import Path
import unittest

from pct.shadow.regression import catalog, run_regression

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / "governance/p2-shadow-policy-v0.1.json").read_text(encoding="utf-8"))


class P2RegressionTests(unittest.TestCase):
    def test_catalog_is_exactly_20_plus_10(self) -> None:
        items = catalog()["cases"]
        self.assertEqual(30, len(items))
        self.assertEqual(20, sum(x["stratum"] == "NORMAL_OR_BOUNDARY" for x in items))
        self.assertEqual(10, sum(x["stratum"] == "MALFORMED_OR_LEAKAGE" for x in items))

    def test_full_regression_passes_without_model_calls(self) -> None:
        report = run_regression(POLICY)
        self.assertEqual("PASS", report["status"])
        self.assertEqual(30, report["passed"])
        self.assertEqual(0, report["failed"])
        self.assertEqual(0, report["live_model_calls"])
        self.assertFalse(report["applied_to_runtime"])


if __name__ == "__main__":
    unittest.main()
