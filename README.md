# Process-Certified Termination

> **Phase status:** P0 approved; P1 closed with limitations; P2 deterministic Shadow engineering active  
> **Current Gate:** Human decisions `PCT-P2-D13` through `PCT-P2-D18`

This independent research project studies whether an evidence-grounded process-certification layer can improve an LLM Agent Harness's termination decision.

The approved near-term subject remains:

> **A Process-Certified Termination Plugin for DeepSeek Harness**

A general LLM-Agent termination framework remains an evidence-dependent later claim.

## P1 state

P1 is complete and merged. It produced the Candidate-Stop Codebook v0.2-pilot, annotation and adjudication schemas, developmental Human/Agent passes, final developmental labels, a Reliability Matrix, Taxonomy Migration, Closure Report, and passed Exit Gate. P1 did not test automated Auditor accuracy or online effectiveness.

## P2 active state

Human decisions `PCT-P2-D01` through `PCT-P2-D12` selected option A and are materialized as append-only Decision Records.

Implemented and policy-frozen:

- observable-only DeepSeek Harness event normalization;
- append-only Event Log and Evidence Ledger;
- Candidate-Stop Snapshot and deterministic replay;
- P1 Reliability-Matrix label layering;
- approved deterministic hard-versus-descriptive checks;
- DeepSeek Harness freeze at `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`;
- source/envelope conformance validation against the exact frozen checkout;
- explicit read-only Candidate-Stop sidecar;
- missing-sidecar `UNKNOWN` / `UNDETERMINED` behavior;
- 20 normal/boundary + 10 malformed/leakage synthetic regression;
- recursive hidden/reference input rejection and static runtime-mutation guard.

Current controlled regression:

```text
30/30 PASS
live model calls = 0
natural-task runs = 0
applied_to_runtime = false
```

## Current Human Gate

- [D13–D18 Natural Pilot Decision Pack](docs/p2/p2-human-decision-pack-d13-d18-v0.1.md)
- [D12 Sidecar Contract](docs/p2/p2-candidate-stop-sidecar-contract-v0.1.md)
- [P2 Work Order v0.2](docs/p2/work-order-PCT-P2-001-v0.2.md)
- [P2 index](docs/p2/README.md)

Natural-task Worker calls, Semantic Auditor calls, private traces, Reference opening, Steering, blocking, Goal mutation, online intervention, production deployment, and effectiveness claims remain unauthorized.

## Key P1 documents

- [P1 Closure Report](docs/p1/p1-closure-report-v0.1.md)
- [P1 Codebook v0.2](docs/p1/annotation-codebook-v0.2.md)
- [P1 Taxonomy Migration](docs/p1/p1-taxonomy-migration-v0.1.md)
- [P1 Final Exit Gate](docs/p1/p1-exit-gate-v0.2-final.md)

## Validation

```bash
make validate
```

Current P2 outputs are engineering and developmental protocol artifacts. They do not establish natural-task Auditor accuracy, independent human reliability, cross-Harness generality, safety improvement, benchmark gain, or online PCT effectiveness.
