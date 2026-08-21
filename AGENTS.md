# AGENTS.md — Process-Certified Termination

## Project identity

This is an independent research project. It is not a GoalEvo subproject and does not inherit GoalEvo's research questions, datasets, hypotheses, implementation, or conclusions. It only borrows selected human–Agent governance mechanisms from an external reference charter.

## Current phase

The project is in **P0: research governance, conceptual boundaries, and Protocol Draft v0.1**.

Agents may autonomously:

- generate competing formalizations, alternatives, counterexamples, and threat cases;
- draft documentation, schemas, validators, tests, simulations, and reproducibility tools;
- perform reversible, sandboxed implementation work;
- check consistency, provenance, replayability, and accidental scope drift;
- preserve failures, disagreements, rejected options, and negative evidence.

Agents must not autonomously:

- approve any normative P0 decision;
- redefine Certified Success, corrupt success, hard process gates, or the primary estimand;
- freeze a model, harness, prompt, dataset, threshold, budget, exclusion rule, or sealed split;
- give themselves completion, Gold-label, sealed-data, merge, release, or publication authority;
- delete adverse runs or reclassify method failures for convenience;
- claim that Process-Certified Termination is effective before the relevant experiment supports that conclusion.

## Authority separation

No single actor may define success, implement the system, evaluate it, approve it, and announce success. Proposal, implementation, evaluation, and normative approval must remain visibly separable.

## Evidence rule

Model explanations are claims, not evidence. Prefer deterministic environment checks, replay, property tests, independent read-only audit, structured human review, and expert adjudication in that order when applicable.

## P0 work rule

- Link substantive work to `PCT-P0-001` or a later Work Order.
- Normative decisions live in `governance/decision-register.json` and human Decision Records.
- Recommendations stay non-effective while status is `pending-human`.
- P0 closure creates an approved development baseline for P1; it is not a main-experiment Protocol Freeze.
- Approved rules may later change only through an explicit Amendment.
