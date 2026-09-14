import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts import run_p2_d21_env as adapter


class EnvConfigTests(unittest.TestCase):
    def test_plain_and_quoted_private_assignments(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / 'deepseek.env'
            for value in ['dummy-value', '"dummy-value"', "'dummy-value'"]:
                p.write_text('# comment\nDEEPSEEK_API_KEY=' + value + '\n')
                p.chmod(0o600)
                self.assertEqual(adapter.read_config(p), {'DEEPSEEK_API_KEY': 'dummy-value'})

    def test_rejects_empty_duplicate_other_settings_and_shell_syntax(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / 'deepseek.env'
            for content in ['', 'DEEPSEEK_API_KEY=', 'MODEL=other',
                            'DEEPSEEK_API_KEY=a\nDEEPSEEK_API_KEY=b',
                            'DEEPSEEK_API_KEY=$(echo secret)', 'DEEPSEEK_API_KEY=`echo secret`']:
                p.write_text(content)
                p.chmod(0o600)
                with self.subTest(content=content), self.assertRaises(ValueError):
                    adapter.read_config(p)

    def test_no_model_does_not_read_or_pass_key(self):
        with patch.object(adapter.sys, 'argv', ['adapter', '--no-model']), \
             patch.dict(adapter.os.environ, {'DEEPSEEK_API_KEY': 'dummy'}), \
             patch.object(adapter, 'read_config') as read, \
             patch.object(adapter.os, 'execve') as execute:
            adapter.main()
            read.assert_not_called()
            self.assertNotIn('DEEPSEEK_API_KEY', execute.call_args.args[2])
