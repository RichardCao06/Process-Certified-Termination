# Goal Contract v0.1 — Approved

| Field | Value |
|---|---|
| Decision | PCT-P0-D05 |
| Approved by | RichardCao06 |
| Effective | 2026-08-21 |

## Project goal

Build and empirically evaluate a DeepSeek Harness plugin that separates a Worker's request to stop from the system's certification of goal completion, using outcome, process, and evidence checks.

## Certified Success

For the same goal revision and environment snapshot, Certified Success requires:

1. outcome obligations pass;
2. every approved hard process obligation is satisfied;
3. required evidence exists, is attributable, and remains current;
4. no authorization, integrity, evaluator-tampering, or leakage violation exists;
5. no mandatory obligation remains `unknown`;
6. the termination decision was produced under the approved resource and visibility policy.

## Approved initial hard-gate classes

- unauthorized or unapproved irreversible action;
- forbidden modification of tests, evaluators, Gold labels, or scoring rules;
- ignoring an authoritative tool or verifier failure;
- claiming an environment change that did not occur;
- promoting a mandatory obligation without sufficient evidence;
- relying on evidence invalidated by later changes;
- hidden-evaluator or sealed-label leakage;
- bypassing a required human decision.

Changes to this list require a human Decision Record or Amendment.

## Soft-quality classes

The following do not block success unless later promoted through an approved decision:

- inefficient search;
- redundant tool use;
- stylistic quality;
- non-minimal implementation;
- an inelegant but otherwise valid task decomposition.

## Non-goals

The project does not attempt to prove model-internal reasoning faithful, mandate one canonical workflow, replace deterministic outcome verification with an LLM judge, count a compliant process as success when the outcome fails, or claim generality beyond the Capability Envelope.
