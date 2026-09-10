# Process-Certified Termination

> **Phase status:** P0 approved; P1 closed with limitations; P2 deterministic Shadow protocol preflight active  
> **Current state:** D01-D18 option A approved; natural-task pilot BLOCKED pending exact Worker identity, profile-derived caps, and independent Reference custody

This independent research project studies whether an evidence-grounded process-certification layer can improve an LLM Agent Harness's termination decision.

The approved near-term subject remains:

> **A Process-Certified Termination Plugin for DeepSeek Harness**

A general LLM-Agent termination framework remains an evidence-dependent later claim.

## P1 state

P1 is complete and merged. It produced the Candidate-Stop Codebook v0.2-pilot, annotation and adjudication schemas, developmental Human/Agent passes, final developmental labels, a Reliability Matrix, Taxonomy Migration, Closure Report, and passed Exit Gate. P1 did not test automated Auditor accuracy or online effectiveness.

## P2 active state

Human decisions `PCT-P2-D01` through `PCT-P2-D18` selected option A and are preserved in append-only Decision Records. The D12 read-only sidecar, exact frozen DeepSeek Harness conformance, 20+10 synthetic regression, and deterministic replay remain active.

D13-D18 have materialized the first natural-task protocol:

```text
20 public non-sensitive tasks
10 highly verifiable + 10 semi-open
3 repetitions per task
60 planned trajectories
first Candidate Stop = primary unit
fixed base caps = 30 minutes / 20 model requests / 50 tool calls / 2 Candidate Stops
Semantic Auditor = disabled
mode = SHADOW
applied_to_runtime = false
```

The protocol is not authorized to run yet. Current Preflight blockers:

```text
PCT-P2-PF-IDENTITY-01  exact DeepSeek V4-Pro provider/model/profile identity missing
PCT-P2-PF-BUDGET-01    profile-derived retry/token/context/output/monetary caps missing
PCT-P2-PF-REFERENCE-01 two independent semi-open raters and adjudication custody unassigned
```

No live Worker call, natural-task trajectory, Reference opening, private trace, Semantic Auditor call, Steering, blocking, Goal mutation, online intervention, production deployment, or effectiveness claim is authorized.

## Current protocol documents

- [Natural-task Shadow Pilot Protocol v0.1](docs/p2/p2-natural-task-shadow-pilot-protocol-v0.1.md)
- [Preflight Input Request v0.1](docs/p2/p2-preflight-input-request-v0.1.md)
- [D12 Sidecar Contract](docs/p2/p2-candidate-stop-sidecar-contract-v0.1.md)
- [P2 Work Order v0.2](docs/p2/work-order-PCT-P2-001-v0.2.md)
- [P2 index](docs/p2/README.md)

## Validation

```bash
make validate
```

Current P2 outputs are engineering and developmental protocol artifacts. They do not establish natural-task Auditor accuracy, independent human reliability, cross-Harness generality, safety improvement, benchmark gain, or online PCT effectiveness.
