# Observable Trace Model v0.1 — Draft

## Design principle

PCT records what can be independently observed and replayed. It does not require or treat private chain-of-thought as authoritative.

The trace separates:

- task and goal obligations;
- environment snapshots;
- observable events;
- evidence objects;
- Candidate Stops;
- annotations stored outside the Worker-visible trace.

## Canonical event classes

| Canonical event | Purpose |
|---|---|
| `GOAL_DEFINED` | establish goal ID, revision, and obligations |
| `OBSERVATION` | record a bounded environment or artifact observation |
| `DECISION_CHECKPOINT` | optional structured Worker claim, assumptions, and intended next state |
| `TOOL_CALL` / `TOOL_RESULT` | record requested action and authoritative result |
| `STATE_DELTA` | record observed change and evidence invalidation scope |
| `EVIDENCE_RECORDED` | identify evidence and its provenance |
| `OBLIGATION_TRANSITION` | record how an obligation's state was promoted or reopened |
| `CANDIDATE_STOP` | identify the natural stop boundary to annotate |
| `VERIFIER_RESULT` / `AUDITOR_RESULT` | store independent checks with clear actor identity |
| `REPAIR_FEEDBACK` | store later feedback without leaking it into the pre-stop annotation view |
| `HUMAN_INPUT` | record authorized decisions or clarifications |
| `BUDGET_EVENT` / `ERROR` | distinguish resource and infrastructure termination from success |

## DeepSeek Harness mapping at the selected commit

At `deepseek-ai/deepseek-harness@141eb6fef83422698aef7a981029e843e8161534`:

- replayable facts are available through `session/event`, including turn/step boundaries, assistant output, tool calls, and tool results;
- live coordination is exposed through `agent/*` events;
- `agent/turn-stopping` is the natural-stop checkpoint before the turn closes;
- `tools/result` provides the immutable final tool outcome for live observation.

P1 defines the canonical model but does not yet install a production adapter or online stop interceptor.

## Evidence lineage

Every evidence record binds to:

- a goal revision;
- a snapshot ID;
- one or more obligation IDs;
- source class and verdict;
- creation event;
- invalidating later events.

A current completion claim cannot rely on evidence invalidated before the Candidate Stop.

## Structural validity versus process correctness

The schema must be able to record failures. Therefore:

- structural validation checks types, IDs, ordering, references, visibility, and leakage;
- deterministic linting emits candidate findings such as stale evidence or verification without evidence;
- human/Auditor annotation determines whether those findings are genuine process defects.

A failure trajectory is valid research data and must not be rejected merely because its process is wrong.

## Visibility and leakage

Observable Worker traces must not contain:

- Gold labels;
- hidden failure locations;
- hidden evaluator outputs;
- reference truth;
- sealed results.

Annotations and offline evaluator labels live in separate stores with independent access control.

## Decision checkpoints

The draft schema permits optional structured checkpoints containing claims, cited evidence, assumptions, and expected effects. They are useful for audit localization but remain Worker self-reports. P1-D09 determines whether and where they are required.
