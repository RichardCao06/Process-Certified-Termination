from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts/p2_replay_shadow.py"
FIXTURE = ROOT / "data/p2/fixtures/replay-clean-success-v0.1.json"


class P2FoundationCliTests(unittest.TestCase):
    def test_replay_and_verify_cli(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "bundle.json"
            completed = subprocess.run(
                [sys.executable, str(CLI), str(FIXTURE), "--output", str(output)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            bundle = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual("PCT_P2_SHADOW_REPLAY_BUNDLE", bundle["record_type"])

            verified = subprocess.run(
                [sys.executable, str(CLI), str(output), "--verify"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, verified.returncode, verified.stderr)
            self.assertIn("verification passed", verified.stdout)


if __name__ == "__main__":
    unittest.main()
