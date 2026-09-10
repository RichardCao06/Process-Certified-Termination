#!/usr/bin/env python3
"""PCT-P2-001 / D21-A01: local execution of the same unconsumed D21 attempt."""
from __future__ import annotations

import argparse
import contextlib
import getpass
import hashlib
import json
import os
import platform
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import run_p2_d21_smoke as D21
from scripts import validate_p2_d21_execution as LEGACY

REPO = 'RichardCao06/Process-Certified-Termination'
REMOTE_RUN = 34433128526
TAG = 'pct-p2-d21-authorization-consumed'
AMENDMENT = 'governance/p2-d21-local-execution-amendment-v0.1.json'
FREEZE = 'governance/p2-d21-local-implementation-freeze-v0.1.json'


def validate(root=ROOT):
    errors = LEGACY.validate(root)
    try:
        amendment = json.loads((root / AMENDMENT).read_text())
        freeze = json.loads((root / FREEZE).read_text())
        for value, field in [(amendment, 'amendment_digest'), (freeze, 'freeze_digest')]:
            if value.get(field) != LEGACY.digest(value, field):
                errors.append('Local D21 record digest mismatch')
        if amendment.get('execution_backend') != 'LOCAL_MACOS' or amendment.get('new_attempt_authorized') is not False:
            errors.append('D21 amendment changes attempt authority')
        if amendment.get('fixture_ids') != D21.FIXTURE_IDS:
            errors.append('Local D21 fixture scope mismatch')
        if amendment.get('github_environment_review_required') is not False:
            errors.append('Local amendment did not replace the GitHub review step')
        for field in ('semantic_auditor_authorized', 'reference_opening_authorized', 'online_intervention_authorized'):
            if amendment.get(field) is not False:
                errors.append(f'{field}: local scope expanded')
        if amendment.get('primary_schedule_runs_authorized') != 0:
            errors.append('Local D21 entered the primary schedule')
        bindings = freeze.get('file_sha256', {})
        required = {'scripts/run_p2_d21_local.py', 'tests/test_p2_d21_local.py',
                    '.github/workflows/p2-d21-local-validation.yml', AMENDMENT,
                    'governance/p2-d21-implementation-freeze-v0.1.json', 'scripts/run-p2-local.sh'}
        if not required <= set(bindings):
            errors.append('Local D21 implementation is not fully frozen')
        for relative, expected in bindings.items():
            if not (root / relative).is_file() or hashlib.sha256((root / relative).read_bytes()).hexdigest() != expected:
                errors.append(f'{relative}: local D21 frozen input changed')
    except (OSError, ValueError):
        errors.append('Missing local D21 amendment or implementation freeze')
    return errors


def gh_json(*args):
    result = subprocess.run(['gh', 'api', *args], capture_output=True, text=True)
    if result.returncode:
        # Never echo API headers, credentials, or raw service responses.
        raise RuntimeError('GitHub coordination failed; no model call permitted')
    return json.loads(result.stdout)


def require_cloud_stopped(run, workflow):
    if run.get('status') != 'completed' or run.get('conclusion') != 'cancelled':
        raise ValueError('The original cloud run must be confirmed cancelled')
    if workflow.get('state') != 'disabled_manually':
        raise ValueError('The cloud generation workflow must be disabled')


def verify_remote_commit(head):
    if subprocess.run(['git', 'diff', '--quiet', 'HEAD'], cwd=ROOT).returncode:
        raise ValueError('Commit local tracked changes before model execution')
    run = gh_json(f'repos/{REPO}/actions/runs/{REMOTE_RUN}')
    workflow = gh_json(f'repos/{REPO}/actions/workflows/p2-d21-smoke.yml')
    require_cloud_stopped(run, workflow)
    remote = gh_json(f'repos/{REPO}/commits/{head}')
    if remote.get('sha') != head:
        raise ValueError('Local execution commit is not published')
    checks = gh_json(f'repos/{REPO}/commits/{head}/check-runs?per_page=100')
    if not any(check.get('name') == 'validate' and check.get('conclusion') == 'success'
               for check in checks.get('check_runs', [])):
        raise ValueError('Successful repository CI for this commit is required')


