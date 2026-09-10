from __future__ import annotations
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts import run_p2_d21_local as local


class D21LocalTests(unittest.TestCase):
    def test_repository_validator_excludes_runtime_but_checks_research(self):
        from scripts import validate_p0
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / '.pct-local').mkdir()
            (root / '.pct-local' / 'vendor.json').write_text('not JSON')
            (root / 'research.json').write_text('not JSON')
            with patch.object(validate_p0, 'ROOT', root):
                errors = validate_p0.validate_json_files()
            self.assertEqual(len(errors), 1)
            self.assertTrue(errors[0].startswith('research.json:'))

    def test_local_amendment_and_freeze(self):
        self.assertEqual(local.validate(), [])

    def test_cloud_must_be_cancelled_and_generation_disabled(self):
        local.require_cloud_stopped({'status': 'completed', 'conclusion': 'cancelled'},
                                    {'state': 'disabled_manually'})
        for status, conclusion, state in [('waiting', None, 'disabled_manually'),
                ('completed', 'success', 'disabled_manually'), ('completed', 'cancelled', 'active')]:
            with self.subTest(status=status, state=state), self.assertRaises(ValueError):
                local.require_cloud_stopped({'status': status, 'conclusion': conclusion}, {'state': state})

    def test_missing_key_in_noninteractive_run_does_not_prompt(self):
        with patch.dict(local.os.environ, {'DEEPSEEK_API_KEY': ''}), \
             patch.object(local.sys.stdin, 'isatty', return_value=False), \
             patch.object(local.getpass, 'getpass') as prompt:
            with self.assertRaises(ValueError):
                local.read_key(None)
            prompt.assert_not_called()

    def test_credential_file_permissions_and_no_repo_secret(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'key'
            path.write_text('dummy-not-a-real-key')
            path.chmod(0o644)
            with self.assertRaises(ValueError):
                local.read_key(path)
            path.chmod(0o600)
            self.assertEqual(local.read_key(path), 'dummy-not-a-real-key')
        with self.assertRaises(ValueError):
            local.read_key(local.ROOT / '.env')

    def test_existing_local_consumption_cannot_reserve_remote_again(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            (directory / 'pct-d21-local-attempt.json').write_text('{}')
            with patch.object(local.subprocess, 'check_output', return_value=temp), \
                 patch.object(local, 'gh_json') as remote:
                with self.assertRaises(FileExistsError):
                    local.reserve_once('test-sha', directory)
                remote.assert_not_called()

    def test_local_binding_records_true_credential_source(self):
        payload = json.dumps({'object': 'list', 'data': [{'id': 'deepseek-v4-pro', 'object': 'model', 'owned_by': 'deepseek'}]}).encode()
        with tempfile.TemporaryDirectory() as temp, \
             patch.object(local.D21, 'urlopen', return_value=io.BytesIO(payload)):
            local.local_binding('dummy-not-a-real-key', Path(temp))
            value = json.loads((Path(temp) / 'deepseek-provider-local-binding-v0.4.json').read_text())
            self.assertEqual(value['credential_handling']['credential_source'], 'LOCAL_PARENT_PROCESS_MEMORY')
            self.assertNotIn('dummy-not-a-real-key', json.dumps(value))

    def test_failure_keeps_attempt_and_stops(self):
        with tempfile.TemporaryDirectory() as temp, \
             patch.object(local, 'local_binding', return_value={'status': 'PASS'}), \
             patch.object(local.D21, 'run_fixture', side_effect=RuntimeError('simulated')) as fixture:
            self.assertEqual(local.execute(Path(temp), Path(temp), 'test-sha', 'dummy'), 1)
            value = json.loads((Path(temp) / local.D21.REPORT_NAME).read_text())
            self.assertEqual(len(value['runs']), 1)
            fixture.assert_called_once()
            self.assertEqual(value['status'], 'ERROR_PRESERVED')
            self.assertEqual(value['research_boundaries']['primary_schedule_runs'], 0)


if __name__ == '__main__':
    unittest.main()
