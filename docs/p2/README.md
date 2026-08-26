# P2 — Non-intervening Process-Certification Shadow

P2 is active under Work Order `PCT-P2-001`. D01–D12 option A are approved and materialized. The current implementation provides append-only Event/Evidence records, deterministic replay, a frozen hard/descriptive policy, exact DeepSeek Harness source/envelope conformance, and an explicit read-only Candidate-Stop sidecar.

Current verified engineering regression:

```text
20 normal/boundary + 10 malformed/leakage
30/30 PASS
live model calls = 0
applied_to_runtime = false
```

Open Human Gate: `PCT-P2-D13` through `PCT-P2-D18`, covering the exact Worker identity, public task catalog, sample/repeats, budgets, offline Reference lane, and whether the first natural pilot remains deterministic-only.

Still prohibited: private traces, Reference opening, Semantic Auditor calls, Worker calls before protocol preflight, Steering, blocking, resume, Goal mutation, online intervention, production deployment, and effectiveness claims.
