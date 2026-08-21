# Autonomy Contract v0.1 — Approved

| Field | Value |
|---|---|
| Decisions | PCT-P0-D06, PCT-P0-D08, PCT-P0-D10 |
| Approved by | RichardCao06 |
| Effective | 2026-08-21 |

## Completion authority

```text
Worker / Experimental Agent -> PROPOSED_COMPLETE
Trusted Certification Layer -> COMPLETE
```

A Worker cannot certify its own terminal success.

## Runtime roles

| Actor | May do | Must not do |
|---|---|---|
| Worker / Experimental Agent | inspect allowed environment, call allowed tools, submit `PROPOSED_COMPLETE`, respond to repair feedback | access hidden labels, commit `COMPLETE`, edit evaluator policy |
| Process Auditor | read permitted trace and evidence, inspect allowed environment, produce a structured verdict | mutate task state, define hard rules, access sealed root-cause labels |
| Outcome Verifier | evaluate final state using frozen logic | reveal hidden evaluator details to Worker |
| Termination Controller | apply the frozen decision policy and commit allowed terminal states | alter the policy during a run |
| Builder Agent | implement plugin, schemas, tests, and adapters | approve scientific claims or sealed release |
| Human authorities | approve scope, risk, hard rules, metrics, freezes, and publication | silently alter frozen rules without Amendment |

## P1 Agent autonomy

Agents may operate at A0–A2 on reversible development tasks under an approved Work Order. They may not enter confirmatory, sealed, release, or publication authority.

## Human escalation

Escalation is mandatory for changes to success semantics, hard gates, primary endpoints, evaluator visibility, permissions, sealed data, irreversible actions, role authority, or publication claims.
