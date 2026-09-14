"""D21 operational gates: no provider calls or live credentials in tests."""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from scripts import run_p2_d21_smoke as runner
from scripts import validate_p2_d21_execution as preflight


class D21ExecutionTests(unittest.TestCase):
    def test_valid_frozen_authorization(self):
        self.assertEqual(preflight.validate(), [])

    def test_unreviewed_rerun_or_different_commit_is_rejected(self):
        env = {'GITHUB_ACTIONS': 'true', 'GITHUB_RUN_ATTEMPT': '1',
               'GITHUB_SHA': 'abc', 'PCT_D21_RESERVATION_SHA': 'abc',
               'PCT_D21_ENVIRONMENT_REVIEWED': 'true'}
        runner.require_execution_context(env)
        for field in env:
            with self.subTest(missing=field), self.assertRaises(ValueError):
                runner.require_execution_context({k: v for k, v in env.items() if k != field})
        for field, value in [('GITHUB_RUN_ATTEMPT', '2'),
                             ('PCT_D21_RESERVATION_SHA', 'other'),
                             ('PCT_D21_ENVIRONMENT_REVIEWED', 'false')]:
            with self.subTest(changed=field), self.assertRaises(ValueError):
                runner.require_execution_context(dict(env, **{field: value}))

    def test_evidence_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'report.json'
            runner.write_once(path, {'status': 'FAIL'})
            before = path.read_bytes()
            with self.assertRaises(FileExistsError):
                runner.write_once(path, {'status': 'PASS'})
            self.assertEqual(path.read_bytes(), before)

    def test_changed_frozen_fixture_is_rejected(self):
        original = Path.read_bytes
        def changed(path):
            data = original(path)
            return data + b' ' if path.name == 'fixture-catalog-v0.1.json' else data
        with patch.object(Path, 'read_bytes', changed):
            self.assertTrue(any('fixture-catalog' in error for error in preflight.validate()))

    def test_usage_failure_blocks_next_upstream_request(self):
        caps = json.loads((runner.ROOT / 'governance/p2-operational-caps-v0.1.json').read_text())
        state = runner.BASE.ProxyState(caps=caps, upstream_api_key='dummy',
                                      expected_tool_names=['edit', 'read', 'write'])
        state.violations.append('MISSING_USAGE')
        with runner.D21Proxy(state) as proxy, patch.object(runner.BASE, 'urlopen') as upstream:
            request = Request(proxy.url + '/chat/completions', data=b'{}',
                              headers={'Authorization': 'Bearer ' + state.local_proxy_token})
            with self.assertRaises(HTTPError) as raised:
                urlopen(request, timeout=5)
            self.assertEqual(raised.exception.code, 409)
            upstream.assert_not_called()
        self.assertEqual(state.upstream_attempts, 0)

    def test_primary_authority_cannot_be_added_even_with_valid_digest(self):
        original = Path.read_text
        def changed(path, *args, **kwargs):
            text = original(path, *args, **kwargs)
            if path.name == 'p2-status-v0.8.json':
                value = json.loads(text)
                value['live_primary_worker_model_calls_authorized'] = True
                value['status_digest'] = preflight.digest(value, 'status_digest')
                return json.dumps(value)
            return text
        with patch.object(Path, 'read_text', changed):
            self.assertIn('live_primary_worker_model_calls_authorized: scope expanded', preflight.validate())

    def test_unexpected_fixture_failure_preserves_attempt_denominator(self):
        env = {'GITHUB_ACTIONS': 'true', 'GITHUB_RUN_ATTEMPT': '1',
               'GITHUB_SHA': 'test-sha', 'PCT_D21_RESERVATION_SHA': 'test-sha',
               'PCT_D21_ENVIRONMENT_REVIEWED': 'true', 'DEEPSEEK_API_KEY': 'dummy'}
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'evidence'
            with patch.dict(runner.os.environ, env), \
                 patch.object(runner.sys, 'argv', ['runner', '--dsh-source', temp, '--output-dir', str(output)]), \
                 patch.object(runner, 'prepare_dsh'), \
                 patch.object(runner, 'fresh_binding', return_value={'status': 'PASS'}), \
                 patch.object(runner, 'run_fixture', side_effect=RuntimeError('simulated failure')):
                self.assertEqual(runner.main(), 1)
            report = json.loads((output / runner.REPORT_NAME).read_text())
            self.assertEqual(report['status'], 'ERROR_PRESERVED')
            self.assertEqual(len(report['runs']), 1)
            self.assertEqual(report['runs'][0]['fixture_id'], runner.FIXTURE_IDS[0])
            self.assertFalse(report['runs'][0]['pass'])
            self.assertTrue((output / f'{runner.FIXTURE_IDS[0]}-v0.4.json').exists())


if __name__ == '__main__':
    unittest.main()
