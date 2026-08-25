# P1 Red-Team Review

## Main attacks considered

### 1. Taxonomy becomes the answer key

**Risk:** code definitions smuggle benchmark-specific failure locations into the Auditor.

**Mitigation:** use abstract mechanism classes, keep task-specific labels outside Worker-visible artifacts, and prohibit held-out/sealed traces in P1.

### 2. One preferred workflow becomes a hard process rule

**Risk:** unfamiliar but valid paths are labeled failures.

**Mitigation:** multi-path policy, `valid_alternative_path`, explicit exclusions, and a clean non-canonical fixture.

### 3. Deterministic lints masquerade as Gold

**Risk:** rules authored by the Builder validate themselves.

**Mitigation:** lints are named candidate findings; empirical labels require blinded human passes and preserved disagreement.

### 4. Hard-gate inflation

**Risk:** every defect is marked hard, driving False Continue toward one.

**Mitigation:** `hard_gate_codes` are restricted to P0-approved classes; other codes remain descriptive.

### 5. Forced exact localization

**Risk:** annotators invent a precise First Invalid Transition to satisfy the schema.

**Mitigation:** permit `RANGE` and `UNKNOWN`; report uncertainty rather than hiding it.

### 6. Worker explanation is treated as causal evidence

**Risk:** structured checkpoints reward plausible narratives.

**Mitigation:** checkpoints are self-reports, never independent proof; evidence classes and citations remain separate.

### 7. Annotation feasibility is overstated

**Risk:** fixture-author agreement with deterministic lints is reported as human reliability.

**Mitigation:** synthetic smoke tests are engineering only; P1 completion requires the human pilot and ambiguity report.

### 8. Leakage through filenames, errors, or annotation files

**Risk:** the Experimental Agent sees expected codes or fixture labels.

**Mitigation:** observable trajectory validation rejects prohibited fields; annotations are separate; later adapters require access-control tests.

### 9. Agreement metrics conceal prevalence or label-set problems

**Risk:** one number appears strong while important labels disagree.

**Mitigation:** report field-level agreement, multi-label Jaccard, raw confusion, ambiguity rates, and qualitative disagreement classes. No P1 threshold is confirmatory.

### 10. P1 quietly becomes an online effectiveness experiment

**Risk:** a linter is attached to the Worker and benchmark gains are interpreted causally.

**Mitigation:** P1 explicitly excludes online intervention, held-out data, and effectiveness claims. Online work requires a later Work Order and Gate.
