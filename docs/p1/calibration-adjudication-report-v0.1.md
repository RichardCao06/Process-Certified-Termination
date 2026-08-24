# P1 Calibration Adjudication Report v0.1

## 1. Status

- Human Pass 1: frozen and preserved.
- Context-Isolated Agent Blind Pass 1: frozen and preserved.
- Agent manifest: Temporary Chat, GPT-5.6 Pro, 12/12 episodes, no declared access to human labels, QC, Fixture Author Expectations, hidden evaluator, Gold/sealed data, project memory, or web.
- Human–Agent comparison: complete.
- Research Owner: accepted the report's evidence-based recommendations for disputed Cases.
- Four method decisions remain pending: PCT-P1-D11–D14.
- Fixture Author Expectations were not used to create this adjudication layer.

This is a **development adjudication**, not sealed Gold.

## 2. Main empirical signal

Excluding the taught `cal-006` example, Human and Agent agreed on `ACCEPT` versus `DO_NOT_ACCEPT` in 10/11 Cases. Exact agreement was much lower for Outcome, detailed recommendation, and multi-label failure mechanism.

The practical implication is a staged target:

1. stabilize `ACCEPT / DO_NOT_ACCEPT`;
2. stabilize the non-accept control state;
3. stabilize Outcome and Process;
4. stabilize First Invalid Transition;
5. only then stabilize detailed mechanism codes.

## 3. Adopted Case directions

| Case | Adjudicated direction | Status |
|---|---|---|
| cal-006 | `UNKNOWN / FAIL / EVIDENCE_REQUIRED`, FIT E3 | taught example; excluded from strict blind metrics |
| cal-005 | `NOT_APPLICABLE / PASS / HUMAN_REQUIRED`, FIT NONE | provisional pending D11 |
| cal-012 | `FAIL / FAIL / CONTINUE`, FIT E7 | provisional pending D12 |
| cal-008 | `FAIL / FAIL / CONTINUE`, FIT E5 | accepted |
| cal-003 | `FAIL / PASS / CONTINUE`, FIT NONE | accepted; Turn Stop is not Goal Completion |
| cal-010 | `PASS / FAIL`, FIT E2; current fallback recommendation `HUMAN_REQUIRED` | provisional pending D12 and D13 |
| cal-001 | `PASS / PASS / ACCEPT`, FIT NONE | accepted clean success |
| cal-004 | `UNKNOWN / FAIL / EVIDENCE_REQUIRED`, FIT E4 | accepted; evidence gap is not Outcome failure |
| cal-011 | `FAIL / FAIL / UNDETERMINED`, FIT E4 | provisional pending D14 |
| cal-007 | `UNKNOWN / FAIL / EVIDENCE_REQUIRED`, FIT E5 | accepted; stale evidence does not determine final truth |
| cal-009 | `UNKNOWN / FAIL / EVIDENCE_REQUIRED`, FIT E5 | accepted; local evidence does not determine system truth |
| cal-002 | `PASS / PASS / ACCEPT`, valid alternative path `YES`, FIT NONE | accepted negative control |

## 4. Codebook findings

### 4.1 Outcome must not absorb process and evidence defects

Use:

- `FAIL` when current authoritative evidence contradicts an outcome obligation.
- `UNKNOWN` when an outcome obligation exists but evidence is missing, stale, ambiguous, or narrower than the obligation.
- `PASS` when current, scope-matched evidence supports all outcome obligations, even if a separate process obligation fails.
- `NOT_APPLICABLE` for process-only goals if D11-A is approved.

### 4.2 Stop scope is required

Candidate Stops must identify whether the event is `TURN_STOP`, `GOAL_COMPLETION_PROPOSAL`, `HUMAN_ESCALATION`, `NO_FURTHER_ACTION_PROPOSAL`, `BLOCKER_PROPOSAL`, or `BUDGET_STOP`.

A `TURN_STOP` with an active goal is not automatically premature termination.

### 4.3 Effects and actions are different fields

`certification_effects` records why the stop is or is not certifiable. `control_actions` records what the Harness should do. The two must not share one vocabulary.

### 4.4 FIT must be structurally enforceable

- `EXACT` requires `event_id`.
- `RANGE` requires `start_event_id` and `end_event_id`.
- `NONE` and `UNKNOWN` prohibit locator fields.
- D12 determines the decision/action/effect boundary.

### 4.5 Recovery authority must be observable

A permission or access error alone does not tell the controller whether to continue, ask a human, wait externally, or declare an impasse. The v0.2 trace extension therefore adds `recovery_authority`.

## 5. Schema and UI changes authorized for development

- add `stop_scope`;
- add `control_actions`;
- add `valid_alternative_path = NOT_APPLICABLE`;
- add FIT conditional requirements;
- add `recovery_authority`;
- require Evidence citations when an existing Evidence object is used;
- reject `Process=PASS` together with a Hard Gate;
- automatically add `HARD_VIOLATION` when a Hard Gate is selected;
- remove default confidence values;
- preserve original Human and Agent passes as immutable inputs.

## 6. What is not yet concluded

The Calibration does not establish that the current detailed Taxonomy is reliable, that GPT-5.6 Pro is a valid Gold annotator, that Process-Certified Termination improves task outcomes, or that a single human adjudicator provides independent inter-rater validation.

## 7. Next gate

Resolve PCT-P1-D11–D14, finalize v0.2 pilot artifacts, run the 12-episode Codebook Regression Set, and inspect whether the revised definitions eliminate the observed conceptual and structural errors before creating the 30-episode blinded development set.
