# P2 Shadow Plugin Architecture v0.1 — Draft

## Status and boundary

This is a non-operative architecture draft prepared while Human Pass B remains blinded. It does not start P2, intercept an Agent stop, change a Goal state, or claim Process-Certified Termination is effective.

P1 must close before a formal P2 Work Order authorizes runtime implementation. Any move from observation to intervention requires a separate human-approved Gate.

## 1. P2 objective

Build a **Shadow Process-Certification Plugin for DeepSeek Harness** that observes Candidate Stops, reconstructs the evidence and obligation state, and emits a structured certification recommendation without changing the Worker’s execution.

The first P2 question is:

> Can the Harness collect enough authoritative state and trajectory evidence to reproduce a Candidate-Stop audit deterministically and independently of the Worker’s completion claim?

The initial P2 question is not:

> Does blocking the Worker improve benchmark success?

That belongs to a later online-intervention phase.

## 2. Authority model

### Shadow mode

The plugin may:

- observe permitted Harness events;
- create immutable PCT event records;
- maintain a development Evidence Ledger;
- snapshot Candidate Stops;
- run deterministic checks;
- request a read-only Audit Agent in an isolated context;
- emit `ACCEPT`, `DO_NOT_ACCEPT`, and a specialized recommendation as a report;
- record what an online controller would have done.

The plugin must not:

- call `agent.steer()`;
- block `agent/turn-stopping`;
- mark a Goal complete, blocked, or failed;
- modify tools, tests, evaluator state, or the Worker context;
- expose hidden evaluator information;
- use Fixture Author Expectations as runtime evidence.

### Later online mode

A future human-approved phase may permit:

```text
Worker -> PROPOSED_COMPLETE
Trusted Controller -> COMPLETE / CONTINUE / EVIDENCE_REQUIRED / ...
```

That authority is explicitly outside this draft.

## 3. Package layout

Recommended repository layout:

```text
packages/pct/core
packages/pct/deepseek-harness-adapter
packages/pct/deterministic-auditor
packages/pct/shadow-runner
packages/pct/reporting
```

For the current repository prototype, the same separation can initially be represented as Python/TypeScript modules before extraction into packages.

## 4. Core data model

### 4.1 PCT Event

```ts
interface PctEvent {
  eventId: string
  sequence: number
  eventType:
    | 'GOAL_STATE'
    | 'OBSERVATION'
    | 'TOOL_CALL'
    | 'TOOL_RESULT'
    | 'STATE_DELTA'
    | 'DECISION_CHECKPOINT'
    | 'OBLIGATION_TRANSITION'
    | 'CANDIDATE_STOP'
    | 'HUMAN_STEERING'
  goalId: string
  goalRevision: number
  snapshotId: string
  sourceEventId?: string
  payload: unknown
  createdAt: string
}
```

### 4.2 Evidence Record

```ts
interface EvidenceRecord {
  evidenceId: string
  producer: string
  sourceClass:
    | 'DETERMINISTIC_VALIDATOR'
    | 'ENVIRONMENT_OBSERVATION'
    | 'TOOL_RESULT'
    | 'AUDIT_AGENT'
    | 'WORKER_CLAIM'
    | 'HUMAN_ACCEPTANCE'
  goalId: string
  goalRevision: number
  snapshotId: string
  obligationIds: string[]
  result: 'PASS' | 'FAIL' | 'UNKNOWN'
  scope: string[]
  invalidatedByEventIds: string[]
  digest: string
  locator?: string
}
```

`WORKER_CLAIM` is retained as an observable claim class but cannot independently satisfy an obligation that requires external evidence.

### 4.3 Obligation State

```ts
interface ObligationState {
  obligationId: string
  kind: 'OUTCOME' | 'DELIVERABLE' | 'INVARIANT' | 'PROCESS' | 'EVIDENCE'
  severity: 'HARD' | 'MAJOR' | 'MINOR'
  state: 'PENDING' | 'ATTEMPTED' | 'PROVISIONAL' | 'VERIFIED' | 'FAILED' | 'UNKNOWN'
  evidenceIds: string[]
  lastTransitionEventId?: string
}
```

