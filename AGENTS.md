# AGENTS.md — Process-Certified Termination

## Project identity

This is an independent research project. It is not a GoalEvo subproject and
does not inherit GoalEvo's research questions, datasets, hypotheses,
implementation, or conclusions. It borrows selected human–Agent governance
mechanisms from an external reference charter.

## Phase status

**P0 is approved. P1 is closed and approved with limitations. P2 reversible
Shadow foundation work is active under Work Order `PCT-P2-001`.**

P2 is not an online controller. The current authorized scope is A0–A2:
analysis, drafting, schemas, synthetic fixtures, replay code, deterministic
checks, tests, and CI. P2-D01 through P2-D07 remain Human Gates.

## P2 Agent autonomy

Agents may autonomously:

- draft competing P2 protocols, policies, schemas, threat models, and fixtures;
- implement an observable-only event adapter contract;
- implement append-only event and Evidence storage;
- build Candidate-Stop snapshots and deterministic replay;
- implement candidate checks whose hard-versus-descriptive status remains policy-gated;
- test stale Evidence, Goal revision, malformed traces, leakage, and valid negative controls;
- run synthetic and explicitly public sandbox tests;
- preserve failures, rejected options, incidents, and migration history;
- maintain hashes and traceability.

Agents must not autonomously:

- approve PCT-P2-D01 through PCT-P2-D07;
- collect private/live Harness traces before the data policy is approved;
- call a semantic Audit Agent before the exact model/tool/budget Gate;
- reveal Human labels, Fixture Author Intent, Gold, hidden evaluator, or sealed material to Worker or Shadow runtime;
- promote a diagnostic check into a Hard Gate without approved provenance;
- register a live hook that blocks, steers, resumes, or extends a Worker;
- mutate Goal state or completion authority;
- run a natural-task Shadow measurement before protocol freeze;
- propose benchmark gains, safety improvement, or online effectiveness;
- start any online-intervention experiment.

## Shadow-only invariant

Every current P2 verdict artifact must state:

```text
mode = SHADOW
applied_to_runtime = false
```

Before a human-frozen P2 policy exists, the foundation may emit replayable findings but must keep:

```text
verdict_status = POLICY_PENDING
labels_emitted = false
```

## Annotation and reference separation

- P1 raw Human passes, Agent Blind Pass, Author Intent, Agent advisory, human adjudication, and D15 correction remain separate append-only layers.
- P1 human developmental adjudication was complete but remains `not_gold=true`.
- Author Intent is not Gold.
- Runtime P2 schemas reject Human labels, Author Intent, reference truth, Gold, hidden evaluator, and sealed-test fields.
- A future reference evaluator must run in a separate offline lane after Shadow outputs are frozen.

## Evidence rule

Worker explanations and structured checkpoints are observable claims, not independent proof. Prefer deterministic state, tool result lineage, Goal revision, Evidence invalidation, replay, read-only inspection, and structured human review.

## Work rule

- Link substantive work to `PCT-P2-001`.
- Normative changes require a Decision Record or Amendment.
- P2 decisions live in `governance/p2-decision-register-v0.1.json`.
- Preserve the P1 limitations and `PCT-P1-I01`.
- Do not overwrite historical P0/P1 status snapshots.
- Complete unaffected reversible work when one normative sub-scope is gated.
- P2 foundation tests prove engineering consistency only, not Auditor accuracy or PCT effectiveness.
