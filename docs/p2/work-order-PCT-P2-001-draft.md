# Work Order PCT-P2-001 — Draft

| Field | Draft value |
|---|---|
| Title | DeepSeek Harness Process-Certification Shadow Plugin |
| Phase | P2 |
| Status | Draft only; not authorized |
| Risk | Medium — runtime observation and research-data collection |
| Agent autonomy | A2 sandbox implementation after human approval |
| Human owner | Research Owner |

## Goal

Implement a non-intervening DeepSeek Harness plugin that captures observable execution trajectories, reconstructs Goal obligations and Evidence state at each Candidate Stop, and emits a replayable Shadow certification verdict without changing Worker behavior.

## Non-goals

- no `agent.steer()`;
- no blocking or extending a Worker turn;
- no Worker completion-authority change;
- no hidden evaluator feedback to Worker or Shadow Auditor;
- no sealed-test execution;
- no claim of improved task success;
- no cross-Harness generality claim.

## Inputs required from P1

- P1 Closure Report;
- label-layer reliability matrix;
- approved Codebook and Schema version;
- classes allowed for Shadow measurement;
- retained ambiguity policy;
- P1 → P2 migration record.

## Deliverables

1. DeepSeek Harness event adapter;
2. append-only PCT event log;
3. Evidence Ledger with Goal revision and snapshot binding;
4. Candidate-Stop Snapshot builder;
5. deterministic Shadow Auditor;
6. replay command;
7. Shadow Verdict schema;
8. leakage and permission tests;
9. controlled synthetic Shadow fixtures;
10. P2 data-retention and privacy record;
11. Shadow benchmark protocol draft;
12. P2 Exit Gate.

## Candidate acceptance criteria

- representative Harness events map deterministically to PCT events;
- every Shadow Verdict can be reconstructed from the frozen event log;
- Shadow mode cannot invoke runtime mutation APIs;
- stale Evidence and Goal-revision changes invalidate old certification support;
- all findings cite observable Event and Evidence IDs;
- valid alternate paths remain accepted when obligations and evidence are satisfied;
- hidden, Gold, sealed, Human-label, and Fixture Author fields are rejected from the runtime input schema;
- failures and malformed traces remain preserved;
- no online intervention occurs.

## Proposed implementation stages

### P2.0 — Adapter contract

Normalize `session/event`, `tools/result`, `agent/turn-stopping`, and Goal state into the approved trace schema.

### P2.1 — Evidence and replay

Implement Evidence extraction, invalidation, snapshots, hashing, and deterministic replay.

### P2.2 — Deterministic Shadow checks

Implement only P0-approved hard checks and P1-approved descriptive checks.

### P2.3 — Optional semantic Shadow Auditor

Add a fresh-context, read-only Auditor only for obligations not decidable by deterministic checks.

### P2.4 — Shadow measurement

Compare natural Harness stopping with Shadow decisions and offline reference labels on copied snapshots.

## Human decisions required before authorization

### P2-D01 — Label scope

Which P1 label layers are stable enough to use as P2 endpoints or development targets?

### P2-D02 — Runtime data policy

What trace content may be retained, for how long, and under what privacy/redaction rules?

### P2-D03 — Deterministic hard checks

Which checks retain non-compensatory hard-gate status in P2?

### P2-D04 — Audit Agent configuration

Which model, tools, context isolation, and budget may the semantic Auditor use?

### P2-D05 — Reference evaluator isolation

Who controls offline labels, what information is visible, and how is leakage prevented?

### P2-D06 — Shadow sample and budget

Which task stream, number of Candidate Stops, repeated runs, token/time/tool budgets, and failure handling are approved?

### P2-D07 — Online-intervention evidence Gate

What Shadow evidence is required before an online controller may even be proposed?

## Research boundaries

P2 should first estimate measurement and replay feasibility. Any online stopping intervention, repair loop, or causal effectiveness claim requires a later protocol and independent Methods / Statistics review.

## Authorization record

```text
Research Owner:
Methods / Statistics reviewer:
Data Steward:
Date:
Status: APPROVED / APPROVED WITH AMENDMENTS / NOT APPROVED
Approved autonomy:
Accepted risks:
```
