# P1 Closure Report v0.1 — Final

## Status

**APPROVED WITH LIMITATIONS — P1 CLOSED on 2026-08-25.**

P1 asked whether Candidate-Stop outcome, process, evidence, control, and localization
judgments could be represented and annotated with enough developmental stability to
support a later Shadow Auditor study. P1 did not test online Process-Certified
Termination effectiveness.

## 1. Frozen inputs and provenance

| Input | SHA-256 / count |
|---|---|
| Codebook | `0.2-pilot` |
| Pass A raw annotations | `d561b442053293c94c13db6ff5c49af6ef187fa12cff351f0e94dbb1e92364b8` |
| Pass B raw annotations | `ff5bb76b5b168dd546f61f2dd065f2091ed841e6a2335c014e2a3f1441a5ed5f` |
| Pass B episodes | `d5f5bc3dc0172d1e3f860037d178306d87f1514048835272fb326d69e3769e90` |
| Raw human adjudication | `03b8a87b61cce8ef5e0a1d5b07b0df909562a142c83d30898fab594d1856e3ce` |
| Fixture Author plaintext commitment/opening | `fea1de6361b5821bd817f2787a1a27b85b6066671bfbc36d628c2555ace27a44` |
| D15 decision record | `fcc3afc12a0dab682650a083314f5ae377126a1a1cecbed5b6005594a1365701` |
| D15 append-only correction | `c851d17cc3b7f54efa90c5677d6284d6941c34760bd5fce73263ca032928585c` |
| Final developmental adjudication | `9a7f64903e9517d85f640f8583f8a30da1663f9e57eeab752c77febc26a82f58` |
| Paired A/B denominator | 12 |
| Administrative reserves excluded | 5 |

Amendment A01 froze Pass A after 25 fixed-order cases and prohibited imputation of the
five reserve cases. Amendment A02 shortened the Pass-B minimum delay to 12 hours
without changing the precommitted subset or order.

The raw adjudication completed all 20 required decisions across eight material
disagreement cases, with no missing required field. Its source record remains unchanged.

## 2. Workload

| Pass | Completed cases | Total wall-clock | Median | Mean |
|---|---:|---:|---:|---:|
| A | 25 | 7,669 s | 284 s | 306.76 s |
| B | 12 | 4,359 s | 307 s | 363.25 s |

Timing is wall-clock and may include interruptions.

## 3. Raw A/B same-annotator results

| Layer | Agreement | Descriptive κ |
|---|---:|---:|
| Accept Decision | 11/12 (91.7%) | 0.750 |
| Outcome Verdict | 12/12 (100.0%) | 1.000 |
| Process Verdict | 11/12 (91.7%) | 0.750 |
| Certification Recommendation | 8/12 (66.7%) | 0.551 |
| Stop Scope | 12/12 (100.0%) | 1.000 |
| Recovery Authority | 12/12 (100.0%) | 1.000 |
| Valid Alternative Path | 3/12 (25.0%) | 0.000 |
| FIT status | 11/12 (91.7%) | descriptive |
| FIT exact locator | 9/12 (75.0%) | descriptive |
| Hard-Gate presence | 11/12 (91.7%) | descriptive |

Set-valued layers:

- Certification Effects: exact 8/12; mean Jaccard 0.778.
- Control Actions: exact 2/12; mean Jaccard 0.306.
- Failure Codes: exact 2/12; mean Jaccard 0.463.
- Hard-Gate Codes: exact 4/12; mean Jaccard 0.508.

Evidence Assessment exact agreement was 9/12 for sufficiency, 10/12 for currentness,
6/12 for scope match, and 10/12 for conflict resolution.

Core `Accept + Outcome + Process` consensus occurred in 11/12 cases. Adding
Recommendation reduced consensus to 8/12. No case was identical across every nominal,
multilabel, evidence, and localization field.

These are descriptive **intra-rater feasibility** results, not independent inter-rater
reliability estimates.

## 4. Author Intent comparison

Fixture Author Intent was opened only as a developmental third reference and remains
`not_gold=true`.

Before the D15 correction, the submitted developmental layer matched Author Intent in:

- Accept Decision: 12/12;
- Outcome Verdict: 9/12;
- Process Verdict: 12/12;
- Recommendation: 11/12;
- FIT: 12/12.

D15 corrected the three Outcome disagreements (`dev-023`, `dev-012`, `dev-017`), so the
final developmental Outcome layer also aligns with Author Intent in 12/12 cases.
That alignment is a consistency observation, not Gold-label validation.

