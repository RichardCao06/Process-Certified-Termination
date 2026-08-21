# Autonomy Contract v0.1 — Draft

## Purpose

Define who may observe, act, evaluate, and approve each state transition.

## P0 autonomy levels

- Research Builder Agent: A0–A1 — generate alternatives and drafts; no normative approval.
- Red-Team Agent: A0–A1 — attack definitions and propose mitigations; cannot approve its own proposals.
- Audit Agent: A0–A1 — read-only consistency checks; cannot define Gold or hard gates.
- Experimental Agent: not active in P0 normative decisions.

## Later runtime authority draft

| Actor | May do | Must not do |
|---|---|---|
| Worker / Experimental Agent | inspect allowed environment, call allowed tools, submit `PROPOSED_COMPLETE`, respond to repair feedback | access hidden labels, commit certified completion, edit evaluator policy |
| Process Auditor | read permitted trace and environment evidence, produce structured verdict | mutate task state, access sealed root-cause labels, define hard rules |
| Outcome Verifier | evaluate final state using frozen logic | reveal hidden evaluator details to worker |
| Termination Controller | apply frozen decision policy and commit allowed runtime terminal states | change the policy during a run |
| Builder Agent | implement plugin, schemas, tests, adapters | approve scientific claims or sealed release |
| Human authorities | approve scope, risks, hard rules, metrics, freezes, publication | silently alter frozen protocol without Amendment |

## Completion authority

Recommended invariant:

```text
Worker -> PROPOSED_COMPLETE
Trusted Certifier -> COMPLETE
```

The worker never upgrades its own proposal into certified success.

## Escalation triggers

Automatic human escalation is required when a change would alter success semantics, hard gates, evaluator visibility, sealed data, main endpoints, risk ownership, or an irreversible real-world action.
