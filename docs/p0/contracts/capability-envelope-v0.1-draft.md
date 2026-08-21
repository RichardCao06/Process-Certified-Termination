# Capability Envelope v0.1 — Draft

## Current evidence status

No empirical effectiveness evidence exists yet. The current envelope describes only the intended development scope.

## Candidate development envelope

| Dimension | Candidate scope | Status |
|---|---|---|
| Harness | DeepSeek Harness | Not frozen |
| Upstream baseline | `141eb6fef83422698aef7a981029e843e8161534` | Candidate |
| Worker model | DeepSeek-V4-Pro | Candidate |
| Primary task stream | Highly verifiable tasks | Candidate |
| Secondary task stream | Semi-open, multi-path tasks | Exploratory later |
| Termination mode | Shadow first, online intervention later | Planned |
| Process data | observable events, state transitions, evidence links | Draft policy |
| Hidden evaluator | blind, offline labeling only | Draft policy |

## Explicit exclusions

No claim currently covers:

- other DeepSeek Harness commits;
- other models or providers;
- Claude Code, Codex, or other harnesses;
- high-stakes production deployment;
- private chain-of-thought monitoring;
- tasks without observable evidence;
- irreversible actions without human approval.

## Expansion rule

The envelope expands only after preregistered external-validity tests. Directional consistency alone does not prove universal generality; heterogeneity, cost, failure modes, and task-specific limits must be reported.
