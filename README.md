# Process-Certified Termination

> **Phase status:** P0 approved; P1 Development Pilot active  
> **Current Gate:** 30-episode Human Pass A

This independent research project studies whether an evidence-grounded process-certification layer can improve an LLM Agent Harness's termination decision.

The approved near-term subject is:

> **A Process-Certified Termination Plugin for DeepSeek Harness**

A general LLM-Agent termination framework remains an evidence-dependent later claim.

## P1 state

Completed:

- process taxonomy and observable trace foundation;
- Human Calibration Pass 1;
- context-isolated Agent Blind Pass;
- Human–Agent comparison and development adjudication;
- P1 decisions D01–D14;
- Codebook / Schema v0.2 Pilot;
- 12/12 post-calibration semantic regression;
- 30-episode blinded Development Pilot Pass A package.

Still required before P1 closes:

- Human Pass A;
- delayed reordered blind Human Pass B;
- intra-rater feasibility analysis;
- adjudication and P1 Closure Report.

## Key documents

- [P0 Protocol v0.1](docs/p0/protocol-v0.1.md)
- [P1 index](docs/p1/README.md)
- [P1 Codebook v0.2](docs/p1/annotation-codebook-v0.2.md)
- [Development Pilot Pass A](docs/p1/development-pilot-pass-a.md)
- [P1 Exit Gate](docs/p1/p1-exit-gate.md)

## Validation

```bash
make validate
make materialize-development-pilot
```

P1 evidence is developmental and does not establish automated Auditor accuracy or online PCT effectiveness.
