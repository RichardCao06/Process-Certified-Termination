# P2 — DeepSeek Harness Process-Certification Shadow Study

## Current status

```text
P1: CLOSED / APPROVED WITH LIMITATIONS
P2 foundation: ACTIVE under A0–A2 reversible sandbox authority
P2-D01 through P2-D07: PENDING HUMAN
Live Shadow measurement: NOT AUTHORIZED
Semantic Audit Agent: NOT AUTHORIZED
Online intervention: NOT AUTHORIZED
Effectiveness claim: NOT ALLOWED
```

P2 begins with a non-intervening foundation. The code in `pct/shadow/` can
normalize supplied observable events, construct append-only evidence, run
descriptive deterministic checks, and replay a Candidate Stop. It does not
register a Harness hook, call a model, access hidden/reference data, or apply a
verdict to runtime.

## Human Gate

Read:

- [`p2-human-decision-pack-v0.1.md`](p2-human-decision-pack-v0.1.md)
- [`work-order-PCT-P2-001-v0.1.md`](work-order-PCT-P2-001-v0.1.md)

The decision source of truth is:

- `governance/p2-decision-register-v0.1.json`
- `governance/p2-status-v0.1.json`

## Foundation artifacts

- Shadow foundation specification:
  `p2-shadow-foundation-spec-v0.1.md`
- Data and isolation draft:
  `p2-data-and-isolation-boundary-v0.1-draft.md`
- Exit Gate draft:
  `p2-exit-gate-v0.1-draft.md`
- Draft inactive policy:
  `governance/p2-shadow-policy-v0.1-draft.json`
- JSON schemas:
  `schemas/pct-p2-*.schema.json`
- Python foundation:
  `pct/shadow/`
- Replay CLI:
  `scripts/p2_replay_shadow.py`
- Validator:
  `scripts/validate_p2_foundation.py`

## Validation

```bash
make validate-p2-foundation
python3 -m unittest tests.test_p2_shadow_foundation -v
```

The P2 foundation is an engineering scaffold. Passing its tests does not
establish Auditor accuracy, human-label validity, cross-Harness compatibility,
or online PCT effectiveness.
