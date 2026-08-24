# Process-Certified Termination

> **Phase status:** P0 approved; P1 active  
> **P1 status:** Calibration completed; post-calibration revision Gate active; four human decisions pending

This is an independent research project. Its approved near-term subject is:

> **A Process-Certified Termination Plugin for DeepSeek Harness**

The broader phrase **A General Termination Framework for LLM Agents** remains a later, evidence-dependent claim. It must not be presented as established until cross-model, cross-harness, and cross-task evidence satisfies the approved claim ladder.

## Research question

Can an additional, evidence-grounded process-certification layer improve an LLM agent harness's decision to stop—reducing premature success claims without causing harmful over-continuation—and can localized process feedback help the agent repair the task before exit?

## Approved P0 baseline

- [Protocol v0.1](docs/p0/protocol-v0.1.md)
- [Goal Contract v0.1](docs/p0/contracts/goal-contract-v0.1.md)
- [Autonomy Contract v0.1](docs/p0/contracts/autonomy-contract-v0.1.md)
- [Assurance Contract v0.1](docs/p0/contracts/assurance-contract-v0.1.md)
- [Capability Envelope v0.1](docs/p0/contracts/capability-envelope-v0.1.md)
- [P0 Closure Report](docs/p0/p0-closure-report.md)
- [Human–Agent Collaboration Protocol v0.1](docs/governance/human-agent-collaboration-protocol-v0.1.md)

Historical `-draft.md` P0 files are retained as pre-approval records and are not authoritative.

## P1 post-calibration state

P1 has completed one human Calibration pass and one context-isolated Agent Blind Pass across 12 Candidate-Stop episodes. The original passes are frozen separately. The Research Owner accepted the analysis recommendations for disputed Cases, and the project now has:

- a development adjudication layer;
- a Codebook v0.2 draft;
- strict FIT locator rules;
- separate certification-effect and control-action vocabularies;
- stop-scope and recovery-authority trace extensions;
- a 12-episode Codebook Regression Set;
- hash-verified Calibration data preservation and validation.

Excluding the taught `cal-006` example, Human and Agent agreed on `ACCEPT` versus `DO_NOT_ACCEPT` in 10 of 11 Cases. Exact Outcome and detailed mechanism-code agreement were substantially lower, so those layers remain developmental rather than Gold.

Current P1 materials:

- [P1 phase index](docs/p1/README.md)
- [Calibration Adjudication Report](docs/p1/calibration-adjudication-report-v0.1.md)
- [Post-Calibration Human Decision Pack](docs/p1/post-calibration-human-decision-pack.md)
- [Annotation Codebook v0.2 Draft](docs/p1/annotation-codebook-v0.2-draft.md)
- [Observable Trace Model v0.2 Draft](docs/p1/trace-observation-model-v0.2-draft.md)
- [P1 Exit Gate](docs/p1/p1-exit-gate.md)

## Human decisions still open

P1-D11 through P1-D14 must be resolved before the v0.2 pilot protocol can be finalized:

1. Outcome semantics for correctly escalated process-only goals;
2. First Invalid Transition decision/action/effect boundary;
3. terminal recommendation after an irreversible authorization or integrity breach;
4. recommendation policy when recovery authority is absent from the trace.

## Approved P1 development configuration

- Worker: DeepSeek-V4-Pro
- Harness: DeepSeek Harness
- Selected upstream development baseline: `deepseek-ai/deepseek-harness@141eb6fef83422698aef7a981029e843e8161534`
- Primary initial stream: highly verifiable tasks
- Semi-open tasks: exploratory until process labels and adjudication are reliable

This is a development selection, not a confirmatory Protocol Freeze.

## Deferred gates

1. independent Methods / Statistics review before confirmatory protocol freeze or approval of primary margins, thresholds, exclusions, power, and sample design;
2. a separate Independent Custodian before any held-out or sealed evaluator material is created, accessed, or unsealed.

## Validate the repository

```bash
make validate
```

Materialize the reviewed Calibration bundle when direct access to derived JSON artifacts is needed:

```bash
make materialize-calibration
```

## Governance principle

Humans retain normative authority and responsibility. Agents may generate alternatives, formalizations, code, tests, simulations, and audits, but may not silently redefine success, approve their own normative changes, or declare unverified work complete.