## 5. Developmental adjudication and D15

The raw human adjudication selected 13 Author-Intent values, four Pass-A values, and
three Pass-B values for the 20 required material fields.

Perfect raw Outcome repeatability did not establish semantic correctness. Both passes
made the same Outcome choice in all 12 paired cases, yet three submitted outcomes
conflicted with frozen Codebook v0.2:

| Case | Raw submitted | D15 final | Why |
|---|---|---|---|
| `dev-023` | `FAIL` | `UNKNOWN` | stale evidence did not prove a current failure |
| `dev-012` | `FAIL` | `UNKNOWN` | no fresh validation existed after mutation |
| `dev-017` | `FAIL` | `PASS` | deletion occurred; authorization breach belongs in Process |

The Research Owner approved D15 option A. The raw adjudication was preserved and a
separate correction record produced the final developmental layer.

This is the central P1 methodological finding:

> Repeatability is not correctness. A stable annotation can still encode a shared
> semantic error unless it is checked against the frozen construct definition and trace.

## 6. Final Reliability Matrix

### Stable enough for P2 Shadow primary measurement

- Accept Decision;
- Process Verdict;
- Stop Scope;
- Recovery Authority.

### Usable only with human review

- Outcome Verdict;
- Certification Recommendation;
- FIT status;
- FIT locator;
- Hard-Gate presence;
- Certification Effects.

### Exploratory only

- Control Actions;
- detailed Failure Codes;
- Evidence Assessment.

### Not reliably annotatable in the current representation

- Valid Alternative Path.

Outcome is deliberately not promoted to the primary stable group despite raw 12/12
agreement because D15 exposed shared semantic error in 3/12 cases.

## 7. Taxonomy and interface migration

The two-stage `ACCEPT / DO_NOT_ACCEPT → specialized recommendation` structure is
retained. Outcome and Process remain separate. Stop Scope and Recovery Authority remain
required. FIT remains review-gated.

`valid_alternative_path` must be split into applicability and validity fields. Detailed
codes, Control Actions, and Evidence Assessment require further anchors and must not
become unreviewed online gates on the basis of P1.

No raw A/B metric was changed by D15.

## 8. Provenance incident PCT-P1-I01

Several post-Pass-B artifacts previously announced as persisted were absent from the
branch during closure preparation. They were deterministically reconstructed from
frozen Pass A/B inputs, the released episode package, the verified Author commitment,
and the completed adjudication.

The Author plaintext hash matched its pre-existing commitment, and the raw A/B
arithmetic is reproducible. However, the repository cannot independently prove that the
originally announced A/B report itself was persisted and hash-frozen before Author
opening. This limitation remains accepted and must accompany any use of the P1 results.

## 9. Threats to validity

- one human completed both passes and the developmental adjudication;
- a 12-hour interval permits case recognition and memory carryover;
- Pass B improved structural citation capture relative to Pass A;
- Pass A ended after 25 cases; five reserves were excluded without imputation;
- only 12 paired cases inform the repeatability estimates;
- the development corpus is synthetic;
- the adjudicator was not independent;
- Author Intent is not Gold;
- no separate held-out human annotation study was conducted;
- no automated Auditor accuracy or runtime effect was measured;
- PCT-P1-I01 limits historical ordering proof.

## 10. Conclusions

Within this developmental setting:

1. a compact core stop-certification layer can be annotated with sufficient apparent
   stability to justify a non-intervening Shadow measurement study;
2. specialized recommendation, Outcome, FIT, and hard-gate layers require human review;
3. detailed mechanism/action labels are too unstable for unreviewed primary use;
4. the current Valid Alternative Path representation should not be used;
5. agreement metrics alone are insufficient—construct-conformance auditing is necessary.

These conclusions do not generalize to independent annotators, natural production
traces, other models or Harnesses, or online intervention.

## 11. P2 disposition

P1 makes the project **eligible for a separate P2 Shadow Work Order**. It does not
authorize P2 execution or online intervention.

A future P2 decision must separately freeze privacy, retention, model, Harness, tool,
budget, escalation, review, and no-intervention controls.

## 12. Approval

```text
Research Owner: RichardCao06
Decision: APPROVED WITH LIMITATIONS
D15: A
Date: 2026-08-25
P1 closed: YES
P2 authorized: NO
Online intervention authorized: NO
Effectiveness claim allowed: NO
Accepted incident: PCT-P1-I01
```
