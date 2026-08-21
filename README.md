# Process-Certified Termination

> **Phase status:** P0 complete and approved on 2026-08-21  
> **Next authorized phase:** P1 — descriptive process review, failure taxonomy, annotation feasibility, and development-only infrastructure

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
- [Human Decision Register](docs/p0/decision-register.md)
- [P0 Closure Report](docs/p0/p0-closure-report.md)
- [Human–Agent Collaboration Protocol v0.1](docs/governance/human-agent-collaboration-protocol-v0.1.md)
- [Threat Model](docs/p0/threat-model.md)
- [Causal Model](docs/p0/causal-model.md)
- [Claim Ladder](docs/p0/claim-ladder.md)
- [Literature Baseline](docs/p0/literature-baseline.md)

Files ending in `-draft.md` are retained as historical pre-approval records and are not authoritative.

## Approved P1 development configuration

- Worker: DeepSeek-V4-Pro
- Harness: DeepSeek Harness
- Selected upstream development baseline: `deepseek-ai/deepseek-harness@141eb6fef83422698aef7a981029e843e8161534`
- Primary initial stream: highly verifiable tasks
- Semi-open tasks: exploratory until process labels and adjudication are reliable

This is a P1 development selection, not a confirmatory Protocol Freeze.

## Deferred gates

P1 may proceed, but two later gates remain mandatory:

1. independent Methods / Statistics review before confirmatory protocol freeze or approval of primary margins, thresholds, exclusions, power, and sample design;
2. a separate Independent Custodian before any held-out or sealed evaluator material is created, accessed, or unsealed.

## Validate the repository

```bash
make validate
```

The validator checks required artifacts, human decision authority, P0 closure, role-gate consistency, cross-file identifiers, candidate upstream commit format, project independence, JSON validity, and local Markdown links.

## Governance principle

Humans retain normative authority and responsibility. Agents may generate alternatives, formalizations, code, tests, simulations, and audits, but may not silently redefine success, approve their own normative changes, or declare unverified work complete.
