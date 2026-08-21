# Work Order PCT-P1-001

| Field | Value |
|---|---|
| Title | Develop process-failure taxonomy, annotation protocol, and observable trace infrastructure |
| Phase | P1 |
| Risk | Medium — methodological semantics and development data |
| Agent autonomy | A0–A2 for reversible development work |
| Human owner | RichardCao06, Research Owner |
| Status | Agent foundation complete; human decisions and pilot pending |

## Goal

Create a reviewable and executable foundation for describing process failures at Candidate Stops, locating the First Invalid Transition, and measuring annotation feasibility without accessing hidden or sealed evaluator information.

## Non-goals

- implement an online termination controller;
- certify real benchmark runs;
- train or select a production Process Auditor;
- freeze agreement thresholds, sample size, or confirmatory statistics;
- access held-out or sealed evaluator material;
- claim the taxonomy is exhaustive or reliable before the human pilot.

## Inputs

- approved PCT Protocol v0.1 and four P0 contracts;
- selected DeepSeek Harness development commit `141eb6fef83422698aef7a981029e843e8161534`;
- public Harness lifecycle documentation;
- synthetic, non-sensitive development fixtures only.

## Deliverables

1. multi-axis failure-taxonomy draft;
2. Candidate-Stop annotation codebook;
3. trace, evidence, and annotation schemas;
4. structural validator and deterministic lint candidates;
5. annotation-agreement development utility;
6. controlled positive, negative, stale-evidence, failure-propagation, and alternate-path fixtures;
7. human decision pack and machine-readable register;
8. red-team report and P1 exit conditions;
9. CI integration and tests.

## Acceptance criteria for the Agent-owned foundation

- malformed and leaking traces are rejected;
- valid alternative paths are not rejected merely for order differences;
- structurally valid failure trajectories can still be recorded and annotated;
- deterministic lints distinguish candidate findings from human Gold labels;
- hard-gate codes cannot be invented outside the P0-approved classes;
- an `ACCEPT` annotation cannot coexist with failed outcome/process verdicts or hard-gate violations;
- synthetic fixtures cover positive, negative, boundary, and evidence-invalidation cases;
- all normative P1 choices remain explicitly pending human approval;
- `make validate` passes after integration.

## Human decisions

PCT-P1-D01 through PCT-P1-D10 in the [Human Decision Pack](human-decision-pack.md).
