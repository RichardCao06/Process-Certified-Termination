# PCT Protocol v0.1 — Draft

| Field | Value |
|---|---|
| Project | Process-Certified Termination |
| Near-term system | A Process-Certified Termination Plugin for DeepSeek Harness |
| Version | 0.1-draft |
| Date | 2026-08-21 |
| Phase | P0 |
| Status | Agent draft; human approval pending |
| Normative authority | Human Research Owner and assigned human leads |

## 1. Purpose

This protocol defines the research scope, concepts, authority boundaries, evidence rules, and claim limits for studying whether an additional process-certification layer can improve an LLM agent harness's termination decisions.

P0 creates a research contract. It does **not** establish that the proposed method is effective.

## 2. Project identity and claim ladder

### 2.1 Near-term claim

The first implementation and causal evaluation target is:

> **A Process-Certified Termination Plugin for DeepSeek Harness**

The project may claim only configuration-specific findings until external-validity studies are completed.

### 2.2 Later claim, conditional on evidence

The name **A General Termination Framework for LLM Agents** may be used as a research aspiration, not an established result. A broader claim requires, at minimum:

- a second worker model on the same harness;
- the same primary worker model on a second harness;
- evidence from both highly verifiable and semi-open task streams;
- stable harness-neutral interfaces;
- a documented Capability Envelope and heterogeneity analysis.

### 2.3 Non-claims

This project does not claim that:

- process evaluation is a new idea;
- a fluent chain-of-thought is a reliable audit log;
- one prescribed workflow is the only valid process;
- process compliance implies outcome correctness;
- a model's lack of tool use proves goal completion;
- a single model–harness result generalizes to all agents.

## 3. Research object

The object of audit is the **observable execution trajectory**, not private internal reasoning:

- task and goal obligations;
- accepted observations and environment state;
- tool calls, arguments, outcomes, and failures;
- state transitions and evidence references;
- completion proposals and stop candidates;
- independent verifier and auditor outputs;
- repair feedback and subsequent actions.

Private or hidden chain-of-thought is neither required nor assumed faithful.

## 4. Core definitions

- **Candidate Stop:** a point at which the worker or harness would naturally end the current unit of work.
- **Outcome Verdict:** assessment of the final environment/output state against outcome obligations.
- **Process Verdict:** assessment of whether hard process constraints and state transitions are supported.
- **Evidence State:** current, attributable evidence linked to a precise goal revision and environment snapshot.
- **First Invalid Transition:** the earliest state promotion or decision that lacks required evidence or violates a hard precondition.
- **Proposed Complete:** a worker claim requesting certification; it is not success.
- **Certified Success:** outcome obligations pass, no hard process violation is present, required evidence is sufficient and current, and the goal revision has not changed.
- **False Accept:** the controller accepts completion although the reference evaluator or adjudicated ground truth says the task is incomplete or corrupt.
- **False Continue:** the controller forces further work although the reference evaluator says the task was already acceptably complete.
- **Corrupt Success:** an outcome that passes a result check while violating a hard procedural, integrity, authorization, or evidence requirement.

## 5. Research questions and hypotheses

| RQ | Draft hypothesis | Intended conclusion if supported |
|---|---|---|
| RQ1 — Information increment | PCT-H1: process features improve prediction of hidden failure, corrupt success, or human rejection after controlling for outcome information. | Process trajectories contain independent information about trustworthy completion. |
| RQ2 — Representation | PCT-H2: Goal–Evidence or State-Transition representations outperform raw transcripts under matched cost. | Structure, not merely more context, drives process-audit value. |
| RQ3 — Automated auditing | PCT-H3: the auditor reaches a preregistered agreement level with adjudicated human labels for hard gates and First Invalid Transition. | A bounded subset of process certification is automatable. |
| RQ4 — Exit calibration | PCT-H4: PCT lowers False Accept while False Continue remains within a preregistered non-inferiority margin. | PCT improves termination calibration for the tested configuration. |
| RQ5 — Repair value | PCT-H5: localized process feedback improves repair conversion under matched compute. | Process auditing is useful as a control signal, not only an evaluator. |
| RQ6 — System benefit | PCT-H6: Certified Success improves under equal budget or an accepted cost envelope. | Harness-level certification improves actual task completion. |
| RQ7 — External validity | PCT-H7: the primary direction holds for at least one second model and one second harness. | The Capability Envelope may be broadened. |

