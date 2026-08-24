# P1 Decision Register

The machine-readable source is [`governance/p1-decision-register.json`](../../governance/p1-decision-register.json).

## Approved P1 method decisions

| ID | Decision | Human owner | State | Human choice |
|---|---|---|---|---|
| PCT-P1-D01 | annotation unit | Research Owner + Domain Lead | Approved | A — Candidate-Stop episode + transition localization |
| PCT-P1-D02 | taxonomy organization | Domain Lead | Approved | A — multi-axis |
| PCT-P1-D03 | verdict scale | Research Owner + Domain Lead | Approved | A — four-way verdict + separate recommendation |
| PCT-P1-D04 | localization policy | Domain Lead | Approved | A — exact/range/unknown |
| PCT-P1-D05 | hard versus soft treatment | Research Owner + Domain Lead | Approved | A — only P0 hard classes block |
| PCT-P1-D06 | pilot corpus | Research Owner + Data Steward | Approved | A — synthetic + public/development only |
| PCT-P1-D07 | annotation independence | Research Owner | Approved | A — delayed, reordered, blind second human pass; intra-rater only |
| PCT-P1-D08 | pilot size | Research Owner | Approved | A — 12 calibration + 30 blinded development episodes |
| PCT-P1-D09 | decision checkpoints | Data Steward + Domain Lead | Approved | A — optional; required only when instrumented |
| PCT-P1-D10 | P1 completion | Research Owner | Approved | A — pilot and revision Gate, not tooling alone |

The approval source is PR #2 comment `5365882275`. No additional Hard Gate or data source was added.

## Post-calibration human Gate

| ID | Question | State | Agent recommendation |
|---|---|---|---|
| PCT-P1-D11 | Outcome verdict for correctly escalated process-only goals | Pending human | A — `NOT_APPLICABLE` |
| PCT-P1-D12 | FIT decision/action/effect boundary | Pending human | A — earliest observable invalid Worker decision/action |
| PCT-P1-D13 | irreversible authorization/integrity breach terminal state | Pending human | A — add `INCIDENT_ESCALATION` |
| PCT-P1-D14 | unknown recovery authority | Pending human | A — `UNDETERMINED` + explicit `recovery_authority` |

See [Post-Calibration Human Decision Pack](post-calibration-human-decision-pack.md) for the full alternatives and effects.

## Decision semantics

D11–D14 change annotation or controller semantics, so they remain human decisions even though the Research Owner accepted the prior Case-level recommendations. Reversible implementation preparation is allowed; the v0.2 pilot version cannot be finalized until these decisions are resolved.
