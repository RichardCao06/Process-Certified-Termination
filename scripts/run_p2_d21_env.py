#!/usr/bin/env python3
"""PCT-P2-001: load a private env file into the unchanged local D21 runner."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = Path.home() / '.config/pct/deepseek.env'


def read_config(path):
    path = path.expanduser().resolve()
    if path.is_relative_to(ROOT) or path.stat().st_mode & 0o077:
        raise ValueError('Configuration must be outside the repository with permissions 600')
    values = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        name, sep, value = line.partition('=')
        name, value = name.strip(), value.strip()
        if not sep or name != 'DEEPSEEK_API_KEY' or name in values:
            raise ValueError('Expected exactly one DEEPSEEK_API_KEY assignment')
        if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
            value = value[1:-1]
        if not value or any(c.isspace() or c in '$`\\\"\'' for c in value):
            raise ValueError('Fill DEEPSEEK_API_KEY with a non-empty literal key')
        values[name] = value
    if set(values) != {'DEEPSEEK_API_KEY'}:
        raise ValueError('DEEPSEEK_API_KEY is missing')
    return values


def main():
    args = sys.argv[1:]
    if any(arg == '--credential-file' or arg.startswith('--credential-file=') for arg in args):
        raise ValueError('This entry reads the configured env file; do not mix credential sources')
    env = dict(os.environ)
    if '--no-model' not in args and '--help' not in args and '-h' not in args:
        env.update(read_config(DEFAULT_CONFIG))
    else:
        env.pop('DEEPSEEK_API_KEY', None)
    command = [sys.executable, str(ROOT / 'scripts/run_p2_d21_local.py'),
               '--dsh-source', str(ROOT / '.pct-local/deepseek-harness'),
               '--node', str(ROOT / '.pct-local/runtime/node_modules/node/bin/node'),
               '--output-dir', str(ROOT / '.pct-local/results/d21'), *args]
    os.execve(sys.executable, command, env)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError):
        print('Local env configuration is missing or invalid. Check ~/.config/pct/deepseek.env and permissions 600; values are not logged.', file=sys.stderr)
        raise SystemExit(2)
