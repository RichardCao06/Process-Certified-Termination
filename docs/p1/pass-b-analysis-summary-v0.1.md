# P1 Pass B Analysis Summary v0.1

## Status

Human Pass B is frozen. The raw A/B report was hash-frozen before Fixture Author Expectations were opened. The opened author file matched its pre-existing plaintext SHA-256 commitment. Author expectations remain a developmental third reference, not Gold.

## Design boundary

- 12-hour delayed, reordered, same-annotator re-annotation;
- developmental intra-rater feasibility only;
- elevated memory-carryover risk;
- not independent inter-rater reliability;
- not Gold-label validation;
- not automated Auditor accuracy or online PCT effectiveness.

## Analysis order preserved

```text
freeze raw Human Pass B
→ freeze raw A/B report and disagreement packet
→ verify and open Fixture Author Expectations
→ compare Pass A / Pass B / Author intent
→ human developmental adjudication
```

The exact field-level metrics and provisional reliability matrix are stored in:

- `reports/p1/pass-b/ab-intrarater-report-pre-author-v0.1.json`;
- `reports/p1/pass-b/ab-author-threeway-report-v0.1.json`;
- `reports/p1/pass-b/ab-author-threeway-summary-v0.1.csv`.

## Human adjudication gate

Only material disagreements in core verdicts, specialized termination recommendation, valid-alternative interpretation, or First Invalid Transition require human adjudication. Fine-grained mechanism-code differences remain descriptive unless they change a hard-gate interpretation.

The adjudication source is:

- `reports/p1/pass-b/human-adjudication-packet-v0.1.json`;
- `docs/p1/human-adjudication-gate-v0.1.md`.

Raw Pass A, raw Pass B, Fixture Author Intent, and the eventual adjudicated layer remain separate and must not be overwritten.
