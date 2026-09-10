# P2 Foundation Validation Record v0.1

## Status

**FOUNDATION VALIDATED — HUMAN DECISION GATE OPEN**

The P2 Shadow foundation on branch `research/p2-shadow-foundation-v0.1` has passed the complete repository validation suite after correcting two JSON-syntax defects in the initial Schema commit.

## Preserved first failure

The first remote CI run failed because the following newly added files were not valid JSON:

- `schemas/pct-p2-replay-bundle-v0.1.schema.json`;
- `schemas/pct-p2-shadow-verdict-v0.1.schema.json`.

The failure was preserved in GitHub Actions. The repair changed JSON syntax/formatting only and did not change the P2 authority model, label policy, event model, or no-intervention boundary.

## Validated foundation

- P0 and P1 historical integrity checks remain enabled;
- P1 closure remains authoritative and unchanged;
- P2 event and Evidence storage are append-only;
- Evidence invalidation and Goal-revision binding are deterministic;
- Candidate-Stop snapshots bind to the event-log tail;
- replay hashes inputs, event log, snapshot, verdict, and bundle;
- hidden, Gold, reference, sealed, and Human-label fields are rejected recursively;
- runtime-mutation calls are statically prohibited;
- no `agent.steer()` or equivalent intervention is available;
- policy-pending mode cannot emit formal Shadow labels;
- ten new P2 foundation tests are included in the full suite.

## Current Gate

Open normative decisions:

```text
PCT-P2-D01
PCT-P2-D02
PCT-P2-D03
PCT-P2-D04
PCT-P2-D05
PCT-P2-D06
PCT-P2-D07
```

Until all required decisions are approved and a versioned Shadow Policy is frozen:

```text
mode = SHADOW
applied_to_runtime = false
verdict_status = POLICY_PENDING
labels_emitted = false
```

No live/private trace collection, semantic Audit Agent call, reference-evaluator opening, natural-task Shadow run, online intervention, or effectiveness claim is authorized by this validation record.
