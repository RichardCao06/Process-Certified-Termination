from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / 'scripts' / 'validate_p0.py'
spec = importlib.util.spec_from_file_location('validate_p0', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class DecisionRegisterTests(unittest.TestCase):
    def setUp(self) -> None:
        with (Path(__file__).resolve().parents[1] / 'governance' / 'decision-register.json').open(encoding='utf-8') as handle:
            self.register = json.load(handle)

    def test_repository_register_is_valid(self) -> None:
        self.assertEqual(module.validate_decision_register(self.register), [])

    def test_agent_cannot_own_normative_decision(self) -> None:
        mutated = json.loads(json.dumps(self.register))
        mutated['decisions'][0]['owner_role'] = 'Research Builder Agent'
        errors = module.validate_decision_register(mutated)
        self.assertTrue(any('human owner role' in error for error in errors))

    def test_recommendation_must_reference_option(self) -> None:
        mutated = json.loads(json.dumps(self.register))
        mutated['decisions'][0]['agent_recommendation'] = 'Z'
        errors = module.validate_decision_register(mutated)
        self.assertTrue(any('recommendation' in error for error in errors))

    def test_d08_recommendation_matches_human_pack(self) -> None:
        decision = next(d for d in self.register['decisions'] if d['id'] == 'PCT-P0-D08')
        self.assertEqual(decision['agent_recommendation'], 'B')

    def test_p0_is_not_protocol_freeze(self) -> None:
        text = (Path(__file__).resolve().parents[1] / 'docs' / 'p0' / 'p0-exit-gate.md').read_text(encoding='utf-8')
        self.assertIn('does not authorize confirmatory claims', text)

    def test_agents_file_preserves_project_independence(self) -> None:
        text = (Path(__file__).resolve().parents[1] / 'AGENTS.md').read_text(encoding='utf-8')
        self.assertIn('not a GoalEvo subproject', text)


if __name__ == '__main__':
    unittest.main()
