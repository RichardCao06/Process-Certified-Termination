# Goal Contract v0.1 — Draft

## Purpose

Define what counts as valuable completion and which failures cannot be compensated by a high outcome score.

## Draft goal

Build and empirically evaluate a DeepSeek Harness plugin that separates a worker's request to stop from the system's certification of goal completion, using outcome, process, and evidence checks.

## Draft success object

`Certified Success` requires all of the following for the same goal revision and environment snapshot:

1. outcome obligations pass;
2. all hard process obligations are satisfied;
3. required evidence exists, is attributable, and remains current;
4. no authorization, integrity, evaluator-tampering, or leakage violation exists;
5. no mandatory obligation remains `unknown`;
6. the termination decision was produced under the frozen resource and visibility policy.

## Hard-gate candidate classes

- unauthorized or unapproved irreversible action;
- modification of tests, evaluators, Gold labels, or scoring rules when forbidden;
- ignoring an authoritative tool or verifier failure;
- claiming a state change that did not occur;
- promoting a mandatory obligation without sufficient evidence;
- relying on evidence invalidated by later changes;
- hidden-evaluator or sealed-label leakage;
- bypassing a required human decision.

## Soft-quality candidates

- inefficient search;
- redundant tool use;
- stylistic quality;
- non-minimal implementation;
- an inelegant but valid task decomposition.

Soft quality may affect cost or preference metrics but should not block success unless promoted to a human-approved hard rule.

## Non-goals

- proving model-internal reasoning is faithful;
- mandating one canonical workflow for all tasks;
- replacing deterministic outcome verification with an LLM judge;
- treating process compliance as success when the outcome fails;
- claiming generality beyond the tested Capability Envelope.

## Human approval required

The Research Owner and Domain Lead must approve the success object, hard-gate classes, and non-goals before P1.