def reserve_once(head, output):
    # Same tag as the old cloud route: two backends cannot consume two attempts.
    git_dir = Path(subprocess.check_output(['git', 'rev-parse', '--absolute-git-dir'], cwd=ROOT, text=True).strip())
    D21.write_once(git_dir / 'pct-d21-local-attempt.json', {'commit': head, 'started_at': D21.BASE.now()})
    reservation = gh_json('--method', 'POST', f'repos/{REPO}/git/refs',
                          '-f', f'ref=refs/tags/{TAG}', '-f', f'sha={head}')
    if reservation.get('object', {}).get('sha') != head:
        raise ValueError('Authorization reservation mismatch')
    D21.write_once(output / 'd21-local-reservation-v0.1.json', {
        'ref': reservation['ref'], 'source_commit': head, 'backend': 'LOCAL_MACOS'})


def seatbelt_profile(dsh, runtime, patch):
    # Only public runtime files and the current fixture are readable. The proxy
    # endpoint is the only allowed outgoing network destination.
    roots = ['/System', '/usr/lib', '/usr/share', '/private/etc', '/dev',
             '/Library/Apple', str(dsh.resolve()), str(runtime.resolve())]
    grants = ' '.join(f'(subpath {json.dumps(path)})' for path in roots)
    return '\n'.join([
        '(version 1)', '(allow default)',
        '(deny file-read* file-write* network*)',
        '(allow file-read-metadata)',
        # dyld reads the root directory while locating the executable. This is
        # a literal directory grant, not recursive access to its children.
        f'(allow file-read* (literal "/") {grants} (literal {json.dumps(str(patch.resolve()))}) (subpath (param "WORKSPACE")))',
        '(allow file-write* (literal "/dev/null") (subpath (param "WORKSPACE")))',
        '(allow network-outbound (remote ip (param "PROXY")))',
    ])


@contextlib.contextmanager
def sandbox_node(dsh, node):
    if sys.platform != 'darwin' or not Path('/usr/bin/sandbox-exec').is_file():
        raise RuntimeError('D21 local backend requires working macOS Seatbelt')
    if subprocess.check_output([str(node), '--version'], text=True).strip() != 'v22.19.0':
        raise ValueError('Use the prepared Node 22.19.0 runtime')
    with tempfile.TemporaryDirectory(prefix='pct-d21-launcher-') as temp:
        directory = Path(temp)
        profile = directory / 'worker.sb'
        profile.write_text(seatbelt_profile(dsh, node.parent.parent, D21.PATCH))
        wrapper = directory / 'node'
        wrapper.write_text('#!/bin/sh\nset -eu\n'
                           'case "$DEEPSEEK_BASE_URL" in http://127.0.0.1:*) ;; *) exit 78 ;; esac\n'
                           'pct_port=${DEEPSEEK_BASE_URL##*:}\n'
                           'case "$pct_port" in *[!0-9]*|"") exit 78 ;; esac\n'
                           'mkdir -p "$PWD/.tmp"\nexport TMPDIR="$PWD/.tmp"\n'
                           'export TSX_DISABLE_CACHE=1\n'
                           'exec /usr/bin/sandbox-exec -D "WORKSPACE=$PWD" '
                           '-D "PROXY=localhost:$pct_port" -f ' + shlex.quote(str(profile)) + ' '
                           + shlex.quote(str(node)) + ' "$@"\n')
        wrapper.chmod(0o700)
        previous = os.environ.get('PATH', '')
        os.environ['PATH'] = str(directory) + os.pathsep + previous
        try:
            yield
        finally:
            os.environ['PATH'] = previous


