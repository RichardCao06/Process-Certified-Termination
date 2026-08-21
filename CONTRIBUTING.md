# Contributing

## Current project phase

The repository is in **P0**. Contributions should improve research governance, definitions, decision clarity, traceability, or deterministic validation. They must not present unapproved drafts as frozen protocol or claim empirical effectiveness.

## Change process

1. Link every change to a Work Order or Decision ID.
2. Use a feature branch; do not put substantive changes directly on `main`.
3. Separate normative changes from implementation changes when practical.
4. Run `make validate`.
5. State what changed, what did not change, tests run, risks, and unresolved human decisions.

## Authority boundary

Agents may draft and implement reversible work. Human approval is required for research scope, primary claims, hard process violations, metrics, statistical thresholds, role assignments, sealed-data rules, model/harness freezes, and external publication.

## Failure preservation

Do not delete failed runs, rejected alternatives, negative findings, or protocol disagreements. Corrections should be additive and traceable.
