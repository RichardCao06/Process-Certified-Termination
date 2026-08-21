# Assurance Contract v0.1 — Draft

## Purpose

Define what evidence is sufficient, who may produce it, when it expires, and how uncertainty affects termination.

## Evidence hierarchy

Prefer, in order:

1. deterministic program or authoritative environment state;
2. property tests, replay, differential checks, or independent reproduction;
3. read-only environment-aware Audit Agent;
4. structured independent human review;
5. expert adjudication.

Another model saying “this looks correct” is not a substitute for available deterministic verification.

## Evidence requirements

Every evidence item should carry:

- evidence ID;
- producer and source class;
- goal ID and revision;
- environment snapshot or digest;
- obligation IDs supported or contradicted;
- result: `pass`, `fail`, or `unknown`;
- timestamp and freshness rule;
- locator or reproducible command when available.

## Freshness

Evidence is stale when a later action changes a state component within the evidence's claimed scope. A stale pass cannot certify the current state.

## Unknown handling

- `unknown` on a hard obligation never becomes pass by default;
- use `EVIDENCE_MISSING` when a permitted probe can resolve it;
- use `HUMAN_REQUIRED` when the remaining question is normative or unavailable to the system;
- use `BLOCKED` only when meaningful progress is not possible under the current authority and environment.

## Independence

The worker's claim and explanation are evidence leads, not independent proof. The same actor must not define the rule, produce the only evidence, evaluate it, and approve success.

## Sealed evaluator rule

Hidden-evaluator outputs may provide offline labels on copied snapshots. Detailed hidden feedback must not enter the worker's context in blind benchmark conditions.
