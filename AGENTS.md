# AGENTS.md — Process-Certified Termination

## Project identity

This is an independent research project. It is not a GoalEvo subproject and does not inherit GoalEvo's research questions, datasets, hypotheses, implementation, or conclusions. It only borrows selected human–Agent governance mechanisms from an external reference charter.

## Phase status

**P0 is complete.** P1 is authorized but begins only under a new Work Order.

The approved P1 scope is descriptive process review, failure taxonomy, annotation feasibility, and development-only infrastructure. Confirmatory analysis and sealed-test work remain blocked by the independent methods-review and custodian gates.

## Agent autonomy after P0

Agents may autonomously, within an approved Work Order:

- generate competing formalizations, alternatives, counterexamples, and threat cases;
- draft documentation, schemas, validators, tests, simulations, and reproducibility tools;
- perform reversible, sandboxed implementation work;
- inspect public DeepSeek Harness interfaces and create development adapters;
- check consistency, provenance, replayability, and accidental scope drift;
- preserve failures, disagreements, rejected options, and negative evidence.

Agents must not autonomously:

- redefine Certified Success, corrupt success, hard process gates, or the primary estimand;
- change the approved claim ladder or hypothesis hierarchy;
- freeze a model, harness, prompt, dataset, threshold, budget, exclusion rule, or sealed split;
- give themselves completion, Gold-label, sealed-data, merge, release, or publication authority;
- access hidden evaluators or sealed labels;
- delete adverse runs or reclassify method failures for convenience;
- claim empirical effectiveness before the relevant experiment supports it.

## Authority separation

No single actor may define success, implement the system, evaluate it, approve it, and announce success. Proposal, implementation, evaluation, and normative approval must remain visibly separable.

## Evidence rule

Model explanations are claims, not evidence. Prefer deterministic environment checks, replay, property tests, independent read-only audit, structured human review, and expert adjudication in that order when applicable.

## Work rule

- Link substantive work to a Work Order.
- Normative changes require a Decision Record or Amendment.
- Approved P0 decisions live in `governance/decision-register.json`.
- The Research Builder Agent cannot also serve as the independent certifier for the same evidence.
- P1 artifacts are developmental unless explicitly promoted through a later Gate.