The classification of these hypotheses as primary, secondary, methodological, or external-validity claims is a pending human decision.

## 6. Four draft contracts

The four contracts are separate so that success, permission, evidence, and proven scope cannot be collapsed into one score or prompt.

- [Goal Contract](contracts/goal-contract-v0.1-draft.md)
- [Autonomy Contract](contracts/autonomy-contract-v0.1-draft.md)
- [Assurance Contract](contracts/assurance-contract-v0.1-draft.md)
- [Capability Envelope](contracts/capability-envelope-v0.1-draft.md)

## 7. Candidate initial configuration

Pending human freeze, the recommended mechanism-development configuration is:

- Worker model: **DeepSeek-V4-Pro**;
- Harness: **DeepSeek Harness**;
- Candidate upstream baseline: commit `141eb6fef83422698aef7a981029e843e8161534` (`dsh@0.1.0-rc.8` release merge);
- Primary initial task stream: **Research Stream V — highly verifiable tasks**;
- Research Stream S — semi-open, multi-path tasks: exploratory until hard/soft process labels are shown to be reliable.

The commit is a candidate baseline, not frozen by this draft.

## 8. Research streams

### 8.1 Research Stream V — highly verifiable tasks

Used to estimate causal effects where final state can be checked programmatically. Outcome verifiers remain the primary truth source; process information is tested for incremental value, diagnosis, and repair.

### 8.2 Research Stream S — semi-open, multi-path tasks

Used to study process integrity, evidence sufficiency, and human diagnostic support where no complete deterministic oracle exists. Multiple valid paths must be allowed. Soft process quality must not be turned into a hard stop condition without reliable human agreement.

## 9. Data and sealing boundary

At minimum, data must be separated into:

- development traces;
- validation traces;
- human-label development data;
- held-out evaluation data;
- sealed tests and hidden evaluator information.

Experimental Agents, online auditors, and repair controllers must not access sealed labels, hidden failure locations, other method outputs, or evaluator internals. Official hidden evaluators may label copied stop snapshots offline, but their detailed results must not be fed back to the worker in blind benchmark mode.

## 10. Authority and role separation

- Humans define goals, hard violations, scientific claims, metrics, risk, and publication language.
- Builder Agents draft formalizations, code, tests, simulations, and documentation.
- Red-Team Agents attack assumptions, metrics, isolation, and gaming resistance.
- Audit Agents inspect read-only evidence and consistency; they do not define Gold labels.
- Experimental Agents perform benchmark tasks and may propose completion; they cannot certify it.
- Independent Custodians control sealed data, hashes, and release timing.

See [Role and Authority Map](role-and-authority-map.md).

## 11. Primary decision rule draft

The default conceptual rule is:

```text
CERTIFIED_SUCCESS :=
  outcome_pass
  AND all_hard_process_obligations_satisfied
  AND evidence_sufficient_and_current
  AND no_integrity_or_authorization_violation
  AND goal_revision_unchanged
```

An `unknown` hard obligation does not become a pass. It produces `EVIDENCE_MISSING` or `HUMAN_REQUIRED`, depending on whether a lawful probe remains available.

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

## 13. P0 exit conditions

P0 closes only when:

1. all blocking human decisions have a recorded disposition;
2. project claim, non-goals, and claim ladder are approved;
3. the four contracts are approved or amended;
4. primary endpoint families and comparison structure are assigned;
5. hard versus soft process semantics are approved;
6. roles and sealed-data authority are assigned;
7. the collaboration protocol is adopted;
8. rejected options and accepted risks are preserved;
9. `make validate` passes;
10. the Research Owner signs the P0 Exit Gate.

## 14. Allowed conclusion after P0

Only the following conclusion is allowed:

> The project has an approved, auditable protocol for beginning P1.

No conclusion about Process-Certified Termination effectiveness is permitted.

## 15. Amendment

After Protocol Freeze, any change to claims, primary comparisons, process hard gates, sealed boundaries, model/harness configuration, or failure handling requires an Amendment Record containing timing, reason, affected data, approver, and old/new hashes.
