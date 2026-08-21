#!/usr/bin/env python3
"""Deterministic integrity checks for the approved PCT P0 package."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    'README.md',
    'AGENTS.md',
    '.gitignore',
    'docs/p0/protocol-v0.1.md',
    'docs/p0/p0-closure-report.md',
    'docs/p0/decision-register.md',
    'docs/p0/threat-model.md',
    'docs/p0/role-and-authority-map.md',
    'docs/p0/causal-model.md',
    'docs/p0/claim-ladder.md',
    'docs/p0/literature-baseline.md',
    'docs/p0/p0-exit-gate.md',
    'docs/p0/contracts/goal-contract-v0.1.md',
    'docs/p0/contracts/autonomy-contract-v0.1.md',
    'docs/p0/contracts/assurance-contract-v0.1.md',
    'docs/p0/contracts/capability-envelope-v0.1.md',
    'docs/governance/human-agent-collaboration-protocol-v0.1.md',
    'docs/references/SOURCE-MANIFEST.md',
    'governance/decision-register.json',
    'governance/p0-status.json',
    'governance/role-assignments.json',
]
ALLOWED_STATUS = {'pending-human', 'approved', 'rejected', 'deferred'}
AGENT_ROLE_WORDS = ('Agent', 'Builder', 'Auditor', 'Red-Team', 'Experimental')


def load_json(path: Path) -> dict:
    with path.open(encoding='utf-8') as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f'{path}: expected a JSON object')
    return value


def validate_decision_register(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get('project_id') != 'PCT':
        errors.append('decision register project_id must be PCT')
    if data.get('phase') != 'P0':
        errors.append('decision register phase must be P0')
    decisions = data.get('decisions')
    if not isinstance(decisions, list) or not decisions:
        return errors + ['decision register requires a non-empty decisions array']
    ids = []
    for decision in decisions:
        if not isinstance(decision, dict):
            errors.append('each decision must be an object')
            continue
        did = decision.get('id')
        ids.append(did)
        if not isinstance(did, str) or not re.fullmatch(r'PCT-P0-D\d{2}', did):
            errors.append(f'invalid P0 decision id: {did!r}')
        if decision.get('status') not in ALLOWED_STATUS:
            errors.append(f'{did}: invalid status')
        options = decision.get('options')
        if not isinstance(options, list) or len(options) < 2:
            errors.append(f'{did}: at least two options are required')
            continue
        option_ids = {item.get('id') for item in options if isinstance(item, dict)}
        if decision.get('agent_recommendation') not in option_ids:
            errors.append(f'{did}: recommendation must reference a declared option')
        if decision.get('normative') is True:
            owner = decision.get('owner_role')
            if not isinstance(owner, str) or any(word in owner for word in AGENT_ROLE_WORDS):
                errors.append(f'{did}: normative decision must have a human owner role')
        if decision.get('status') in {'approved', 'rejected'}:
            if decision.get('human_decision') not in option_ids:
                errors.append(f'{did}: resolved human decision must reference a declared option')
            for field in ('rationale', 'approver_identity', 'effective_from'):
                if not decision.get(field):
                    errors.append(f'{did}: resolved decision missing {field}')
            rejected = decision.get('rejected_options_and_reasons')
            if not isinstance(rejected, list) or not rejected:
                errors.append(f'{did}: resolved decision must preserve rejected options and reasons')
    if len(ids) != len(set(ids)):
        errors.append('decision ids must be unique')
    expected = [f'PCT-P0-D{i:02d}' for i in range(1, len(decisions) + 1)]
    if ids != expected:
        errors.append(f'decision ids must be ordered and contiguous: expected {expected}, got {ids}')
    return errors


def validate_status(status: dict, register: dict) -> list[str]:
    errors: list[str] = []
    if status.get('project_id') != 'PCT' or status.get('phase') != 'P0':
        errors.append('P0 status must identify project PCT and phase P0')
    commit = status.get('candidate_harness', {}).get('commit')
    if not isinstance(commit, str) or not re.fullmatch(r'[0-9a-f]{40}', commit):
        errors.append('selected DeepSeek Harness commit must be a 40-character SHA')
    pending_blockers = [d['id'] for d in register['decisions'] if d.get('blocks_p0') and d.get('status') == 'pending-human']
    if status.get('blocking_decision_ids') != pending_blockers:
        errors.append('p0-status blocking_decision_ids must exactly match pending blocking decisions')
    expected_status = 'agent-work-complete-human-gate-pending' if pending_blockers else 'approved'
    if status.get('status') != expected_status:
        errors.append(f'p0-status status must be {expected_status!r} for current decision states')
    if expected_status == 'approved':
        for field in ('approved_at', 'approved_by'):
            if not status.get(field):
                errors.append(f'approved P0 status missing {field}')
        if status.get('next_phase_authorized') is not True:
            errors.append('approved P0 must authorize the next phase')
    return errors


def validate_roles(data: dict) -> list[str]:
    errors: list[str] = []
    assignments = data.get('assignments')
    if not isinstance(assignments, list):
        return ['role assignments require an assignments array']
    by_role = {item.get('role'): item for item in assignments if isinstance(item, dict)}
    required = {'Research Owner', 'Domain Lead', 'Data Steward', 'Methods / Statistics Lead', 'Independent Custodian'}
    missing = required - set(by_role)
    if missing:
        errors.append(f'missing required roles: {sorted(missing)}')
    if by_role.get('Research Owner', {}).get('identity') != 'RichardCao06':
        errors.append('P0-approved Research Owner must be RichardCao06')
    for role in ('Methods / Statistics Lead', 'Independent Custodian'):
        item = by_role.get(role, {})
        if item.get('status') == 'deferred' and not item.get('required_by'):
            errors.append(f'{role}: deferred assignment requires an explicit deadline')
    if by_role.get('Independent Custodian', {}).get('identity') == by_role.get('Research Owner', {}).get('identity'):
        errors.append('Independent Custodian must not collapse into the Research Owner')
    return errors


def validate_identity() -> list[str]:
    errors: list[str] = []
    paths = [ROOT / 'README.md', ROOT / 'docs/p0/protocol-v0.1.md']
    for path in paths:
        if 'GoalEvo' in path.read_text(encoding='utf-8'):
            errors.append(f'{path.relative_to(ROOT)}: external project branding leaked into project identity')
    return errors


def validate_cross_file(register: dict, status: dict) -> list[str]:
    errors: list[str] = []
    decisions = {item['id']: item for item in register.get('decisions', [])}
    expected = {
        'PCT-P0-D01': 'A', 'PCT-P0-D02': 'A', 'PCT-P0-D03': 'A',
        'PCT-P0-D04': 'A', 'PCT-P0-D05': 'A', 'PCT-P0-D06': 'A',
        'PCT-P0-D07': 'A', 'PCT-P0-D08': 'B', 'PCT-P0-D09': 'A',
        'PCT-P0-D10': 'A',
    }
    actual = {did: decisions.get(did, {}).get('human_decision') for did in expected}
    if actual != expected:
        errors.append(f'approved P0 choices differ from the human PR decision: {actual}')
    protocol = (ROOT / 'docs/p0/protocol-v0.1.md').read_text(encoding='utf-8')
    if 'does **not** establish that the proposed method is effective' not in protocol:
        errors.append('protocol must preserve the P0 no-effectiveness-claim boundary')
    gate = (ROOT / 'docs/p0/p0-exit-gate.md').read_text(encoding='utf-8')
    if 'P0 approved and complete' not in gate:
        errors.append('P0 Exit Gate must record approved completion')
    if status.get('protocol_version') != '0.1':
        errors.append('P0 status must point to Protocol v0.1')
    return errors


def validate_required_files() -> list[str]:
    return [f'missing required P0 artifact: {name}' for name in REQUIRED_FILES if not (ROOT / name).is_file()]


def validate_json_files() -> list[str]:
    errors: list[str] = []
    for path in ROOT.rglob('*.json'):
        try:
            json.loads(path.read_text(encoding='utf-8'))
        except json.JSONDecodeError as exc:
            errors.append(f'{path.relative_to(ROOT)}: invalid JSON: {exc}')
    return errors


def validate_markdown_links() -> list[str]:
    errors: list[str] = []
    link_pattern = re.compile(r'(?<!!)\[[^\]]+\]\(([^)]+)\)')
    for path in ROOT.rglob('*.md'):
        text = path.read_text(encoding='utf-8')
        for target in link_pattern.findall(text):
            target = target.strip().split('#', 1)[0]
            if not target or re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target) or target.startswith('/'):
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                errors.append(f'{path.relative_to(ROOT)}: link escapes repository: {target}')
                continue
            if not resolved.exists():
                errors.append(f'{path.relative_to(ROOT)}: broken local link: {target}')
    return errors


def main() -> int:
    errors = validate_required_files()
    try:
        register = load_json(ROOT / 'governance/decision-register.json')
        status = load_json(ROOT / 'governance/p0-status.json')
        roles = load_json(ROOT / 'governance/role-assignments.json')
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(str(exc))
    else:
        errors.extend(validate_decision_register(register))
        errors.extend(validate_status(status, register))
        errors.extend(validate_roles(roles))
        errors.extend(validate_cross_file(register, status))
    errors.extend(validate_identity())
    errors.extend(validate_json_files())
    errors.extend(validate_markdown_links())
    if errors:
        print('P0 validation failed:', file=sys.stderr)
        for error in errors:
            print(f' - {error}', file=sys.stderr)
        return 1
    print('P0 validation passed: approved baseline is internally consistent.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
