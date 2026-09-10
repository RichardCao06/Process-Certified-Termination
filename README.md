# Process-Certified Termination

> **Phase status:** P0 approved; P1 closed with limitations; P2 deterministic Shadow protocol preflight active  
> **Current state:** D01-D21 option A approved; the two-fixture engineering rerun passed no-model validation and awaits human Environment review; the primary natural-task pilot remains unauthorized.

This independent research project studies whether an evidence-grounded process-certification layer can improve an LLM Agent Harness's termination decision.

The approved near-term subject remains:

> **A Process-Certified Termination Plugin for DeepSeek Harness**

A general LLM-Agent termination framework remains an evidence-dependent later claim.

## P1 state

P1 is complete and merged. It produced the Candidate-Stop Codebook v0.2-pilot, annotation and adjudication schemas, developmental Human/Agent passes, final developmental labels, a Reliability Matrix, Taxonomy Migration, Closure Report, and passed Exit Gate. P1 did not test automated Auditor accuracy or online effectiveness.

## P2 active state

Human decisions `PCT-P2-D01` through `PCT-P2-D21` selected option A and are preserved in append-only Decision Records. The D12 read-only sidecar, exact frozen DeepSeek Harness conformance, 20+10 synthetic regression, and deterministic replay remain active. See [active status v0.8](governance/p2-status-v0.8.json) and [D21 execution protocol](docs/p2/p2-d21-approved-execution-v0.1.md).

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

The primary protocol is not authorized to run yet. The engineering-only profile and caps have been frozen; semi-open Reference custody records the approved developmental single-rater downgrade. These updates do not establish independent inter-rater reliability.

D19 and D20 failed during configuration before a model request. Their evidence is preserved. The official DSH patch passed a credential-free boot check. D21-A now permits exactly one attempt of the original two engineering fixtures, each capped at 30 CNY, behind the human GitHub Environment gate. The new driver must pass its own no-model check before access to the credential. Results will be appended as v0.4 regardless of success or failure; no quality rerun follows automatically.

The actual D21 driver and all 105 repository tests passed remote validation at `13dddc89d7562aad755401d2c8037bb3db5d98b2`. [Readiness evidence](governance/p2-d21-execution-readiness-v0.1.json) binds the report, artifact, commit, and CI runs. [The protected engineering job](https://github.com/RichardCao06/Process-Certified-Termination/actions/runs/34433128526) awaits `RichardCao06` Environment review; no D21 model turn has occurred in this readiness snapshot.

No primary natural-task trajectory, Reference opening, private trace, Semantic Auditor call, Steering, blocking, Goal mutation, online intervention, production deployment, or effectiveness claim is authorized.

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
