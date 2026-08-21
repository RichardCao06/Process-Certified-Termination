#!/usr/bin/env python3
"""Deterministic integrity checks for the PCT P0 governance package."""
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
    'docs/p0/protocol-v0.1-draft.md',
    'docs/p0/human-decision-pack.md',
    'docs/p0/decision-register.md',
    'docs/p0/threat-model.md',
    'docs/p0/role-and-authority-map.md',
    'docs/p0/causal-model.md',
    'docs/p0/claim-ladder.md',
    'docs/p0/literature-baseline.md',
    'docs/p0/p0-exit-gate.md',
    'docs/p0/contracts/goal-contract-v0.1-draft.md',
    'docs/p0/contracts/autonomy-contract-v0.1-draft.md',
    'docs/p0/contracts/assurance-contract-v0.1-draft.md',
    'docs/p0/contracts/capability-envelope-v0.1-draft.md',
    'docs/governance/human-agent-collaboration-protocol-v0.1-draft.md',
    'docs/references/SOURCE-MANIFEST.md',
    'governance/decision-register.json',
    'governance/p0-status.json',
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
        option_ids = {item.get('id') for item in options if isinstance(item, dict)}
        if decision.get('agent_recommendation') not in option_ids:
            errors.append(f'{did}: recommendation must reference a declared option')
        if decision.get('normative') is True:
            owner = decision.get('owner_role')
            if not isinstance(owner, str) or any(word in owner for word in AGENT_ROLE_WORDS):
                errors.append(f'{did}: normative decision must have a human owner role')
        if decision.get('status') in {'approved', 'rejected'}:
            for field in ('human_decision', 'rationale', 'approver_identity', 'effective_from'):
                if not decision.get(field):
                    errors.append(f'{did}: resolved decision missing {field}')
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
        errors.append('candidate DeepSeek Harness commit must be a 40-character SHA')
    pending_blockers = [d['id'] for d in register['decisions'] if d.get('blocks_p0') and d.get('status') == 'pending-human']
    if status.get('blocking_decision_ids') != pending_blockers:
        errors.append('p0-status blocking_decision_ids must exactly match pending blocking decisions')
    expected_status = 'agent-work-complete-human-gate-pending' if pending_blockers else 'approved'
    if status.get('status') != expected_status:
        errors.append(f'p0-status status must be {expected_status!r} for current decision states')
    return errors


def validate_identity() -> list[str]:
    errors: list[str] = []
    # The collaboration-protocol provenance note may describe an external source;
    # core project identity documents must not adopt unrelated project branding.
    paths = [ROOT / 'README.md', ROOT / 'docs/p0/protocol-v0.1-draft.md']
    for path in paths:
        if 'GoalEvo' in path.read_text(encoding='utf-8'):
            errors.append(f'{path.relative_to(ROOT)}: external project branding leaked into project identity')
    return errors


def validate_cross_file_recommendations(register: dict) -> list[str]:
    errors: list[str] = []
    recommendations = {item['id']: item.get('agent_recommendation') for item in register.get('decisions', [])}
    if recommendations.get('PCT-P0-D08') != 'B':
        errors.append('PCT-P0-D08 recommendation must match the human decision pack: B')
    protocol = (ROOT / 'docs/p0/protocol-v0.1-draft.md').read_text(encoding='utf-8')
    if 'P0 creates a research contract. It does **not** establish that the proposed method is effective.' not in protocol:
        errors.append('protocol must preserve the P0 no-effectiveness-claim boundary')
    agents = (ROOT / 'AGENTS.md').read_text(encoding='utf-8')
    if 'not a GoalEvo subproject' not in agents:
        errors.append('AGENTS.md must state project independence explicitly')
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
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(str(exc))
    else:
        errors.extend(validate_decision_register(register))
        errors.extend(validate_status(status, register))
        errors.extend(validate_cross_file_recommendations(register))
    errors.extend(validate_identity())
    errors.extend(validate_json_files())
    errors.extend(validate_markdown_links())
    if errors:
        print('P0 validation failed:', file=sys.stderr)
        for error in errors:
            print(f' - {error}', file=sys.stderr)
        return 1
    print('P0 validation passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