### 4.4 Candidate-Stop Snapshot

```ts
interface CandidateStopSnapshot {
  stopId: string
  stopScope:
    | 'TURN_STOP'
    | 'GOAL_COMPLETION_PROPOSAL'
    | 'HUMAN_ESCALATION'
    | 'NO_FURTHER_ACTION_PROPOSAL'
    | 'BLOCKER_PROPOSAL'
    | 'BUDGET_STOP'
    | 'OTHER'
  goalId: string
  goalRevision: number
  snapshotId: string
  workspaceDigest?: string
  recoveryAuthority:
    | 'SELF_SERVICE'
    | 'HUMAN_ONLY'
    | 'EXTERNAL_WAIT'
    | 'IMPOSSIBLE'
    | 'UNKNOWN'
    | 'NOT_APPLICABLE'
  obligationStates: ObligationState[]
  evidenceIds: string[]
  lastSequence: number
}
```

### 4.5 Shadow Verdict

```ts
interface ShadowVerdict {
  stopId: string
  acceptDecision: 'ACCEPT' | 'DO_NOT_ACCEPT'
  outcomeVerdict: 'PASS' | 'FAIL' | 'UNKNOWN' | 'NOT_APPLICABLE'
  processVerdict: 'PASS' | 'FAIL' | 'UNKNOWN' | 'NOT_APPLICABLE'
  recommendation:
    | 'ACCEPT'
    | 'CONTINUE'
    | 'EVIDENCE_REQUIRED'
    | 'HUMAN_REQUIRED'
    | 'BLOCKED'
    | 'NO_PROGRESS'
    | 'UNDETERMINED'
    | 'INCIDENT_ESCALATION'
  certificationEffects: string[]
  controlActions: string[]
  failureCodes: string[]
  hardGateCodes: string[]
  firstInvalidTransition: unknown
  citations: {
    eventIds: string[]
    evidenceIds: string[]
  }
  mode: 'SHADOW'
  appliedToRuntime: false
}
```

## 5. DeepSeek Harness event adapter

The adapter should map only observable facts.

### `session/event`

Use for durable trajectory facts such as:

- assistant messages;
- tool calls and results;
- Goal changes;
- step and turn boundaries;
- steering and cancellation events.

### `tools/result`

Use as the preferred observation point for the final immutable tool result. A tool result may become Evidence only after its authority, scope, Goal revision, and snapshot are recorded.

### `agent/turn-stopping`

In Shadow mode:

- create a Candidate-Stop Snapshot;
- run the shadow audit asynchronously within the current request lifecycle if permitted;
- record the hypothetical recommendation;
- return without steering or blocking.

The Shadow listener must never turn a natural stop into another execution step.

### Goal service

Read Goal ID, revision, phase, and approved obligations. Do not mutate them in Shadow mode.

## 6. Processing pipeline

```text
Harness event
→ Adapter normalization
→ Append-only PCT event log
→ Evidence extraction
→ Evidence invalidation and freshness update
→ Obligation-state reconstruction
→ Candidate Stop snapshot
→ Deterministic process checks
→ Optional isolated read-only Audit Agent
→ Shadow verdict
→ Replayable report
```

## 7. Deterministic checks for the first prototype

The first implementation should prefer checks that can be evaluated without an LLM:

- duplicate or missing event IDs;
- Goal revision mismatch;
- Evidence bound to an older relevant snapshot;
- missing required Evidence for a mandatory obligation;
- authoritative FAIL not propagated to obligation state;
- `VERIFIED` transition with no valid Evidence IDs;
- Evidence scope narrower than the certified claim;
- protected test/evaluator path modified;
- Candidate Stop with unresolved feasible hard obligation;
- `BLOCKED` proposal while an authorized recovery action remains;
- budget exit represented as success;
- unauthorized or irreversible action before a required human Gate;
- `TURN_STOP` incorrectly interpreted as Goal completion.

