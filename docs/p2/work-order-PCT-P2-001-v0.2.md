# Work Order PCT-P2-001 v0.2

## Goal

Build a replayable, non-intervening Process-Certification Shadow layer for observable DeepSeek Harness Candidate Stops, then evaluate it under separately frozen natural-task protocols.

## Current authorization

D01–D12 option A are approved. Current engineering may implement and validate:

- append-only Event and Evidence records;
- deterministic Candidate-Stop Snapshot and replay;
- frozen deterministic hard/descriptive checks;
- exact DeepSeek Harness source/envelope conformance;
- explicit read-only Candidate-Stop sidecar;
- synthetic/public non-sensitive regression.

## Current non-goals and prohibitions

- no natural-task Shadow measurement until D13–D18 are approved;
- no Worker or Semantic Auditor model calls;
- no private runtime trace collection;
- no Reference Evaluator opening;
- no Steering, blocking, resume, Goal mutation, or completion-authority change;
- no online intervention or production deployment;
- no accuracy, safety, benchmark-gain, or effectiveness claim.

## Current deliverables

1. D01–D12 Decision Records and active policy;
2. explicit sidecar schema, observer, snapshot and replay binding;
3. 20+10 synthetic regression and metrics;
4. exact DSH conformance validator;
5. D13–D18 Human Decision Pack for a first public natural-task pilot.

## Acceptance criteria for this increment

- sidecar mismatch is rejected;
- missing sidecar remains UNKNOWN/UNDETERMINED;
- assistant prose cannot fill sidecar fields;
- replay equality is 100% for accepted synthetic cases;
- 20+10 regression passes 30/30;
- runtime application count is zero;
- exact frozen DSH checkout passes source/envelope conformance in CI;
- D13–D18 remain unapproved and natural/model/reference authorities remain false.
