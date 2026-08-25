# Process-Certified Termination

> **Phase status:** P0 approved; P1 closed with limitations; P2 Shadow foundation active  
> **Current Gate:** Human decisions `PCT-P2-D01` through `PCT-P2-D07`

This independent research project studies whether an evidence-grounded process-certification layer can improve an LLM Agent Harness's termination decision.

The approved near-term subject remains:

> **A Process-Certified Termination Plugin for DeepSeek Harness**

A general LLM-Agent termination framework remains an evidence-dependent later claim.

## P1 state

P1 is complete and merged. It produced:

- Candidate-Stop Codebook v0.2-pilot;
- observable trace, annotation, and adjudication schemas;
- Calibration Human and context-isolated Agent passes;
- a 25-case Human Pass A and a reordered 12-case Human Pass B;
- developmental adjudication and D15 append-only correction;
- a final Reliability Matrix and Taxonomy Migration;
- a Closure Report and passed P1 Exit Gate.

P1 concluded that a compact core layer is suitable for a later non-intervening Shadow study, while several fields remain human-review-only or exploratory. P1 did not test automated Auditor accuracy or online effectiveness.

## P2 state

P2 has started under a **reversible A2 foundation authorization**.

Implemented foundation:

- observable-only DeepSeek Harness event normalization contract;
- append-only canonical event log;
- Evidence Ledger and invalidation lineage;
- Candidate-Stop Snapshot construction;
- deterministic descriptive-check registry;
- policy-pending Shadow envelopes;
- deterministic replay and hashes;
- hidden/reference input rejection;
- static runtime-mutation guard;
- synthetic clean and stale-evidence fixtures;
- validation and unit tests.

Not authorized:

- live/private trace collection;
- semantic Audit Agent calls;
- reference-evaluator opening;
- natural-task Shadow measurement;
- online blocking, steering, or Goal mutation;
- effectiveness claims.

## Human decision pack

- [P2 Human Decision Pack](docs/p2/p2-human-decision-pack-v0.1.md)
- [P2 Work Order](docs/p2/work-order-PCT-P2-001-v0.1.md)
- [P2 index](docs/p2/README.md)

## Key P1 documents

- [P1 Closure Report](docs/p1/p1-closure-report-v0.1.md)
- [P1 Codebook v0.2](docs/p1/annotation-codebook-v0.2.md)
- [P1 Taxonomy Migration](docs/p1/p1-taxonomy-migration-v0.1.md)
- [P1 Final Exit Gate](docs/p1/p1-exit-gate-v0.2-final.md)

## Validation

```bash
make validate
```

Current P2 outputs are engineering artifacts. They do not establish automated Auditor accuracy, independent human reliability, cross-Harness generality, or online PCT effectiveness.
