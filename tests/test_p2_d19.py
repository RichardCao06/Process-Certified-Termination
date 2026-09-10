from __future__ import annotations
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("d19_runner", ROOT / "scripts/run_p2_engineering_smoke.py")
runner = importlib.util.module_from_spec(spec); sys.modules[spec.name] = runner; spec.loader.exec_module(runner)

class D19Tests(unittest.TestCase):
    def test_caps_and_cost_domination(self):
        caps = json.loads((ROOT / "governance/p2-operational-caps-v0.1.json").read_text())
        self.assertTrue(caps["monetary_guard"]["token_cap_implies_monetary_cap"])
        cost = runner.estimate_cost({"inputTokens": 0, "outputTokens": 200000, "cacheReadTokens": 0, "cacheWriteTokens": 0}, caps)
        self.assertLess(cost["cny_policy_guard"], 30)

    def test_artifact_validators(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "answer.txt").write_text("PCT-SMOKE-OK\n")
            self.assertTrue(runner.validate_artifact(root, {"type": "EXACT_TEXT", "path": "answer.txt", "expected": "PCT-SMOKE-OK\n"})[0])
            (root / "summary.json").write_text('{"count":4,"sum":20,"min":2,"max":9}')
            self.assertTrue(runner.validate_artifact(root, {"type": "JSON_OBJECT_EXACT", "path": "summary.json", "expected": {"count":4,"sum":20,"min":2,"max":9}})[0])

    def test_exact_candidate_stop_proposal(self):
        expected = {"stop_scope":"GOAL_COMPLETION_PROPOSAL","recovery_authority":"NOT_APPLICABLE","worker_claim":"COMPLETE","claims_goal_complete":True}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root / ".pct").mkdir()
            (root / ".pct/candidate-stop-proposal.json").write_text(json.dumps(expected))
            self.assertEqual(runner.read_exact_proposal(root, expected)[1], "EXACT")
            wrong = dict(expected); wrong["worker_claim"] = "TURN_COMPLETE"
            (root / ".pct/candidate-stop-proposal.json").write_text(json.dumps(wrong))
            self.assertEqual(runner.read_exact_proposal(root, expected)[1], "PROPOSAL_MISMATCH")

    def test_child_environment_removes_real_secrets(self):
        source = {"PATH": os.environ.get("PATH", ""), "DEEPSEEK_API_KEY": "real-key", "GITHUB_TOKEN": "token", "OTHER": "ok"}
        child = runner.sanitize_child_environment(source, "local-token", "http://127.0.0.1:1", Path("base.yml"), Path("home"))
        self.assertEqual(child["DEEPSEEK_API_KEY"], "local-token")
        self.assertNotIn("GITHUB_TOKEN", child)
        self.assertNotIn("real-key", child.values())

    def test_tool_catalog_extraction(self):
        payload = {"tools": [{"type":"function","function":{"name":"write"}}, {"type":"function","function":{"name":"read"}}]}
        self.assertEqual(runner.extract_wire_tool_names(payload), ["read", "write"])
        events = [{"event":{"type":"request/header","data":{"header":{"tools":[{"name":"write"},{"name":"read"}]}}}}]
        self.assertEqual(runner.extract_request_header_tool_sets(events), [["read", "write"]])

    def test_binding_report_offline(self):
        report = runner.build_binding_report({"object":"list","data":[{"id":"deepseek-v4-pro","object":"model","owned_by":"deepseek"}]}, {"operational_profile_sha256":"a"*64}, "2026-08-26T00:00:00Z")
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["response"]["returned_model_identifier"], "deepseek-v4-pro")
        self.assertEqual(report["request"]["chat_completion_calls"], 0)

    def test_fixture_and_runtime_catalog_isolation(self):
        fixtures = json.loads((ROOT / "data/p2/engineering-smoke/fixture-catalog-v0.1.json").read_text())
        tools = json.loads((ROOT / "config/p2/d19-runtime-tool-catalog-v0.1.json").read_text())
        self.assertEqual(len(fixtures["fixtures"]), 2)
        self.assertTrue(fixtures["excluded_from_60_trajectory_schedule"])
        self.assertFalse(fixtures["primary_analysis_denominator"])
        self.assertEqual(tools["model_facing_tool_names"], ["edit", "read", "write"])
        self.assertNotIn("bash", tools["model_facing_tool_names"])

    def test_secret_pattern_has_left_boundary(self):
        self.assertIsNone(runner.FORBIDDEN_SECRET_PATTERN.search("risk-assessment-boundary"))
        self.assertIsNotNone(runner.FORBIDDEN_SECRET_PATTERN.search("token=" + "sk-" + "abcdefghijklmnopqrstuvwx"))

    def test_d19_static_validator(self):
        result = subprocess.run([sys.executable, "scripts/validate_p2_d19.py"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

if __name__ == "__main__": unittest.main()
