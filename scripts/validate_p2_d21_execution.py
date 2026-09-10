#!/usr/bin/env python3
"""Validate D21-A execution inputs without granting any primary-pilot authority."""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_IDS = ['PCT-P2-SMOKE-ENG-001', 'PCT-P2-SMOKE-ENG-002']


def digest(value, field):
    body = {k: v for k, v in value.items() if k != field}
    return hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def validate(root=ROOT):
    errors = []
    records = {
        'p2-human-approval-d21-v0.1.json': 'approval_digest',
        'p2-d21-implementation-freeze-v0.1.json': 'freeze_digest',
        'p2-status-v0.8.json': 'status_digest',
        'p2-decision-register-v0.7.json': 'register_digest',
    }
    values = {}
    for name, field in records.items():
        try:
            value = json.loads((root / 'governance' / name).read_text())
            values[name] = value
            if value.get(field) != digest(value, field):
                errors.append(f'{name}: digest mismatch')
        except (OSError, ValueError):
            errors.append(f'{name}: missing or invalid')
    if errors:
        return errors
    approval = values['p2-human-approval-d21-v0.1.json']
    if approval.get('approved_options') != {'PCT-P2-D21': 'A'}:
        errors.append('D21-A explicit approval missing')
    scope = approval.get('execution_scope', {})
    if scope.get('fixture_ids') != FIXTURE_IDS or scope.get('attempts_per_fixture') != 1:
        errors.append('D21 fixture scope changed')
    if scope.get('per_trajectory_cny_cap') != 30 or scope.get('aggregate_cny_cap') != 60:
        errors.append('D21 monetary scope changed')
    if approval.get('approval_source', {}).get('verbatim_user_message') != '批准':
        errors.append('D21 approval source missing')
    freeze = values['p2-d21-implementation-freeze-v0.1.json']
    for relative, expected in freeze.get('file_sha256', {}).items():
        path = root / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            errors.append(f'{relative}: frozen input changed')
    required = {'scripts/run_p2_d21_smoke.py', 'scripts/p2/d21-driver.mts',
                'config/p2/dsh-engineering-smoke.patch-v0.2.yml',
                'data/p2/engineering-smoke/fixture-catalog-v0.1.json',
                'governance/p2-operational-caps-v0.1.json',
                '.github/workflows/p2-d21-smoke.yml',
                'scripts/validate_p2_d21_execution.py',
                'scripts/run_p2_engineering_smoke.py',
                'scripts/run_p2_engineering_smoke_remediation.py',
                'governance/p2-human-approval-d21-v0.1.json',
                'governance/p2-worker-profile-freeze-v0.2.json',
                'config/p2/deepseek-v4-pro-operational-profile-v0.2.json',
                'config/p2/natural-pilot-system-prompt-v0.1.txt',
                'config/p2/d19-runtime-tool-catalog-v0.1.json',
                'reports/p2/engineering-smoke-run-v0.2.json',
                'reports/p2/engineering-smoke-remediation-run-v0.3.json'}
    if not required <= set(freeze.get('file_sha256', {})):
        errors.append('D21 freeze lacks execution inputs')
    catalog = json.loads((root / 'data/p2/engineering-smoke/fixture-catalog-v0.1.json').read_text())
    if [item['fixture_id'] for item in catalog['fixtures']] != FIXTURE_IDS:
        errors.append('D21 fixture count or order changed')
    status = values['p2-status-v0.8.json']
    register = values['p2-decision-register-v0.7.json']
    lineage = [f'PCT-P2-D{i:02d}' for i in range(1, 22)]
    if status.get('approved_decision_ids') != lineage or register.get('approved_decision_ids') != lineage:
        errors.append('D21 approval lineage mismatch')
    if status.get('active_decision_register') != 'governance/p2-decision-register-v0.7.json':
        errors.append('D21 active register mismatch')
    if register.get('pending_decisions') != [] or status.get('open_normative_gate_ids') != []:
        errors.append('D21 approval remains pending')
    if status.get('additional_engineering_worker_calls_authorized') is not True:
        errors.append('D21 engineering authorization missing')
    for field in ('natural_task_shadow_measurement_authorized', 'live_primary_worker_model_calls_authorized',
                  'semantic_audit_agent_authorized', 'reference_evaluator_opening_authorized',
                  'online_intervention_authorized', 'worker_behavior_change_authorized', 'effectiveness_claim_allowed'):
        if status.get(field) is not False:
            errors.append(f'{field}: scope expanded')
    if status.get('primary_schedule_runs_completed') != 0:
        errors.append('D21 entered primary schedule')
    return errors


if __name__ == '__main__':
    errors = validate()
    if errors:
        print('\n'.join(errors), file=sys.stderr)
    else:
        print('D21 execution inputs PASS: one protected two-fixture attempt; primary pilot remains closed.')
    raise SystemExit(bool(errors))
