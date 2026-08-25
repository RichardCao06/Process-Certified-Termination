# P1 Closure Report v0.1 — Draft for Final Human Gate

## Status

**Empirical and engineering work complete; P1 closure is blocked by PCT-P1-D15 and final Research Owner approval.**

P1 asks whether Candidate-Stop outcome, process, evidence, control, and localization judgments can be represented and annotated with enough developmental stability to support a later Shadow Auditor study. P1 does **not** test online PCT effectiveness.

## 1. Frozen inputs

- Codebook: `0.2-pilot`
- Pass A raw annotations SHA-256: `d561b442053293c94c13db6ff5c49af6ef187fa12cff351f0e94dbb1e92364b8`
- Pass B raw annotations SHA-256: `ff5bb76b5b168dd546f61f2dd065f2091ed841e6a2335c014e2a3f1441a5ed5f`
- Pass B episodes SHA-256: `d5f5bc3dc0172d1e3f860037d178306d87f1514048835272fb326d69e3769e90`
- Human adjudication SHA-256: `03b8a87b61cce8ef5e0a1d5b07b0df909562a142c83d30898fab594d1856e3ce`
- Fixture Author plaintext commitment and verified opening SHA-256: `fea1de6361b5821bd817f2787a1a27b85b6066671bfbc36d628c2555ace27a44`
- Paired denominator: 12
- Administrative reserve excluded without imputation: 5
- Amendments: A01 (25-case truncation / 12-case subset), A02 (12-hour delay)

## 2. Workload

| Pass | Cases | Total wall-clock | Median | Mean |
|---|---:|---:|---:|---:|
| A | 25 | 7669 s | 284 s | 306.76 s |
| B | 12 | 4359 s | 307 s | 363.25 s |

Timing is wall-clock and may include interruptions.

## 3. Raw A/B intra-rater results

| Layer | Agreement | Descriptive κ |
|---|---:|---:|
| Accept Decision | 11/12 (91.7%) | 0.750 |
| Outcome | 12/12 (100.0%) | 1.000 |
| Process | 11/12 (91.7%) | 0.750 |
| Recommendation | 8/12 (66.7%) | 0.551 |
| Stop Scope | 12/12 (100.0%) | 1.000 |
| Recovery Authority | 12/12 (100.0%) | 1.000 |
| Valid Alternative Path | 3/12 (25.0%) | 0.000 |
| FIT status | 11/12 (91.7%) | descriptive |
| FIT exact locator | 9/12 (75.0%) | descriptive |
| Hard-Gate presence | 11/12 (91.7%) | descriptive |

Set-valued layers:

- Certification Effects: exact 8/12, mean Jaccard 0.778.
- Control Actions: exact 2/12, mean Jaccard 0.306.
- Failure Codes: exact 2/12, mean Jaccard 0.463.
- Hard-Gate Codes: exact 4/12, mean Jaccard 0.508.

Evidence Assessment exact agreement:

- sufficiency 9/12;
- currentness 10/12;
- scope match 6/12;
- conflicts resolved 10/12.

Core `Accept + Outcome + Process` consensus was 11/12. Core plus Recommendation consensus was 8/12. No Case achieved strict equality across every compared nominal, multilabel, evidence, and FIT field.

## 4. Provenance incident

The PR branch did not contain the previously announced post-Pass-B freeze and report artifacts. They were reconstructed from frozen raw inputs during closure preparation. The reconstructed arithmetic is deterministic, but the originally claimed pre-author-opening report timestamp and hash are not independently recoverable. This is recorded as `PCT-P1-I01` and must be accepted as a P1 limitation.

## 5. Developmental adjudication

The submitted artifact completed all 20 required field decisions across 8 material-disagreement Cases, with no unresolved required field.

Disposition counts:

- Author Intent: 13;
- Pass A: 4;
- Pass B: 3.

Author Intent was used only as a developmental third reference. It was not treated as Gold.

## 6. Important consistency finding

Perfect raw Outcome agreement did **not** imply semantic validity. Both passes made the same Outcome choice in all 12 Cases, yet the submitted adjudication contains three choices that conflict with frozen Codebook v0.2:

- `dev-023`: submitted `FAIL`; v0.2 implies `UNKNOWN`.
- `dev-012`: submitted `FAIL`; v0.2 implies `UNKNOWN`.
- `dev-017`: submitted `FAIL`; v0.2 implies `PASS`.

This is a direct demonstration that intra-rater agreement measures repeatability, not correctness.

## 7. Provisional reliability matrix

- Stable enough for Shadow measurement: Accept Decision, Process, Stop Scope, Recovery Authority.
- Usable with human review: Recommendation, FIT status, FIT locator, Hard-Gate presence, Certification Effects.
- Exploratory only: Control Actions, detailed Failure Codes, Evidence Assessment.
- Not reliable in current form: Valid Alternative Path.
- Outcome: pending D15.

## 8. Threats to validity

- one human completed both passes and the adjudication;
- only a 12-hour interval, with elevated memory carryover;
- Pass B improved citation capture relative to Pass A;
- Pass A stopped at 25, with five right-truncated reserve cases;
- only 12 paired cases;
- synthetic development fixtures;
- non-independent developmental adjudicator;
- Author Intent is not Gold;
- no separate held-out human annotation study;
- no automated Auditor or online intervention was tested.

## 9. P2 recommendation

After D15 and formal P1 closure approval, proceed to **P2 Shadow capture only**, using stable layers as primary measurements. Recommendation and FIT remain reviewed secondary outputs; detailed codes/actions remain diagnostics. No online termination blocking is authorized.

## 10. Remaining human Gate

1. Resolve PCT-P1-D15.
2. Approve P1 closure with limitations.
3. Separately authorize the P2 Shadow Work Order and its privacy, retention, model, tool, budget, and escalation decisions.

## 11. Prohibited claims

P1 does not establish:

- automated Auditor accuracy;
- general human reliability;
- online PCT effectiveness;
- cross-model or cross-Harness generality;
- confirmatory statistical support.
