# Process-Certified Termination

> **Phase status:** P0 approved; P1 closed with limitations; P2 deterministic Shadow protocol preflight active  
> **Current state:** D01-D21 option A approved; D21-A01 moves the unused two-fixture attempt to local macOS execution. Local credentials are pending; the primary pilot remains unauthorized.

This independent research project studies whether an evidence-grounded process-certification layer can improve an LLM Agent Harness's termination decision.

The approved near-term subject remains:

> **A Process-Certified Termination Plugin for DeepSeek Harness**

A general LLM-Agent termination framework remains an evidence-dependent later claim.

## P1 state

P1 is complete and merged. It produced the Candidate-Stop Codebook v0.2-pilot, annotation and adjudication schemas, developmental Human/Agent passes, final developmental labels, a Reliability Matrix, Taxonomy Migration, Closure Report, and passed Exit Gate. P1 did not test automated Auditor accuracy or online effectiveness.

## P2 active state

Human decisions `PCT-P2-D01` through `PCT-P2-D21` selected option A and are preserved in append-only Decision Records. The D12 read-only sidecar, exact frozen DeepSeek Harness conformance, 20+10 synthetic regression, and deterministic replay remain active. See [active status v0.9](governance/p2-status-v0.9.json) and [local D21 execution](docs/p2/p2-d21-local-execution-v0.1.md).

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

D19 and D20 failed during configuration before a model request. Their evidence is preserved. The official DSH patch passed a credential-free boot check. D21-A permits exactly one attempt of the original two engineering fixtures, each capped at 30 CNY. The user subsequently requested local execution: D21-A01 replaces the GitHub Environment review step with the local runner and preserves the same scope. Results will be appended as v0.4 regardless of success or failure; no quality rerun follows automatically.

The former cloud route passed all 105 tests and actual driver boot at `13dddc89d7562aad755401d2c8037bb3db5d98b2`; [that readiness snapshot](governance/p2-d21-execution-readiness-v0.1.json) is preserved. Its waiting model job was cancelled and its generation workflow disabled before any model request. Use `./scripts/run-p2-local.sh` for local execution or add `--no-model` for credential-free validation. The API key is entered invisibly in the terminal; it is not saved or passed to the Worker subprocess.

[Local readiness evidence](governance/p2-d21-local-readiness-v0.1.json) binds `de4738e26845da5427d686c6c5ec4c4c8e2bd08d` to 113 passing repository tests, successful macOS no-model CI, and actual local filesystem/network confinement and Harness boot checks. The local API key remains the only missing execution input in this snapshot; no D21 model request has occurred.

For the requested local env-file workflow, fill `~/.config/pct/deepseek.env` with `DEEPSEEK_API_KEY=...`, then use `python3 scripts/run_p2_d21_env.py`. [Env-file instructions](docs/p2/p2-local-env-file-v0.1.md) describe the private configuration and unchanged execution boundaries. The file is outside the repository and is never included in evidence.

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
