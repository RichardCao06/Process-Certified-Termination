# Process-Certified Termination

> **Phase status:** P0 approved; P1 active  
> **P1 status:** Agent-owned taxonomy/annotation foundation complete; human decisions and annotation pilot pending

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

## P1 development foundation

- [P1 phase index](docs/p1/README.md)
- [Human Decision Pack](docs/p1/human-decision-pack.md)
- [Failure Taxonomy v0.1 Draft](docs/p1/failure-taxonomy-v0.1-draft.md)
- [Annotation Codebook v0.1 Draft](docs/p1/annotation-codebook-v0.1-draft.md)
- [Annotation Feasibility Protocol](docs/p1/annotation-feasibility-protocol-v0.1-draft.md)
- [Observable Trace Model](docs/p1/trace-observation-model-v0.1-draft.md)
- [DeepSeek Harness event mapping](docs/p1/deepseek-harness-event-mapping.md)
- [P1 Exit Gate](docs/p1/p1-exit-gate.md)

P1 includes dependency-free structural validation, deterministic candidate lints, exploratory annotation-agreement tooling, and controlled synthetic fixtures. These are development instruments, not evidence that the taxonomy is reliable or that PCT improves task performance.

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

Useful P1 development commands:

```bash
python3 scripts/lint_trajectory.py data/p1/synthetic/stale-evidence.json
python3 scripts/annotation_agreement.py \
  tests/fixtures/p1/annotator-a.jsonl \
  tests/fixtures/p1/annotator-b.jsonl
```

## Governance principle

Humans retain normative authority and responsibility. Agents may generate alternatives, formalizations, code, tests, simulations, and audits, but may not silently redefine success, approve their own normative changes, or declare unverified work complete.
