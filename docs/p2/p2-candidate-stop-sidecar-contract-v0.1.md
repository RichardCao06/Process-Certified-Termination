# PCT P2 Explicit Candidate-Stop Sidecar Contract v0.1

**Status:** FROZEN FOR P2 SHADOW DEVELOPMENT  
**Human decision:** `PCT-P2-D12: A`  
**Authority:** read-only observation only  
**Runtime effect:** none (`mode=SHADOW`, `applied_to_runtime=false`)

## 1. Purpose

The frozen DeepSeek Harness boundary `agent/turn-stopping` tells an observer that a turn is about to stop, but its native payload does not state whether the Worker is proposing Goal completion, waiting for a human, reporting a blocker, or merely ending the current turn. PCT therefore uses an explicit sidecar supplied by a Task or Harness adapter.

The sidecar exists to prevent a dangerous substitution:

```text
no more tool calls / turn stopping
≠
Goal completion proved
```

## 2. Normative rule

PCT **MUST NOT** infer any of the following from assistant prose, wording, confidence, tool silence, or `turn/end` alone:

- `stop_scope`;
- `recovery_authority`;
- `worker_claim`;
- `claims_goal_complete`.

An integration **MUST** either provide a complete sidecar or explicitly record that sidecar metadata is missing.

## 3. Sidecar fields

```json
{
  "schema_version": "0.1",
  "sidecar_id": "...",
  "source": "TASK_ADAPTER | HARNESS_ADAPTER | TEST_FIXTURE",
  "session_id": "...",
  "turn": 1,
  "goal_id": "...",
  "goal_revision": 1,
  "snapshot_id": "...",
  "stop_scope": "GOAL_COMPLETION_PROPOSAL | TURN_STOP | HUMAN_ESCALATION | NO_FURTHER_ACTION_PROPOSAL | BLOCKER_PROPOSAL | BUDGET_STOP | OTHER",
  "recovery_authority": "SELF_SERVICE | HUMAN_ONLY | EXTERNAL_WAIT | IMPOSSIBLE | UNKNOWN | NOT_APPLICABLE",
  "worker_claim": "COMPLETE | TURN_COMPLETE | HUMAN_REQUIRED | BLOCKED | BUDGET_EXHAUSTED | NO_FURTHER_ACTION | OTHER | UNKNOWN",
  "claims_goal_complete": true,
  "created_at": "RFC3339 timestamp",
  "sidecar_digest": "lowercase SHA-256"
}
```

`claims_goal_complete=true` is valid only with `stop_scope=GOAL_COMPLETION_PROPOSAL`, and that scope requires the boolean to be true.

## 4. Binding and replay

The observer binds the sidecar to:

```text
session_id
turn
goal_id
goal_revision
snapshot_id
Candidate-Stop event
sidecar_id
sidecar_digest
```

The complete sidecar is preserved in replay input. The Candidate-Stop event and Candidate-Stop Snapshot preserve its identifier and digest. Any mismatch is rejected rather than silently repaired.

## 5. Missing metadata

When no sidecar is supplied, the observer records:

```text
metadata_status = MISSING
stop_scope = UNKNOWN
recovery_authority = UNKNOWN
worker_claim = UNKNOWN
claims_goal_complete = false
```

The deterministic Shadow layer then returns:

```text
accept_decision = DO_NOT_ACCEPT
certification_recommendation = UNDETERMINED
deterministic_decision_covered = false
```

Assistant prose such as “everything is complete” does not fill the missing fields.

## 6. Historical compatibility

Pre-D12 synthetic fixtures containing explicit Candidate-Stop fields but no sidecar are marked:

```text
metadata_status = LEGACY_EXPLICIT
```

They remain replayable for historical regression. A natural-task P2 pilot may not count `LEGACY_EXPLICIT` as explicit sidecar completeness.

## 7. Authority boundary

The observer and sidecar contract provide no method to:

- call `agent.steer()`;
- reject or block `agent/turn-stopping`;
- resume or continue the Worker;
- modify Goal state or completion authority;
- apply a Shadow verdict to runtime;
- expose Reference or Human labels to the Worker.

## 8. Engineering metrics

P2 records at least:

- explicit sidecar completeness rate;
- metadata-available rate, with legacy separated;
- deterministic decision coverage rate;
- deterministic replay equality rate;
- runtime-application incident count.

These are observability and replay metrics, not task-success or Auditor-accuracy claims.
