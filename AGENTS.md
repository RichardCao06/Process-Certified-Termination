# AGENTS.md — Process-Certified Termination

## Project identity

This is an independent research project. It is not a GoalEvo subproject and does not inherit GoalEvo research questions, datasets, hypotheses, implementation, or conclusions. It borrows selected human–Agent governance mechanisms from an external reference charter.

## Phase status

**P0 is approved. P1 is closed and approved with limitations. P2 deterministic Shadow engineering is active under Work Order `PCT-P2-001`.**

`PCT-P2-D01` through `PCT-P2-D12` option A are approved. `PCT-P2-D13` through `PCT-P2-D18` remain Human Gates. P2 is not an online controller.

## Current Agent autonomy

Agents may autonomously:

- implement approved schemas, sidecars, deterministic checks, replay, fixtures, metrics, tests, CI, and documentation;
- run synthetic and explicitly public non-sensitive sandbox tests;
- validate exact frozen DeepSeek Harness source and public envelopes;
- preserve failures, incidents, rejected options, hashes, and migration history;
- prepare but not approve D13–D18 protocols.

Agents must not autonomously:

- approve D13–D18 or choose a substitute Worker model when the intended profile is ambiguous;
- start natural-task Worker calls before the exact Worker/task/budget/reference preflight is frozen;
- collect private/live traces;
- call a Semantic Audit Agent;
- open Reference, Human label, Author Intent, Gold, hidden-evaluator, or sealed material in the runtime lane;
- promote a descriptive check into a Hard Gate without approved provenance;
- register a hook that blocks, steers, resumes, or extends a Worker;
- mutate Goal state or completion authority;
- claim accuracy, benchmark gain, safety improvement, or effectiveness;
- start any online-intervention experiment.

## D12 Sidecar invariant

Candidate-Stop semantics come only from an explicit read-only Task/Harness sidecar. They must not be inferred from assistant prose, lack of tool calls, or `turn/end` alone.

Missing sidecar metadata is recorded as:

```text
metadata_status = MISSING
stop_scope = UNKNOWN
recovery_authority = UNKNOWN
certification_recommendation = UNDETERMINED
deterministic_decision_covered = false
```

Every active verdict remains:

```text
mode = SHADOW
applied_to_runtime = false
```

## Annotation and reference separation

- P1 raw Human passes, Agent Blind Pass, Author Intent, Agent advisory, human adjudication, and D15 correction remain separate append-only layers.
- P1 human developmental adjudication remains `not_gold=true`.
- Author Intent is not Gold.
- Runtime schemas reject Human labels, Author Intent, Reference truth, Gold, hidden evaluator, and sealed fields.
- Future Reference evaluation runs on copied snapshots only after Shadow output is frozen.

## Evidence rule

Worker explanations and structured checkpoints are observable claims, not independent proof. Prefer deterministic state, tool-result lineage, Goal revision, Evidence invalidation, replay, read-only inspection, and structured blinded human review.

## Work rule

- Link substantive work to `PCT-P2-001`.
- Normative changes require a Decision Record or Amendment.
- Active P2 decisions live in `governance/p2-decision-register-v0.2.json`; preserve the historical v0.1 pending snapshot.
- Preserve P1 limitations, `PCT-P1-I01`, and P2 reconciliation record `PCT-P2-I01`.
- Do not force-push or overwrite historical status snapshots.
- Complete unaffected reversible work when one normative sub-scope is gated.
- Bind completion claims to a remote commit SHA and successful CI run.
- P2 tests prove engineering consistency only, not natural-task accuracy or PCT effectiveness.
