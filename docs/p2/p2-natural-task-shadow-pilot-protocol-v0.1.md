# PCT P2 Natural-Task Shadow Pilot Protocol v0.1

**Status:** MATERIALIZED FOR PREFLIGHT — NOT AUTHORIZED TO RUN  
**Work Order:** `PCT-P2-001`  
**Human decisions:** `PCT-P2-D13` through `PCT-P2-D18`, option A  
**Approval source:** PR #3 comment `5420758863` at `2026-08-26T04:51:11Z`

## 1. Purpose

This protocol prepares the first public, non-sensitive natural-task measurement of the deterministic PCT Shadow layer. It does not authorize an online controller, Worker steering, a Semantic Audit Agent, private trace collection, Reference opening before Shadow freeze, or any effectiveness claim.

## 2. Frozen design

- 20 public project-authored synthetic tasks;
- 10 highly verifiable and 10 semi-open tasks;
- 3 independent repetitions per task, totaling 60 planned trajectories;
- first Candidate Stop per trajectory as the primary analysis unit;
- at most two Candidate Stops captured; the second is exploratory only;
- fixed order, seeds, failure handling, and exclusions before any result;
- deterministic-only Shadow evaluation in the first pilot.

## 3. Fixed base budget

```text
wall-clock cap: 30 minutes
model-request cap: 20
tool-call cap: 50
Candidate-Stop capture cap: 2
```

The exact retry policy, context window, maximum output, token cap, and monetary cap are profile-derived fields and remain unresolved until the exact Worker profile is frozen. No adaptive budget extension is permitted.

## 4. Worker identity rule

The intended display name carried from the accepted recommendation is `DeepSeek V4-Pro`. A display name is not a reproducible identity. Before any run, the repository must record the exact provider route, returned model identifier/revision, profile or configuration digest, system-prompt digest, tool-catalog digest, reasoning/sampling settings, and retry policy.

No Agent may silently substitute a different model. If exact identity cannot be recorded, the pilot remains blocked and a smaller Worker-configuration Gate is required.

## 5. Task and schedule freeze

The public task catalog is `data/p2/natural-pilot/public-task-catalog-v0.1.json`. Its digest is:

```text
32d0bd6854196fdbac4e5a91ffcfb4fa5bd57f6c0949102919bc5ce0b5742a5c
```

The fixed 60-trajectory schedule is `data/p2/natural-pilot/run-schedule-v0.1.json`. Its digest is:

```text
b422d8cf43dd2093f995fa0cb62705ab5dba3a2af0a0da8110051753ac6b349f
```

Tasks and ordering may not be replaced, reordered, or excluded based on observed Worker or Shadow results.

## 6. Reference isolation

For highly verifiable tasks, the copied frozen Candidate-Stop packet is evaluated by an independent rerun of the deterministic validator. For semi-open tasks, two different blinded humans judge independently before seeing each other, the Shadow verdict, or adjudication. Substantive disagreement is adjudicated and preserved.

Reference evaluation begins only after the Candidate-Stop packet and Shadow verdict digest are frozen. Reference output never flows back into the Worker or runtime Shadow lane.

## 7. Failure handling

Infrastructure failure and method failure are recorded separately. Failed trajectories are never silently deleted or rerun. A replacement trajectory requires an append-only Amendment and a new trajectory identifier. Later Candidate Stops cannot inflate the primary denominator.

## 8. Metrics

The pilot measures Sidecar completeness, metadata availability, deterministic decision coverage, replay equality, False Accept, False Continue, abstention/UNDETERMINED, latency, requests, tools, tokens, and monetary cost. These are developmental measurements. They do not establish safety improvement, benchmark gain, cross-Harness generality, or online PCT effectiveness.

## 9. Current Preflight result

```text
status: BLOCKED
PCT-P2-PF-IDENTITY-01: exact Worker identity missing
PCT-P2-PF-BUDGET-01: profile-derived retry/token/context/output/monetary caps missing
PCT-P2-PF-REFERENCE-01: two independent semi-open raters and adjudication custody unassigned
live Worker model calls: 0
natural-task runs: 0
Reference packets opened: 0
Semantic Auditor calls: 0
```

Only protocol preparation, deterministic validation, sanitized profile-manifest ingestion, and Reference-role assignment are authorized at this state.
