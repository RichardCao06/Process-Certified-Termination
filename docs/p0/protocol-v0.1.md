# PCT Protocol v0.1 — Approved P0 Baseline

| Field | Value |
|---|---|
| Project | Process-Certified Termination |
| Near-term system | A Process-Certified Termination Plugin for DeepSeek Harness |
| Version | 0.1 |
| Approved | 2026-08-21 |
| Approver | RichardCao06, Research Owner |
| Decision source | PR #1 comment 5364822055 |
| Status | P0 approved; P1 development authorized |

## 1. Purpose

This protocol defines the research scope, concepts, authority boundaries, evidence rules, and claim limits for studying whether an additional process-certification layer can improve an LLM agent harness's termination decisions.

P0 creates an approved research contract. It does **not** establish that the proposed method is effective.

## 2. Project identity and claim ladder

### 2.1 Approved near-term claim

The first implementation and causal evaluation target is:

> **A Process-Certified Termination Plugin for DeepSeek Harness**

Findings remain configuration-specific until external-validity studies are completed.

### 2.2 Conditional later claim

**A General Termination Framework for LLM Agents** is a research aspiration, not an established result. A broader claim requires, at minimum:

- a second worker model on the same harness;
- the primary worker model on a second harness;
- evidence from highly verifiable and semi-open task streams;
- stable harness-neutral interfaces;
- a documented Capability Envelope and heterogeneity analysis.

### 2.3 Non-claims

The project does not claim that:

- process evaluation is a new idea;
- a fluent chain-of-thought is a reliable audit log;
- one prescribed workflow is the only valid process;
- process compliance implies outcome correctness;
- lack of tool use proves goal completion;
- one model–harness result generalizes to all agents.

## 3. Research object

The audit object is the **observable execution trajectory**, not private internal reasoning:

- task and goal obligations;
- accepted observations and environment state;
- tool calls, arguments, outcomes, and failures;
- state transitions and evidence references;
- completion proposals and candidate stops;
- independent verifier and auditor outputs;
- repair feedback and subsequent actions.

Private or hidden chain-of-thought is neither required nor assumed faithful.

## 4. Core definitions

- **Candidate Stop:** a point at which the Worker or harness would naturally end the current work unit.
- **Outcome Verdict:** assessment of final state against outcome obligations.
- **Process Verdict:** assessment of hard process constraints and evidence-supported state transitions.
- **Evidence State:** attributable evidence linked to a precise goal revision and environment snapshot.
- **First Invalid Transition:** the earliest state promotion or decision lacking required evidence or violating a hard precondition.
- **Proposed Complete:** a Worker request for certification; it is not success.
- **Certified Success:** outcome obligations pass, no hard process violation exists, evidence is sufficient/current, and the goal revision is unchanged.
- **False Accept:** completion is accepted although reference truth says the task is incomplete or corrupt.
- **False Continue:** further work is forced although reference truth says the task was already acceptably complete.
- **Corrupt Success:** an outcome passes a result check while violating a hard procedural, integrity, authorization, or evidence rule.

## 5. Approved research questions and hierarchy

| RQ | Hypothesis | Classification |
|---|---|---|
| RQ1 — Information increment | PCT-H1: process features improve prediction of hidden failure, corrupt success, or human rejection after controlling for outcome information. | Foundational |
| RQ2 — Representation | PCT-H2: Goal–Evidence or State-Transition representations outperform raw transcripts under matched cost. | Method development |
| RQ3 — Automated auditing | PCT-H3: the Auditor reaches frozen agreement thresholds with adjudicated human labels for hard gates and First Invalid Transition. | Method development |
| RQ4 — Exit calibration | PCT-H4: PCT lowers False Accept while False Continue remains within a frozen non-inferiority margin. | Primary confirmatory system claim |
| RQ5 — Repair value | PCT-H5: localized process feedback improves Repair Conversion under matched compute. | Secondary confirmatory |
| RQ6 — System benefit | PCT-H6: Certified Success improves under equal budget or an approved cost envelope. | Secondary confirmatory |
| RQ7 — External validity | PCT-H7: the primary direction holds for at least one second model and one second harness. | External validity |

