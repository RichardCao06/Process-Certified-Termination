# AGENTS.md — Process-Certified Termination

## Project identity

This is an independent research project. It is not a GoalEvo subproject and does not inherit GoalEvo research questions, datasets, hypotheses, implementation, or conclusions. It borrows selected human-Agent governance mechanisms from an external reference charter.

## Phase status

**P0 is approved. P1 is closed with limitations. P2 deterministic Shadow protocol preflight is active under Work Order `PCT-P2-001`.**

`PCT-P2-D01` through `PCT-P2-D18` option A are approved. The first natural-task protocol is materialized but BLOCKED pending exact Worker identity/profile-derived caps and independent Reference custody. P2 is not an online controller.

## Current Agent autonomy

Agents may autonomously:

- implement approved schemas, sidecars, deterministic checks, replay, public fixtures, metrics, tests, CI, and documentation;
- materialize the approved 20-task/60-trajectory protocol without calling a model;
- run offline deterministic validators and protocol consistency checks;
- ingest a sanitized exact profile manifest and record non-secret hashes;
- preserve failures, incidents, rejected options, hashes, and migration history.

Agents must not autonomously:

- choose a substitute Worker model when `DeepSeek V4-Pro` is ambiguous or unavailable;
- start natural-task Worker calls before `scripts/validate_p2_natural_pilot_preflight.py` reports PASS;
- fill unresolved provider/model/profile, retry, token, context, output, or monetary fields by guesswork;
- assign the same person to both independent semi-open rater roles;
- collect private/live traces;
- call a Semantic Audit Agent;
- open Reference, Human label, Author Intent, Gold, hidden-evaluator, or sealed material in the runtime lane;
- register a hook that blocks, steers, resumes, or extends a Worker;
- mutate Goal state or completion authority;
- claim accuracy, benchmark gain, safety improvement, or effectiveness;
- start any online-intervention experiment.

## D12 Sidecar invariant

Candidate-Stop semantics come only from an explicit read-only Task/Harness sidecar. They must not be inferred from assistant prose, lack of tool calls, or `turn/end` alone. Missing metadata remains `UNKNOWN` / `UNDETERMINED`.

Every active verdict remains:

```text
mode = SHADOW
applied_to_runtime = false
```

## D13-D18 pilot invariant

The task catalog, run schedule, first-Candidate-Stop primary unit, fixed base caps, failure policy, Reference ordering, and deterministic-only Auditor scope are frozen before any result. Task substitutions, adaptive repetitions, silent reruns, denominator changes, and post-result budget extensions are prohibited.

The active blockers are:

```text
PCT-P2-PF-IDENTITY-01
PCT-P2-PF-BUDGET-01
PCT-P2-PF-REFERENCE-01
```

## Annotation and reference separation

- P1 raw Human passes, Agent Blind Pass, Author Intent, Agent advisory, human adjudication, and D15 correction remain separate append-only layers.
- P1 human developmental adjudication remains `not_gold=true`.
- Runtime schemas reject Human labels, Author Intent, Reference truth, Gold, hidden evaluator, and sealed fields.
- Reference evaluation uses copied Candidate-Stop packets only after Shadow output is frozen.

## Work rule

- Link substantive work to `PCT-P2-001`.
- Normative changes require a Decision Record or Amendment.
- Active P2 decisions live in `governance/p2-decision-register-v0.3.json`; preserve v0.1 and v0.2.
- Do not force-push or overwrite historical status snapshots.
- Complete unaffected reversible work when one sub-scope is blocked.
- Bind completion claims to a remote commit SHA and successful CI run.
- P2 tests prove engineering consistency only, not natural-task accuracy or PCT effectiveness.
