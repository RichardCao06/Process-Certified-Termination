# P2 Shadow Foundation Specification v0.1

## Status

**IMPLEMENTED AS A REVERSIBLE, NON-OPERATIVE FOUNDATION.**

This specification supersedes neither P1 nor the earlier architecture draft.
It turns the non-intervening portions of that draft into testable code while
leaving P2-D01–D07 unresolved.

## 1. Trust boundary

```text
Untrusted Worker/Harness envelopes
              ↓
Observable-only adapter + hidden-field guard
              ↓
Append-only canonical PCT event log
              ↓
Evidence Ledger and invalidation lineage
              ↓
Candidate-Stop Snapshot
              ↓
Deterministic descriptive checks
              ↓
Policy-pending Shadow envelope
              ↓
Replay bundle and hashes
```

No arrow returns to the Worker. There is no steering, blocking, continuation,
Goal mutation, or completion-state write.

## 2. Canonical invariants

1. Event `sequence` is contiguous from 1.
2. `event_id` is unique.
3. Events are immutable after append.
4. Evidence records are immutable; invalidations are append-only references.
5. Evidence is current only for the same Goal ID and Goal revision and when no
   invalidation event is recorded.
6. A Candidate-Stop Snapshot binds to the tail `CANDIDATE_STOP` event.
7. Every replay bundle hashes its input, event log, snapshot, verdict, and full
   bundle.
8. Runtime inputs may not contain Human labels, Author Intent, Gold, hidden
   evaluator, reference truth, or sealed-test fields.
9. A verdict may never be applied to runtime in P2 Shadow mode.

## 3. Policy-pending behavior

Before human decisions are frozen:

```json
{
  "verdict_status": "POLICY_PENDING",
  "labels_emitted": false,
  "mode": "SHADOW",
  "applied_to_runtime": false
}
```

Deterministic findings remain available because they are observable engineering
facts or candidate diagnostics. Their hard-versus-descriptive status is not
chosen by the code.

## 4. Frozen-policy behavior

After a versioned policy has:

- `status=FROZEN`;
- `online_intervention_authorized=false`;
- approved `PCT-P2-D01`;
- approved `PCT-P2-D03`;

the same engine may emit policy-defined Shadow labels. The code still cannot
apply them to the Harness.

The foundation intentionally requires explicit lists of:

- primary label layers;
- human-review layers;
- hard check IDs.

An empty or pending policy cannot silently become permissive.

## 5. Implemented check candidates

| Check | Candidate diagnostic | Default status |
|---|---|---|
| VERIFIED without valid Evidence | `EVD.MISSING_REQUIRED_EVIDENCE` | descriptive pending D03 |
| Stale or wrong-revision Evidence referenced | `EVD.STALE_EVIDENCE` | descriptive pending D03 |
| Authoritative FAIL not propagated | `TRN.FAILURE_NOT_PROPAGATED` | descriptive pending D03 |
| Hard obligation unresolved at completion proposal | `EXIT.PREMATURE_TERMINATION` | descriptive |
| Unknown recovery authority at no-further-action/blocker stop | recommendation `UNDETERMINED` | descriptive |
| Self-service recovery but blocker claimed | `EXIT.FALSE_BLOCKER` | descriptive |
| TURN_STOP represented as Goal completion | termination diagnostic | descriptive |
| Budget stop represented as success | termination diagnostic | descriptive |
| Irreversible unauthorized action | `ACT.IRREVERSIBLE_WITHOUT_APPROVAL` | descriptive pending D03 |
| Protected evaluator modification | `INT.EVALUATOR_TAMPERING` | descriptive pending D03 |

The implementation does not claim these checks are exhaustive or perfectly
mapped to every DeepSeek Harness event.

## 6. DeepSeek Harness compatibility status

The adapter currently normalizes supplied envelopes corresponding to:

- `turn/start`;
- `turn/end`;
- `step/start`;
- `step/end`;
- `user/message`;
- `assistant/message`;
- `tool/call`;
- `tool/result`;
- `goal/change`;
- a supplied `agent/turn-stopping` record.

This is an interface contract, not proof that a specific current Harness commit
emits every field exactly as assumed. P2.0 must freeze and test the exact
external commit before any live collection.

## 7. Replay

```bash
python3 scripts/p2_replay_shadow.py \
  data/p2/fixtures/replay-clean-success-v0.1.json \
  --output /tmp/clean-replay.json

python3 scripts/p2_replay_shadow.py /tmp/clean-replay.json --verify
```

Replay does not call the Worker, Harness, model, network, shell tools, or
reference evaluator.

## 8. Security posture

The foundation rejects prohibited reference keys recursively. It also parses
Python source to detect direct calls to mutation-like methods such as `steer`,
`block_stop`, `resume_agent`, or Goal-state mutation.

These are defense-in-depth engineering checks, not a complete security proof.

## 9. Allowed conclusion

Only:

> A non-intervening, policy-gated and replayable engineering foundation exists
> for supplied observable Candidate-Stop traces.

Not:

> The DeepSeek Harness integration is complete, the Auditor is accurate, or PCT
> improves task success.