Exact margins, sample sizes, exclusions, power, and statistical thresholds remain unfrozen until independent methods review.

## 6. Approved contracts

The project keeps success, permission, proof, and proven scope separate:

- [Goal Contract v0.1](contracts/goal-contract-v0.1.md)
- [Autonomy Contract v0.1](contracts/autonomy-contract-v0.1.md)
- [Assurance Contract v0.1](contracts/assurance-contract-v0.1.md)
- [Capability Envelope v0.1](contracts/capability-envelope-v0.1.md)

## 7. Approved P1 development configuration

- Worker model: **DeepSeek-V4-Pro**;
- Harness: **DeepSeek Harness**;
- selected upstream development baseline: `141eb6fef83422698aef7a981029e843e8161534`;
- primary initial task stream: highly verifiable tasks;
- semi-open, multi-path tasks: exploratory until hard/soft process labels are reliable.

This selection is not a confirmatory Protocol Freeze. Any later baseline change must be visible and versioned.

## 8. Research streams

### 8.1 Stream V — highly verifiable tasks

Outcome verifiers remain the primary truth source. Process information is tested for incremental prediction, diagnosis, termination calibration, and repair.

### 8.2 Stream S — semi-open, multi-path tasks

Used to study process integrity, evidence sufficiency, and human diagnostic support where no complete deterministic oracle exists. Multiple valid paths must remain possible. A soft preference cannot become a hard stop condition without reliable human agreement and a new decision.

## 9. Data and sealing boundary

Data must be separated into development, validation, human-label development, held-out evaluation, and sealed evaluator/test partitions.

Experimental Agents, online Auditors, and repair controllers must not access sealed labels, hidden failure locations, other condition outputs, or evaluator internals. Hidden evaluators may label copied candidate-stop snapshots offline; detailed results never return to the Worker in blind benchmark mode. Oracle feedback is reported only as a separately labeled upper bound.

## 10. Human and Agent authority

- Humans define goals, hard constraints, scientific claims, metrics, risk, and publication language.
- Builder Agents draft formalizations, code, tests, simulations, and documentation.
- Red-Team Agents attack assumptions, metrics, isolation, and gaming resistance.
- Audit Agents inspect read-only evidence and consistency; they do not define Gold labels.
- Experimental Agents execute tasks and may submit `PROPOSED_COMPLETE`; they cannot commit `COMPLETE`.
- Independent Custodians control sealed data, hashes, and release timing.

P1 uses the approved minimum viable human-role separation in the [Role and Authority Map](role-and-authority-map.md). Confirmatory and sealed work is blocked until the deferred independent roles are satisfied.

## 11. Approved completion rule

```text
CERTIFIED_SUCCESS :=
  outcome_pass
  AND all_hard_process_obligations_satisfied
  AND evidence_sufficient_and_current
  AND no_integrity_or_authorization_violation
  AND goal_revision_unchanged
```

An `unknown` hard obligation never becomes a pass. It produces `EVIDENCE_MISSING` when a lawful probe remains, or `HUMAN_REQUIRED` when the unresolved question is normative or unavailable.

## 12. Termination states

The controller must distinguish:

- `CERTIFIED`
- `REPAIR_REQUIRED`
- `EVIDENCE_MISSING`
- `BLOCKED`
- `HUMAN_REQUIRED`
- `NO_PROGRESS`
- `BUDGET_EXHAUSTED`
- `FAILED`

Stopping a loop is not synonymous with success.

## 13. P1 authorization

P1 may perform descriptive process review, failure-taxonomy development, annotation-feasibility studies, schema/trace prototypes, and reversible development work.

P1 may not make confirmatory effectiveness claims, access sealed evaluators, or present the system as a general LLM-agent framework.

## 14. Amendment

Any change to approved claims, primary endpoint family, hypothesis hierarchy, hard process gates, trace policy, completion authority, sealed boundaries, or role-gate requirements requires an Amendment Record. Confirmatory configuration, thresholds, exclusions, and statistical rules require a later independent methods review and freeze.
