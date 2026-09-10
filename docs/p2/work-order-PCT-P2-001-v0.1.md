# Work Order PCT-P2-001 — DeepSeek Harness Process-Certification Shadow Foundation

## Authorization status

**PARTIALLY AUTHORIZED — A0/A1/A2 reversible foundation only.**

The Research Owner instructed the Agent on 2026-08-25 to begin P2, route
human-reserved decisions to the Research Owner, and autonomously advance the
remaining work. This authorizes analysis, drafting, schemas, synthetic
fixtures, deterministic replay code, tests, and CI integration.

It does **not** authorize:

- collection of live or private Harness traces;
- a semantic Audit Agent call;
- opening or using hidden/reference evaluator material;
- blocking, steering, resuming, or extending a Worker;
- changing Goal completion authority;
- a natural-task Shadow measurement run;
- an effectiveness or safety claim.

## Goal

Build and validate a non-intervening foundation that can:

1. normalize supplied observable DeepSeek Harness-style events;
2. preserve an append-only canonical event log;
3. bind Evidence to Goal revision and observable invalidation events;
4. construct a Candidate-Stop Snapshot;
5. run deterministic descriptive checks;
6. emit a policy-pending Shadow envelope;
7. reproduce the same snapshot and findings by replay;
8. prove by static validation that the package does not call runtime mutation APIs.

The first scientific question remains:

> Can observable Harness data support deterministic, independently replayable
> Candidate-Stop auditing without relying on the Worker's completion claim?

## Non-goals

- no online controller;
- no `agent.steer()` or equivalent mutation;
- no benchmark-gain claim;
- no production deployment;
- no sealed-test run;
- no claim that current deterministic checks are exhaustive;
- no automatic promotion of a P1 diagnostic code into a P2 Hard Gate;
- no use of `valid_alternative_path` before its representation is repaired.

## Inputs from P1

- P1 closure status and report;
- Candidate-Stop Annotation Codebook v0.2-pilot;
- final P1 Reliability Matrix;
- final Taxonomy Migration;
- P1 hard-gate provenance;
- P1 limitations, including `PCT-P1-I01`.

P1's completed developmental human adjudication remains `not_gold=true`; its
status was complete, with 8 required cases and 20/20 required fields, but it is
not a runtime input to P2.

## Deliverables

### Completed in the foundation PR

1. P2 Work Order and status record;
2. P2-D01–D07 decision register and human decision pack;
3. observable event, Evidence, snapshot, verdict, and replay schemas;
4. append-only event log;
5. append-only Evidence Ledger plus invalidation lineage;
6. pure DeepSeek Harness event normalization contract;
7. Candidate-Stop Snapshot builder;
8. deterministic descriptive-check registry;
9. policy-gated Shadow Auditor;
10. deterministic replay and CLI;
11. hidden/reference input guard;
12. runtime-mutation static guard;
13. clean and stale-evidence fixtures;
14. foundation validator and unit tests;
15. Draft P2 Exit Gate.

### Blocked by human decisions

- frozen endpoint scope;
- data retention and privacy policy;
- hard-versus-descriptive check policy;
- semantic Audit Agent configuration;
- reference evaluator isolation protocol;
- live sample/model/Harness/budget freeze;
- evidence threshold before an online-intervention study may be proposed.

## Acceptance criteria for A2 foundation

- supplied events are append-only, uniquely identified, and strictly ordered;
- replay reproduces input, event-log, snapshot, verdict, and bundle digests;
- stale Evidence and wrong-revision Evidence cannot silently count as current;
- Worker claims remain observable data, never independent proof;
- hidden, Gold, sealed, human-label, and Fixture Author fields are rejected;
- policy-pending mode emits findings but no P1-style verdict labels;
- a frozen policy must cite approved human decisions before labels are enabled;
- every output states `mode=SHADOW` and `applied_to_runtime=false`;
- no package source calls a forbidden runtime-mutation API;
- clean and adverse fixtures are preserved;
- `make validate` remains green.

## Stages

### P2.0 — Foundation and adapter contract

Current authorized stage. Uses synthetic supplied envelopes only.

### P2.1 — Evidence Ledger and replay

May proceed after the foundation validates. Still synthetic/public data only
unless P2-D02 authorizes otherwise.

### P2.2 — Frozen deterministic Shadow policy

Requires P2-D01 and P2-D03. No semantic model and no online intervention.

### P2.3 — Optional semantic Auditor

Requires the later exact-model configuration Gate under P2-D04.

### P2.4 — Natural-task Shadow measurement

Requires all relevant P2 decisions, a frozen protocol, exact Worker/Harness
versions, sample and budget, privacy controls, and reference isolation.

### Later phase — Online intervention protocol proposal

Requires P2-D07 and separate human authorization. P2 itself cannot deploy an
online controller.

## Human decisions

The blocking normative questions are `PCT-P2-D01` through `PCT-P2-D07`.
See `p2-human-decision-pack-v0.1.md`.

## Owner and autonomy

```text
Research Owner: RichardCao06
Agent autonomy now: A0–A2
Formal runtime authority: NONE
Work Order status: PARTIALLY AUTHORIZED
Date: 2026-08-25
```