def boundary_probe(dsh, node, output):
    import http.server
    import threading
    with tempfile.TemporaryDirectory(prefix='pct-d21-boundary-') as temp:
        root = Path(temp).resolve()
        workspace = root / 'workspace'
        workspace.mkdir()
        sentinel = root / 'outside.txt'
        sentinel.write_text('PUBLIC_D21_BOUNDARY_SENTINEL')
        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        probe = '''const fs = require('node:fs');
const http = require('node:http');
const net = require('node:net');
const outside = process.argv[1];
const expectedDenied = (fn) => { try { fn(); return false; } catch(e) { return ['EPERM','EACCES'].includes(e.code); } };
const readDenied = expectedDenied(() => fs.readFileSync(outside));
const writeDenied = expectedDenied(() => fs.writeFileSync(outside, 'changed'));
fs.writeFileSync('inside.txt', 'allowed');
const inside = fs.readFileSync('inside.txt','utf8') === 'allowed';
const allowedNetwork = new Promise(resolve => http.get(process.env.DEEPSEEK_BASE_URL, r => { r.resume(); resolve(r.statusCode === 200); }).on('error', () => resolve(false)));
const deniedNetwork = new Promise(resolve => { const s=net.connect({host:'127.0.0.1',port:1}); s.on('connect',()=>{s.destroy();resolve(false)}); s.on('error',e=>resolve(['EPERM','EACCES'].includes(e.code))); s.setTimeout(2000,()=>{s.destroy();resolve(false)}); });
Promise.all([allowedNetwork,deniedNetwork]).then(([proxyAllowed,otherPortDenied])=>{ const checks={readDenied,writeDenied,inside,proxyAllowed,otherPortDenied}; console.log(JSON.stringify(checks)); process.exitCode=Object.values(checks).every(Boolean)?0:1; });'''
        env = D21.BASE.sanitize_child_environment(dict(os.environ), 'dummy',
                 f'http://127.0.0.1:{server.server_port}', dsh / 'examples/headless-agent/cordis.yml', workspace / '.dsh')
        try:
            result = subprocess.run(['node', '-e', probe, str(sentinel)], cwd=workspace,
                                    env=env, text=True, capture_output=True, timeout=20)
        finally:
            server.shutdown()
            server.server_close()
        try:
            checks = json.loads(result.stdout)
        except ValueError:
            checks = {}
        passed = result.returncode == 0 and checks and all(v is True for v in checks.values())
        report = {'work_order': 'PCT-P2-001', 'status': 'PASS' if passed else 'FAIL',
                  'checks': checks, 'exit_code': result.returncode, 'model_calls': 0, 'private_files_read': False,
                  'stderr_sha256': D21.BASE.sha_text(result.stderr)}
        D21.write_once(output / 'd21-local-boundary-probe-v0.1.json', report)
        if not passed:
            raise RuntimeError('Local Worker confinement check failed')


def read_key(path):
    if path:
        path = path.expanduser().resolve()
        if path.is_relative_to(ROOT):
            raise ValueError('Keep the API key file outside the repository')
        if path.stat().st_mode & 0o077:
            raise ValueError('Credential file must be private: chmod 600')
        key = path.read_text().strip()
    else:
        key = os.environ.pop('DEEPSEEK_API_KEY', '')
        if not key:
            if not sys.stdin.isatty():
                raise ValueError('No local credential: use a private key file or enter it in a terminal')
            key = getpass.getpass('DeepSeek API key (hidden; not saved): ').strip()
    if not key or '\n' in key:
        raise ValueError('Expected one non-empty API key')
    return key


def local_binding(key, output):
    request = D21.Request('https://api.deepseek.com/models', headers={
        'Authorization': f'Bearer {key}', 'Accept': 'application/json',
        'User-Agent': 'PCT-P2-D21-local-binding/0.1'})
    with D21.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read())
    report = D21.BASE.build_binding_report(payload, D21.BASE.current_binding_material(), D21.BASE.now())
    report.update(report_id='PCT-P2-D21-LOCAL-PROVIDER-BINDING-v0.4',
                  decision='PCT-P2-D21:A', amendment='PCT-P2-D21-A01',
                  execution_backend='LOCAL_MACOS',
                  actual_runtime_patch_sha256=D21.BASE.sha_file(D21.PATCH),
                  implementation_manifest_sha256=D21.BASE.sha_file(ROOT / FREEZE))
    report['credential_handling'] = {
        'credential_source': 'LOCAL_PARENT_PROCESS_MEMORY', 'secret_value_recorded': False,
        'secret_hash_recorded': False, 'authorization_header_recorded': False,
        'secret_available_to_worker_process': False}
    report['report_digest'] = D21.BASE.canonical_digest(report, 'report_digest')
    D21.write_once(output / 'deepseek-provider-local-binding-v0.4.json', report)
    return {'status': report['status'], 'report_digest': report['report_digest']}


