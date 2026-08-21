from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / 'scripts' / 'validate_p0.py'
spec = importlib.util.spec_from_file_location('validate_p0', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class ApprovedP0Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.register = json.loads((ROOT / 'governance' / 'decision-register.json').read_text(encoding='utf-8'))
        self.status = json.loads((ROOT / 'governance' / 'p0-status.json').read_text(encoding='utf-8'))
        self.roles = json.loads((ROOT / 'governance' / 'role-assignments.json').read_text(encoding='utf-8'))

    def test_repository_register_is_valid(self) -> None:
        self.assertEqual(module.validate_decision_register(self.register), [])

    def test_all_human_decisions_are_resolved(self) -> None:
        self.assertTrue(all(item['status'] == 'approved' for item in self.register['decisions']))
        self.assertEqual(self.status['blocking_decision_ids'], [])

    def test_human_choices_match_pr_comment(self) -> None:
        expected = ['A', 'A', 'A', 'A', 'A', 'A', 'A', 'B', 'A', 'A']
        self.assertEqual([item['human_decision'] for item in self.register['decisions']], expected)

    def test_agent_cannot_own_normative_decision(self) -> None:
        mutated = json.loads(json.dumps(self.register))
        mutated['decisions'][0]['owner_role'] = 'Research Builder Agent'
        errors = module.validate_decision_register(mutated)
        self.assertTrue(any('human owner role' in error for error in errors))

    def test_resolved_decision_requires_rejected_options(self) -> None:
        mutated = json.loads(json.dumps(self.register))
        mutated['decisions'][0]['rejected_options_and_reasons'] = []
        errors = module.validate_decision_register(mutated)
        self.assertTrue(any('rejected options' in error for error in errors))

    def test_p0_status_is_approved(self) -> None:
        self.assertEqual(module.validate_status(self.status, self.register), [])
        self.assertEqual(self.status['status'], 'approved')
        self.assertTrue(self.status['next_phase_authorized'])

    def test_deferred_roles_have_gates(self) -> None:
        self.assertEqual(module.validate_roles(self.roles), [])
        by_role = {item['role']: item for item in self.roles['assignments']}
        self.assertEqual(by_role['Methods / Statistics Lead']['status'], 'deferred')
        self.assertEqual(by_role['Independent Custodian']['status'], 'deferred')

    def test_p0_is_not_effectiveness_evidence(self) -> None:
        text = (ROOT / 'docs' / 'p0' / 'protocol-v0.1.md').read_text(encoding='utf-8')
        self.assertIn('does **not** establish that the proposed method is effective', text)

    def test_project_independence_is_preserved(self) -> None:
        text = (ROOT / 'AGENTS.md').read_text(encoding='utf-8')
        self.assertIn('not a GoalEvo subproject', text)

    def test_exit_gate_is_closed(self) -> None:
        text = (ROOT / 'docs' / 'p0' / 'p0-exit-gate.md').read_text(encoding='utf-8')
        self.assertIn('P0 approved and complete', text)


if __name__ == '__main__':
    unittest.main()
