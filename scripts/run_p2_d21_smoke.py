#!/usr/bin/env python3
"""PCT-P2-001: one approved D21 attempt, new outputs only, no primary pilot."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import queue
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from types import SimpleNamespace
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DSH_COMMIT = 'b150a551b8d465e31e418e1b2eaf5e79bbb7d28e'
FIXTURE_IDS = ['PCT-P2-SMOKE-ENG-001', 'PCT-P2-SMOKE-ENG-002']
PATCH = ROOT / 'config/p2/dsh-engineering-smoke.patch-v0.2.yml'
REPORT_NAME = 'engineering-smoke-official-patch-run-v0.4.json'


def load_script(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_script('pct_d21_d19_helpers', ROOT / 'scripts/run_p2_engineering_smoke.py')
D20 = load_script('pct_d21_d20_helpers', ROOT / 'scripts/run_p2_engineering_smoke_remediation.py')
build_source_mode_child_environment = D20.build_source_mode_child_environment
classify_stderr = D20.classify_stderr


def write_once(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write('\n')


def require_execution_context(env):
    if env.get('GITHUB_ACTIONS') != 'true' or env.get('GITHUB_RUN_ATTEMPT') != '1':
        raise ValueError('D21 permits only a first GitHub Actions attempt')
    if env.get('PCT_D21_RESERVATION_SHA') != env.get('GITHUB_SHA') or not env.get('GITHUB_SHA'):
        raise ValueError('D21 requires the atomic authorization reservation for this commit')
    if env.get('PCT_D21_ENVIRONMENT_REVIEWED') != 'true':
        raise ValueError('D21 requires the protected Environment job')


def prepare_dsh(dsh):
    actual = subprocess.check_output(['git', '-C', str(dsh), 'rev-parse', 'HEAD'], text=True).strip()
    if actual != DSH_COMMIT:
        raise ValueError('Frozen DSH commit mismatch')
    shutil.copyfile(ROOT / 'scripts/p2/d21-driver.mts', dsh / '.pct-d21-driver.mts')


class D21Proxy(BASE.GuardedProxy):
    """Preserve frozen transport behavior; stop after an accounting failure."""
    def __init__(self, state):
        super().__init__(state)
        handler = self.server.RequestHandlerClass
        original = handler.do_POST
        request_lock = threading.Lock()

        def guarded_post(connection):
            # One completed usage update must precede the next request.
            with request_lock:
                if state.violations:
                    connection.send_error(409)
                    return
                try:
                    original(connection)
                except Exception:
                    # No partial-response retry and no raw server traceback.
                    state.violations.append('UPSTREAM_STREAM_OR_ACCOUNTING_FAILURE')
                    connection.close_connection = True

        handler.do_POST = guarded_post


def fresh_binding(api_key, output):
    # Historical profile hashes stay unchanged. D21 additionally binds the actual
    # official patch and the new driver through the implementation manifest.
    bindings = BASE.current_binding_material()
    request = Request('https://api.deepseek.com/models', method='GET', headers={
        'Authorization': f'Bearer {api_key}', 'Accept': 'application/json',
        'User-Agent': 'PCT-P2-D21-fresh-binding/0.1',
    })
    with urlopen(request, timeout=30) as response:
        payload = json.loads(response.read())
    report = BASE.build_binding_report(payload, bindings, BASE.now())
    report.update(report_id='PCT-P2-D21-PROVIDER-BINDING-v0.4', decision='PCT-P2-D21:A',
                  actual_runtime_patch_sha256=BASE.sha_file(PATCH),
                  implementation_manifest_sha256=BASE.sha_file(ROOT / 'governance/p2-d21-implementation-freeze-v0.1.json'))
    report['report_digest'] = BASE.canonical_digest(report, 'report_digest')
    write_once(output / 'deepseek-provider-introspection-v0.4.json', report)
    return {'status': report['status'], 'report_digest': report['report_digest'],
            'returned_model_identifier': report['response']['returned_model_identifier']}


def run_driver(base, dsh, config, workspace, task, proxy, limits, real_api_key, mode="fixture"):
    loader = dsh / 'node_modules/tsx/dist/esm/index.mjs'
    driver = dsh / '.pct-d21-driver.mts'
    tsconfig = dsh / 'tsconfig.json'
    if not loader.is_file() or not driver.is_file() or (not tsconfig.is_file()):
        raise FileNotFoundError('DSH source-mode loader, driver, or tsconfig missing')
    child_env = build_source_mode_child_environment(base, dict(os.environ), proxy.state.local_proxy_token, proxy.url, dsh, workspace)
    if real_api_key and real_api_key in child_env.values():
        raise RuntimeError('real DeepSeek key reached Worker subprocess environment')
    process = subprocess.Popen(['node', '--import', loader.as_uri(), str(driver), str(dsh / 'examples/headless-agent/cordis.yml'), str(config), mode, task], cwd=workspace, env=child_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    q = queue.Queue()

    def pump(name, stream):
        for line in iter(stream.readline, ''):
            q.put((name, line))
        q.put((name, None))
    threading.Thread(target=pump, args=('stdout', process.stdout), daemon=True).start()
    threading.Thread(target=pump, args=('stderr', process.stderr), daemon=True).start()
    events = []
    boot_checks_pass = False
    stderr = []
    other = []
    done = set()
    started = time.monotonic()
    cap = None
    secret = False
    while len(done) < 2 or process.poll() is None:
        if getattr(proxy.state, 'violations', []):
            cap = 'PROXY_FAIL_CLOSED'
            process.kill()
            break
        if time.monotonic() - started > limits['wall_clock_seconds']:
            cap = 'WALL_CLOCK_CAP'
            process.kill()
            break
        try:
            name, line = q.get(timeout=0.2)
        except queue.Empty:
            continue
        if line is None:
            done.add(name)
            continue
        if real_api_key and real_api_key in line:
            secret = True
            cap = 'REAL_SECRET_OUTPUT'
            process.kill()
            continue
        if base.FORBIDDEN_SECRET_PATTERN.search(line):
            secret = True
            cap = 'SECRET_LIKE_OUTPUT'
            process.kill()
            continue
        if name == 'stderr':
            stderr.append(line[-1000:])
            continue
        try:
            item = json.loads(line)
        except Exception:
            other.append(line[-1000:])
            continue
        if item.get('type') == 'd21_boot':
            boot_checks_pass = bool(item.get('checks')) and all(v is True for v in item['checks'].values())
        elif item.get('type') == 'session_event':
            events.append(item)
            tools = sum((1 for e in events if (e.get('event') or {}).get('type') == 'tool/call'))
            stops = sum((1 for e in events if (e.get('event') or {}).get('type') == 'agent/turn-stopping'))
            if tools > limits['tool_calls']:
                cap = 'TOOL_CALL_CAP'
                process.kill()
            if stops > limits['candidate_stops']:
                cap = 'CANDIDATE_STOP_CAP'
                process.kill()
        else:
            other.append(json.dumps(item, sort_keys=True)[-2000:])
    try:
        exit_code = process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
        exit_code = process.wait()
    process.stdout.close()
    process.stderr.close()
    stderr_text = ''.join(stderr)
    types = [(e.get('event') or {}).get('type') for e in events]
    return {'boot_checks_pass': boot_checks_pass, 'exit_code': exit_code, 'elapsed_seconds': round(time.monotonic() - started, 3), 'events': events, 'event_type_counts': {n: types.count(n) for n in sorted(set(types)) if n}, 'request_header_tool_sets': base.extract_request_header_tool_sets(events), 'stderr_tail_hash': base.sha_text(stderr_text), 'stderr_classification': classify_stderr(stderr_text), 'other_output_hash': base.sha_text(''.join(other)), 'cap_violation': cap, 'secret_output_detected': secret, 'source_mode_bindings': {'tsx_tsconfig_path_set': child_env.get('TSX_TSCONFIG_PATH') == str(tsconfig), 'dsh_agents_home_isolated': child_env.get('DSH_AGENTS_HOME') == str(workspace / '.agents')}}


def no_model_probe(dsh, output):
    caps = json.loads((ROOT / 'governance/p2-operational-caps-v0.1.json').read_text())
    limits = dict(caps['per_trajectory_caps'], wall_clock_seconds=90)
    proxy = SimpleNamespace(state=SimpleNamespace(local_proxy_token='PCT_D21_DUMMY'), url='http://127.0.0.1:9')
    with tempfile.TemporaryDirectory(prefix='pct-d21-boot-') as temp:
        result = run_driver(BASE, dsh, PATCH, Path(temp), '', proxy, limits, '', mode='no-model')
    events = result.pop('events')
    passed = result['exit_code'] == 0 and not events and result['boot_checks_pass']
    report = {'work_order': 'PCT-P2-001', 'status': 'PASS' if passed else 'FAIL',
              'source_head_sha': os.environ.get('GITHUB_SHA'), 'driver': result,
              'model_turns': 0, 'real_credentials_used': False, 'provider_endpoint': 'http://127.0.0.1:9',
              'driver_sha256': BASE.sha_file(ROOT / 'scripts/p2/d21-driver.mts')}
    write_once(output / 'd21-driver-no-model-validation-v0.1.json', report)
    return 0 if passed else 1


def run_fixture(dsh, fixture, workspace, caps, real_key):
    workspace.mkdir()
    for relative, content in fixture['initial_files'].items():
        target = workspace / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8')
    limits = caps['per_trajectory_caps']
    expected = ['edit', 'read', 'write']
    state = BASE.ProxyState(caps=caps, upstream_api_key=real_key, expected_tool_names=expected)
    with D21Proxy(state) as proxy:
        driver = run_driver(BASE, dsh, PATCH, workspace, fixture['task'], proxy, limits, real_key)
    events = driver.pop('events')
    artifact_pass, detail = BASE.validate_artifact(workspace, fixture['validator'])
    sidecar = BASE.bind_sidecar(fixture, events, workspace)
    headers = driver['request_header_tool_sets']
    header_exact = bool(headers) and all(item == expected for item in headers)
    cost = BASE.estimate_cost(state.usage, caps)
    passed = (driver['exit_code'] == 0 and driver['boot_checks_pass']
              and driver['cap_violation'] is None and not driver['secret_output_detected']
              and not state.violations and state.logical_requests >= 1 and artifact_pass
              and sidecar['status'] == 'BOUND_EXACT' and header_exact
              and BASE.token_total(state.usage) <= limits['cumulative_tokens']
              and cost['cny_policy_guard'] <= limits['monetary_cap'])
    return {'fixture_id': fixture['fixture_id'], 'goal_id': fixture['goal_id'], 'pass': passed,
            'excluded_from_primary_schedule': True, 'driver': driver,
            'proxy': {'logical_model_requests': state.logical_requests,
                      'upstream_attempts': state.upstream_attempts, 'usage': state.usage,
                      'cost_guard': cost, 'violations': sorted(set(state.violations)),
                      'request_records': state.records},
            'validator': {'pass': artifact_pass, 'detail': detail},
            'candidate_stop_binding': sidecar, 'runtime_tool_catalog_exact': header_exact,
            'workspace_digest': BASE.workspace_digest(workspace)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dsh-source', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--no-model', action='store_true')
    args = parser.parse_args()
    from scripts.validate_p2_d21_execution import validate
    errors = validate()
    if errors:
        raise RuntimeError('; '.join(errors))
    dsh, output = args.dsh_source.resolve(), args.output_dir.resolve()
    prepare_dsh(dsh)
    if args.no_model:
        return no_model_probe(dsh, output)
    require_execution_context(os.environ)
    if (output / REPORT_NAME).exists():
        raise FileExistsError('D21 evidence cannot be overwritten')
    report = {'schema_version': '0.4', 'record_type': 'PCT_P2_D21_ENGINEERING_SMOKE',
              'work_order': 'PCT-P2-001', 'decision': 'PCT-P2-D21:A',
              'started_at': BASE.now(), 'status': 'NOT_RUN', 'runs': [],
              'source_head_sha': os.environ['GITHUB_SHA'], 'github_run_id': os.environ.get('GITHUB_RUN_ID'),
              'github_run_attempt': 1, 'profile_binding': {'status': 'NOT_RUN'},
              'research_boundaries': {'maximum_trajectories': 2, 'primary_schedule_runs': 0,
                  'reference_packets_opened': 0, 'semantic_auditor_calls': 0,
                  'mode': 'SHADOW', 'applied_to_runtime': False, 'online_intervention': False,
                  'raw_model_or_tool_content_in_evidence': False}}
    real_key = os.environ.pop('DEEPSEEK_API_KEY', '')
    code = 1
    try:
        if not real_key:
            raise ValueError('MissingCredential')
        report['profile_binding'] = fresh_binding(real_key, output)
        if report['profile_binding']['status'] != 'PASS':
            raise ValueError('Exact model not available; substitution prohibited')
        catalog = json.loads((ROOT / 'data/p2/engineering-smoke/fixture-catalog-v0.1.json').read_text())
        caps = json.loads((ROOT / 'governance/p2-operational-caps-v0.1.json').read_text())
        with tempfile.TemporaryDirectory(prefix='pct-p2-d21-') as temp:
            for fixture in catalog['fixtures']:
                item = {'fixture_id': fixture['fixture_id'], 'pass': False,
                        'attempt_started_at': BASE.now(), 'status': 'ATTEMPT_STARTED'}
                report['runs'].append(item)
                try:
                    item.update(run_fixture(dsh, fixture, Path(temp) / fixture['fixture_id'], caps, real_key))
                    item['status'] = 'PASS' if item['pass'] else 'FAIL'
                except Exception as exc:
                    item.update(status='ERROR_PRESERVED', failure={
                        'class': type(exc).__name__, 'message_sha256': BASE.sha_text(str(exc)),
                        'accounting_complete': False})
                    raise
                finally:
                    write_once(output / f"{fixture['fixture_id']}-v0.4.json", item)
                if item['driver']['secret_output_detected'] or item['driver']['cap_violation']:
                    break
        report['status'] = 'PASS' if len(report['runs']) == 2 and all(r['pass'] for r in report['runs']) else 'FAIL'
        code = 0 if report['status'] == 'PASS' else 1
    except Exception as exc:
        report['status'] = 'ERROR_PRESERVED'
        report['failure'] = {'class': type(exc).__name__, 'message_sha256': BASE.sha_text(str(exc))}
    finally:
        report['completed_at'] = BASE.now()
        report['report_digest'] = BASE.canonical_digest(report, 'report_digest')
        write_once(output / REPORT_NAME, report)
        print(json.dumps({'status': report['status'], 'fixture_attempts': len(report['runs']),
                          'report_digest': report['report_digest']}))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