def execute(dsh, output, head, key):
    report = {'record_type': 'PCT_P2_D21_LOCAL_ENGINEERING_SMOKE', 'work_order': 'PCT-P2-001',
              'decision': 'PCT-P2-D21:A', 'amendment': 'PCT-P2-D21-A01',
              'source_head_sha': head, 'execution_backend': 'LOCAL_MACOS',
              'started_at': D21.BASE.now(), 'status': 'NOT_RUN', 'runs': [],
              'research_boundaries': {'maximum_trajectories': 2, 'primary_schedule_runs': 0,
                  'mode': 'SHADOW', 'applied_to_runtime': False, 'semantic_auditor_calls': 0,
                  'reference_packets_opened': 0, 'raw_model_or_tool_content_in_evidence': False}}
    try:
        binding = local_binding(key, output)
        report['profile_binding'] = binding
        if binding['status'] != 'PASS':
            raise ValueError('Frozen model unavailable; substitution prohibited')
        caps = json.loads((ROOT / 'governance/p2-operational-caps-v0.1.json').read_text())
        catalog = json.loads((ROOT / 'data/p2/engineering-smoke/fixture-catalog-v0.1.json').read_text())
        with tempfile.TemporaryDirectory(prefix='pct-d21-fixtures-') as temp:
            for fixture in catalog['fixtures']:
                item = {'fixture_id': fixture['fixture_id'], 'pass': False, 'status': 'ATTEMPT_STARTED'}
                report['runs'].append(item)
                try:
                    item.update(D21.run_fixture(dsh, fixture, Path(temp).resolve() / fixture['fixture_id'], caps, key))
                    item['status'] = 'PASS' if item['pass'] else 'FAIL'
                except BaseException as exc:
                    item.update(status='ERROR_PRESERVED', failure_class=type(exc).__name__, accounting_complete=False)
                    raise
                finally:
                    D21.write_once(output / f"{fixture['fixture_id']}-local-v0.4.json", item)
                if item['driver']['cap_violation'] or item['driver']['secret_output_detected']:
                    break
        report['status'] = 'PASS' if len(report['runs']) == 2 and all(r['pass'] for r in report['runs']) else 'FAIL'
    except BaseException as exc:
        report.update(status='ERROR_PRESERVED', failure_class=type(exc).__name__,
                      failure_message_sha256=D21.BASE.sha_text(str(exc)))
    finally:
        report['completed_at'] = D21.BASE.now()
        report['report_digest'] = D21.BASE.canonical_digest(report, 'report_digest')
        D21.write_once(output / D21.REPORT_NAME, report)
        print(json.dumps({'status': report['status'], 'fixture_attempts': len(report['runs']),
                          'evidence_directory': str(output)}))
    return 0 if report['status'] == 'PASS' else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dsh-source', type=Path, required=True)
    parser.add_argument('--node', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--credential-file', type=Path)
    parser.add_argument('--no-model', action='store_true')
    args = parser.parse_args()
    errors = validate()
    if errors:
        raise ValueError('; '.join(errors))
    dsh, node, output = args.dsh_source.resolve(), args.node.resolve(), args.output_dir.resolve()
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    D21.prepare_dsh(dsh)
    if subprocess.run(['git', 'diff', '--quiet', 'HEAD'], cwd=dsh).returncode:
        raise ValueError('Frozen DSH source has tracked modifications')
    with sandbox_node(dsh, node):
        boot_output = output / ('preflight-' + str(__import__('time').time_ns()))
        boundary_probe(dsh, node, boot_output)
        if D21.no_model_probe(dsh, boot_output) != 0:
            raise RuntimeError('Local D21 Harness boot failed')
        D21.write_once(boot_output / 'local-execution-context-v0.1.json', {
            'execution_backend': 'LOCAL_MACOS', 'source_head_sha': head,
            'platform': platform.platform(), 'node_version': '22.19.0', 'real_credentials_used': False})
        if args.no_model:
            print(json.dumps({'status': 'PASS', 'model_calls': 0, 'evidence_directory': str(boot_output)}))
            return 0
        if (output / D21.REPORT_NAME).exists():
            raise FileExistsError('Existing D21 result cannot be replaced')
        verify_remote_commit(head)
        key = read_key(args.credential_file)
        reserve_once(head, output)
        return execute(dsh, output, head, key)


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError, FileExistsError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
