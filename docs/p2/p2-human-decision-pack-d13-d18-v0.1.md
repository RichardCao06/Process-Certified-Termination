# PCT P2 Human Decision Pack — D13 through D18

D12 has made Candidate-Stop semantics observable through an explicit read-only sidecar. The next step would be the first **public, non-sensitive natural-task Shadow pilot**. That pilot is not authorized until the following six decisions are frozen.

## PCT-P2-D13 — Worker identity and model freeze

### A — One exact Worker configuration for the first pilot **(recommended)**

Use the Research Owner's designated DeepSeek Worker profile. Before the first run, freeze and record the exact Harness commit, provider route, model identifier returned by the configured profile, profile/config digest, system prompt digest, tool catalog digest, reasoning/sampling settings, and retry policy. Aliases may not silently move; if the exact identity cannot be recorded, the run stops.

This option does not authorize a substitute model. If the intended DeepSeek V4-Pro profile is unavailable or resolves ambiguously, Agent must return a smaller configuration Gate rather than choose another model.

### B — Multiple Worker models in the first pilot

Broader comparison, but model effects become entangled with Sidecar and deterministic-Auditor feasibility.

### C — Use whatever model is current at run time

Fast, but not reproducible and vulnerable to silent provider drift.

**Recommendation:** A.

## PCT-P2-D14 — Public task composition

### A — Freeze 20 public, non-sensitive tasks **(recommended)**

Use 10 highly verifiable tasks and 10 semi-open tasks. Publish or record each task text, source/license, Goal Contract, hard obligations, allowed tools, deterministic validators where applicable, and a SHA-256 catalog before any Worker run. No task may contain private repository or personal data.

### B — Use only highly verifiable tasks

Cleaner evaluation, but does not test the semi-open setting that motivates process review.

### C — Use open-ended ad hoc tasks selected during execution

Not reproducible and vulnerable to selection bias.

**Recommendation:** A.

## PCT-P2-D15 — Pilot sample and analysis unit

### A — 20 tasks × 3 independent repetitions = 60 trajectories **(recommended)**

The first Candidate Stop in each trajectory is the primary analysis unit. A maximum of two Candidate Stops may be captured per trajectory; later stops are exploratory and may not inflate the primary denominator. Seeds, order, failures, retries, and exclusions are frozen before the run.

### B — One run per task

Cheaper, but cannot quantify run-to-run variability.

### C — Adaptive repetitions until results appear stable

Introduces outcome-dependent stopping.

**Recommendation:** A.

## PCT-P2-D16 — Per-trajectory resource budget

### A — Fixed conservative budget **(recommended)**

Freeze before execution:

```text
wall-clock cap: 30 minutes
model-request cap: 20
Tool-call cap: 50
Candidate-Stop capture cap: 2
retry policy: frozen with Worker profile
context/output/token and monetary caps: exact values recorded from the selected profile before run; no adaptive extension
```

Infrastructure failure and method failure remain separate; no failed run is silently rerun or deleted.

### B — Larger flexible budget controlled by the Agent

May reduce budget exits, but makes results and stopping rules less comparable.

### C — No fixed budget

Not reproducible.

**Recommendation:** A.

## PCT-P2-D17 — Offline Reference lane

### A — Hybrid isolated Reference evaluation **(recommended)**

For highly verifiable tasks, use frozen deterministic validators. For semi-open tasks, use two independent blinded human judgments on the copied Candidate-Stop packet, followed by recorded adjudication for substantive disagreement. Shadow verdicts and hashes are frozen before Reference opening. Author Intent and Agent Advisory are not Gold and are unavailable to the Worker and runtime Shadow layer.

If a second independent human annotator cannot be secured, the semi-open part must be explicitly downgraded to developmental single-rater evidence rather than reported as independent reliability.

### B — One unblinded human reviewer

Operationally easier, but vulnerable to anchoring and provides no inter-rater evidence.

### C — Use an LLM judge as the Reference

Would conflate the system under study with an unvalidated semantic evaluator.

**Recommendation:** A.

## PCT-P2-D18 — Semantic Audit Agent in the first natural pilot

### A — Keep the first natural pilot deterministic-only **(recommended)**

Measure Event/Sidecar completeness, deterministic decision coverage, replay equality, false accept, false continue, abstention/undetermined, latency, and cost before adding a semantic model. Residual cases that deterministic checks cannot classify become the evidence base for a later exact-model Semantic Auditor Gate.

### B — Add a read-only semantic model now

May improve coverage but introduces judge variance and leakage surface before deterministic gaps are measured.

### C — Use the Worker model as its own semantic Auditor

Maximizes correlated error and weakens independence.

**Recommendation:** A.

## Reply template

Accepting all recommendations:

```text
PCT-P2-D13: A
PCT-P2-D14: A
PCT-P2-D15: A
PCT-P2-D16: A
PCT-P2-D17: A
PCT-P2-D18: A

Intended Worker profile/display name: DeepSeek V4-Pro
Additional constraints or amendments:
```

Approval of D13–D18 authorizes protocol materialization and preflight only. Actual Worker calls may begin only after the preflight records an unambiguous exact provider/model/profile identity and the frozen task catalog, budgets, and Reference custody are present. It never authorizes online intervention.
