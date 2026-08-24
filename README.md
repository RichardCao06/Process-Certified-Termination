# Process-Certified Termination

> **Phase status:** P0 approved; P1 Development Pilot active  
> **Current Gate:** frozen 25-case Human Pass A; 12-hour delayed 12-case Human Pass B not yet released

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
- original 30-episode Development Pilot package;
- Human Pass A frozen after fixed-order positions 1–25 under Amendment `PCT-P1-A01`;
- five unannotated reserve Cases recorded without imputation;
- 12-case Pass-B subset and order precommitted by SHA-256;
- Amendment `PCT-P1-A02` shortens only the Pass-B minimum delay to 12 hours while preserving the same Cases, order, and commitment;
- Pass-B agreement, adjudication-packet, and author-opening verification tools implemented with synthetic tests;
- P1 Closure Report template and P2 Shadow architecture draft prepared without exposing Pass-B identities.

Still required before P1 closes:

- release Pass B no earlier than `2026-08-24T19:48:20Z`;
- 12-hour delayed, reordered, blind Human Pass B;
- intra-rater feasibility and ambiguity analysis;
- author-expectation opening after both passes and the raw A/B report are frozen;
- adjudication and P1 Closure Report.

The shorter interval carries greater memory-carryover risk than the superseded approximately 72-hour condition. Results must remain developmental and cannot be described as independent inter-rater reliability or Gold-label validation.

## Key documents

- [P0 Protocol v0.1](docs/p0/protocol-v0.1.md)
- [P1 index](docs/p1/README.md)
- [P1 Codebook v0.2](docs/p1/annotation-codebook-v0.2.md)
- [Pass-A workload Amendment](docs/p1/amendment-PCT-P1-A01.md)
- [Pass-B delay Amendment](docs/p1/amendment-PCT-P1-A02.md)
- [Pass-B analysis plan](docs/p1/pass-b-analysis-plan-v0.1.md)
- [P1 Closure Report template](docs/p1/p1-closure-report-template.md)
- [P2 Shadow architecture draft](docs/p2/p2-shadow-plugin-architecture-v0.1-draft.md)
- [P1 Exit Gate](docs/p1/p1-exit-gate.md)

## Validation

```bash
make validate
```

P1 evidence is developmental and does not establish automated Auditor accuracy or online PCT effectiveness.
