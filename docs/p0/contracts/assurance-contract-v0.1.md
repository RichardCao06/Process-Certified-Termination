# Assurance Contract v0.1 — Approved

| Field | Value |
|---|---|
| Decisions | PCT-P0-D05, PCT-P0-D07, PCT-P0-D09 |
| Approved by | RichardCao06 |
| Effective | 2026-08-21 |

## Evidence hierarchy

Prefer, when applicable:

1. deterministic program or authoritative environment state;
2. property tests, replay, differential checks, or independent reproduction;
3. read-only environment-aware Audit Agent;
4. structured independent human review;
5. expert adjudication.

Another model saying “this looks correct” does not replace available deterministic verification.

## Evidence record

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

Evidence becomes stale when a later action changes a state component inside the evidence's claimed scope. A stale pass cannot certify the current state.

## Reasoning-data policy

The project records observable events, actions, tool outcomes, state changes, evidence links, and short structured decision checkpoints. It does not require private or hidden chain-of-thought. Worker explanations are evidence leads and claims, not independent proof.

## Unknown handling

- `unknown` on a hard obligation never becomes pass by default;
- use `EVIDENCE_MISSING` when a permitted probe can resolve it;
- use `HUMAN_REQUIRED` when the remaining question is normative or unavailable;
- use `BLOCKED` only when meaningful progress is impossible under current authority and environment.

## Blind hidden-evaluator rule

Hidden evaluators may label copied candidate-stop snapshots offline. Detailed hidden failures must not enter Worker or online Auditor context. Oracle feedback is allowed only as a separately labeled upper-bound experiment.
