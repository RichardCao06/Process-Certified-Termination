# P1 — Process Taxonomy, Annotation Feasibility, and Trace Infrastructure

P1 operationalizes the approved P0 research object: the **observable execution trajectory** around a Candidate Stop. It does not test the online PCT controller and does not make an effectiveness claim.

## Current status

- P1-D01 through P1-D10: approved by the Research Owner.
- Human Calibration Pass 1: frozen and preserved.
- Context-isolated Agent Blind Pass 1: frozen and preserved.
- Human–Agent comparison: complete.
- Core Case recommendations: accepted by the Research Owner.
- Post-calibration method decisions P1-D11 through P1-D14: pending human disposition.
- Codebook / Trace / Annotation Schema v0.2: development drafts prepared.
- 12-episode Codebook Regression Set: prepared but not yet run under the finalized D11–D14 semantics.
- 30-episode blinded development pilot: not yet started.

P1 therefore remains at the **post-calibration revision Gate**. Human decisions and annotation pilot pending items remain before P1 closure.

## Main calibration signal

Excluding the taught `cal-006` Case, Human and Agent agreed on `ACCEPT` versus `DO_NOT_ACCEPT` in 10 of 11 Cases, while exact Outcome and detailed failure-code agreement were much lower. The development response is to stabilize the hierarchy in this order:

1. accept versus do not accept;
2. specialized non-accept control state;
3. Outcome and Process verdicts;
4. First Invalid Transition;
5. detailed failure mechanism codes.

This is descriptive Calibration evidence, not a confirmatory result.

## Current authoritative development materials

- [Work Order PCT-P1-001](work-order-PCT-P1-001.md)
- [Calibration Recommendation Acceptance Record](calibration-recommendation-acceptance-record.md)
- [Calibration Adjudication Report v0.1](calibration-adjudication-report-v0.1.md)
- [Post-Calibration Human Decision Pack](post-calibration-human-decision-pack.md)
- [Annotation Codebook v0.2 Draft](annotation-codebook-v0.2-draft.md)
- [Trace Observation Model v0.2 Draft](trace-observation-model-v0.2-draft.md)
- [Annotation Migration v0.1 to v0.2](taxonomy-migration-v0.1-to-v0.2.md)
- [Failure Taxonomy v0.1 Draft](failure-taxonomy-v0.1-draft.md)
- [DeepSeek Harness Event Mapping](deepseek-harness-event-mapping.md)
- [Red-Team Review](red-team-review.md)
- [P1 Exit Gate](p1-exit-gate.md)

Historical v0.1 drafts and the original Human/Agent passes remain preserved. Derived adjudication does not overwrite them.

## Four human decisions still required

- PCT-P1-D11 — Outcome semantics for a correctly escalated process-only goal.
- PCT-P1-D12 — FIT boundary between invalid decision/action and resulting effect/assertion.
- PCT-P1-D13 — terminal recommendation after an irreversible authorization/integrity breach.
- PCT-P1-D14 — recommendation policy when recovery authority is not observable.

The Agent recommendations are `A, A, A, A`, but they do not become effective without human approval.

## Development data and validation

The Calibration records are stored in a hash-verified bundle under `data/p1/calibration/`. It contains the two original passes, episode inputs, Human QC, comparison, derived adjudication, and regression expectations. It contains no Fixture Author Expectations, hidden evaluator output, held-out data, or sealed data.

```bash
make validate
make materialize-calibration
```

## Allowed conclusion now

> Human and context-isolated Agent labels show promising agreement on coarse stop acceptance, while Outcome semantics, next-state policy, FIT boundaries, and detailed diagnostic codes require revision and further feasibility testing.

This is not evidence that an automated Auditor or online Process-Certified Termination controller improves task performance.
