# Process-Certified Termination

> **Current phase:** P0 — research governance, conceptual boundaries, and Protocol Draft v0.1  
> **Current status:** Agent-owned P0 drafting is complete; human normative decisions are pending.

This is an independent research project. Its near-term subject is:

> **A Process-Certified Termination Plugin for DeepSeek Harness**

The broader phrase **A General Termination Framework for LLM Agents** is a later, evidence-dependent research claim. It must not be used as an established result until cross-model, cross-harness, and cross-task evidence satisfies a frozen protocol.

## Research question

Can an additional, evidence-grounded process-certification layer improve an LLM agent harness's decision to stop—reducing premature success claims without causing harmful over-continuation—and can localized process feedback help the agent repair the task before exit?

## P0 deliverables

- [Protocol Draft v0.1](docs/p0/protocol-v0.1-draft.md)
- [Human Decision Pack](docs/p0/human-decision-pack.md)
- [Decision Register](docs/p0/decision-register.md)
- [Goal / Autonomy / Assurance / Capability contract drafts](docs/p0/contracts/)
- [Threat Model](docs/p0/threat-model.md)
- [Role and Authority Map](docs/p0/role-and-authority-map.md)
- [Causal Model](docs/p0/causal-model.md)
- [Literature Baseline](docs/p0/literature-baseline.md)
- [P0 Exit Gate](docs/p0/p0-exit-gate.md)

## Repository status

The P0 documents are **drafts**, not approved policy. The project must not enter P1 until every blocking item in `governance/decision-register.json` has an authorized human disposition and the P0 gate is signed.

## Validate the P0 package

```bash
make validate
```

The validator checks required artifacts, decision ownership, phase status, cross-file identifiers, candidate upstream commit format, and accidental project-identity leakage.

## Governance principle

Humans retain normative authority and responsibility. Agents may generate alternatives, formalizations, code, tests, simulations, and audits, but may not silently redefine success, approve their own normative changes, or declare unverified work complete.
