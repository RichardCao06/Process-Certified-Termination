# Observable Trace Model v0.2 — Post-Calibration Draft

## Purpose

The v0.2 extension preserves the v0.1 event/evidence model while adding the minimum metadata needed to distinguish stop scope, control action, and recovery authority.

## 1. New Candidate-Stop field: `stop_scope`

```text
TURN_STOP
GOAL_COMPLETION_PROPOSAL
HUMAN_ESCALATION
NO_FURTHER_ACTION_PROPOSAL
BLOCKER_PROPOSAL
BUDGET_STOP
OTHER
```

This field prevents a normal turn boundary from being interpreted as a goal-level success or failure.

## 2. New control field: `control_actions`

`certification_effects` remains a bounded description of certification consequences. `control_actions` records the requested Harness behavior. The two must not share one vocabulary.

## 3. New recoverability field: `recovery_authority`

```text
SELF_SERVICE
HUMAN_ONLY
EXTERNAL_WAIT
IMPOSSIBLE
UNKNOWN
NOT_APPLICABLE
```

This field can be placed in Candidate-Stop metadata or a blocker/recovery observation. It must be based on observable tool and authority information.

## 4. FIT conditional structure

The schema must use conditional validation:

```text
EXACT -> event_id required
RANGE -> start_event_id and end_event_id required
NONE/UNKNOWN -> locator fields forbidden
```

## 5. Process-only goals

The Goal Contract continues to classify obligation kinds. The Codebook derives Outcome applicability from those kinds instead of treating correct escalation as an ordinary external outcome.

## 6. Backward compatibility

- v0.1 trajectories remain immutable.
- v0.2 regression records wrap or map v0.1 trajectories; they do not overwrite original events.
- All label migration is explicit.
- Human Pass 1 and Agent Blind Pass 1 remain in their original schemas.

## 7. Visibility

The v0.2 extension adds no Gold, Fixture Author Expectation, hidden evaluator output, or post-stop repair result to Worker-visible traces.
