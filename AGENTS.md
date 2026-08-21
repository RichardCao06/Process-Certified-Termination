# AGENTS.md — Process-Certified Termination

## Project identity

This is an independent research project. It is not a GoalEvo subproject and does not inherit GoalEvo's research questions, datasets, hypotheses, implementation, or conclusions. It only borrows selected human–Agent governance mechanisms from an external reference charter.

## Phase status

**P0 is approved. P1 is active under Work Order `PCT-P1-001`.**

The current P1 branch develops descriptive process review, failure taxonomy, annotation feasibility, observable trace schemas, and reversible development tooling. Confirmatory, online-intervention, held-out, and sealed-test work remains out of scope.

## P1 Agent autonomy

Agents may autonomously at A0–A2:

- generate competing taxonomy structures, definitions, exclusions, examples, and counterexamples;
- implement reversible schemas, validators, lints, fixtures, mapping prototypes, and analysis utilities;
- inspect public interfaces from the selected DeepSeek Harness commit;
- run engineering smoke tests and synthetic simulations;
- identify ambiguity, leakage, gaming, and valid-alternative-path risks;
- preserve failures, disagreements, rejected options, and migration history.

Agents must not autonomously:

- approve PCT-P1-D01 through PCT-P1-D10;
- promote a new code into a hard certification gate;
- define empirical Gold labels from deterministic lints or fixture-author expectations;
- access held-out or sealed evaluator material;
- attach the draft linter as an online controller and report benchmark gains;
- freeze agreement thresholds, sample size, primary statistics, or a production Auditor;
- require private chain-of-thought or treat Worker explanations as proof;
- claim the taxonomy is exhaustive, reliable, or effective before the human pilot.

## Annotation separation

- Observable trajectories must not contain Gold labels, hidden evaluator outputs, reference truth, or hidden failure locations.
- Synthetic fixture expectations must be labeled `FIXTURE_AUTHOR` and described as engineering expectations.
- Human annotations must be preserved independently before adjudication.
- Audit Agent output cannot define its own Gold standard.

## Evidence rule

Model explanations and structured decision checkpoints are claims. Prefer deterministic state, replay, current evidence lineage, independent read-only inspection, and structured human adjudication.

## Work rule

- Link substantive work to a Work Order.
- Normative changes require a Decision Record or Amendment.
- P1 human decisions live in `governance/p1-decision-register.json`.
- Maintain a negative control for valid alternative paths.
- Do not reject structurally valid failure trajectories; lint and annotation operate after structural validation.
- P1 artifacts remain developmental until the P1 Exit Gate is signed.