Each check must emit Event and Evidence citations. A check may propose a taxonomy code but cannot create a new hard-gate class.

## 8. Replay and reproducibility

For every Candidate Stop, persist:

- normalized event log hash;
- Goal Contract version and hash;
- adapter version;
- deterministic auditor version;
- model and Audit Agent metadata when used;
- Candidate-Stop Snapshot hash;
- Shadow Verdict hash;
- cost and duration;
- any missing or malformed source events.

A replay command should reconstruct the verdict from the frozen event log without calling the Worker again.

## 9. Isolation and leakage controls

- Shadow Auditor receives only the approved observable trajectory and read-only environment tools.
- It cannot access Human labels, Fixture Author Expectations, hidden evaluator results, sealed tests, or other method outputs.
- Worker-generated text is treated as untrusted data and separated from auditor instructions.
- Tool outputs must be normalized so embedded prompt-injection text cannot silently become system policy.
- Hidden-evaluator details may label copied snapshots offline in a separate condition, but never enter the online Shadow context.

## 10. Shadow evaluation design

For each natural Candidate Stop:

```text
Worker/Harness natural decision: stop
Shadow PCT decision: accept or do not accept
Reference evaluator on copied snapshot: complete or incomplete/corrupt
```

The reference label is not returned to the Worker or Shadow Auditor.

This produces the later calibration table:

| | Reference complete | Reference incomplete/corrupt |
|---|---:|---:|
| Shadow ACCEPT | correct accept | false accept |
| Shadow DO_NOT_ACCEPT | false continue | correct continue |

Shadow mode measures decision quality without changing the Worker trajectory.

## 11. Milestones

### P2.0 — Adapter contract

- normalize representative DeepSeek Harness events;
- freeze event and snapshot schemas;
- validate missing, duplicate, and out-of-order events.

### P2.1 — Replayable Evidence Ledger

- append-only event storage;
- evidence freshness and invalidation;
- Goal revision and snapshot binding;
- deterministic replay.

### P2.2 — Deterministic Shadow Auditor

- implement P0-approved hard checks;
- produce structured citations;
- no LLM Judge and no runtime intervention.

### P2.3 — Isolated semantic Auditor

- add a fresh-context, read-only Audit Agent only for unresolved semantic obligations;
- compare raw transcript with structured evidence graph under matched compute.

### P2.4 — Shadow benchmark

- run natural Worker trajectories;
- label copied Candidate-Stop snapshots offline;
- estimate false accept, false continue, cost, and coverage.

### Later Gate — Online intervention

Only after Shadow evidence and a human-approved protocol may the project consider:

- completion authority separation;
- `agent.steer()` repair feedback;
- online evidence requests;
- incident escalation;
- no-progress termination.

## 12. Tests and invariants

Minimum tests before any Shadow run:

- positive and negative event mapping;
- deterministic replay equality;
- stale Evidence invalidation;
- Goal-revision change invalidates an old verdict;
- protected path modification is detected;
- valid alternative path is not rejected;
- `TURN_STOP` negative control;
- unknown recovery authority yields `UNDETERMINED`;
- irreversible unauthorized action yields `INCIDENT_ESCALATION`;
- no hidden/Gold/sealed fields accepted by the event schema;
- Shadow mode cannot call runtime mutation APIs.

## 13. Human decisions required before P2 starts

The P2 Work Order should ask the Research Owner to approve:

- exact P2 scope and allowed task stream;
- Shadow data retention and privacy policy;
- which deterministic checks are hard versus descriptive;
- Audit Agent model and tool permissions;
- offline reference-evaluator isolation;
- resource budget;
- minimum Shadow evidence required before online intervention is considered.

Methods / Statistics review is required before freezing confirmatory margins, sample size, exclusions, or primary statistical claims.

## 14. Allowed conclusion from this draft

Only:

> A proposed, testable architecture exists for collecting and replaying process-certification evidence in DeepSeek Harness Shadow mode.

The draft does not establish that the required Harness APIs are fully compatible, that the Auditor is accurate, or that online intervention improves results.
