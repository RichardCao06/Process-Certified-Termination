# P1 — Process Annotation Feasibility

## Current state

Calibration, Codebook v0.2, the 12-case semantic regression, and the 25-case Pass-A freeze are complete. Under A02, the unchanged precommitted 12-case Pass B was released after the 12-hour gate and now awaits human annotation.

The five Pass-A reserve cases remain unannotated: they are not failures, are not imputed, and never enter A/B denominators. Fixture Author Expectations remain unopened.

## Authoritative materials

- `annotation-codebook-v0.2.md`
- `amendment-PCT-P1-A01.md`
- `amendment-PCT-P1-A02.md`
- `development-pilot-pass-b.md`
- `pass-b-interface-requirements-v0.1.md`
- `pass-b-analysis-plan-v0.1.md`
- `p1-closure-report-template.md`
- `p1-exit-gate.md`
- `governance/p1-status.json`
- `data/p1/development-pilot/pass-b/release-record-v0.1.json`
- `data/p1/development-pilot/pass-b/release-delivery-manifest-v0.1.json`

## Pass B release

The ordered list was reconstructed from the frozen Pass-A hash and verified against the pre-existing SHA-256 commitment before any participant file was generated. Pass B uses neutral display IDs and does not include Pass-A labels or QC, author expectations, Gold, hidden-evaluator, held-out, sealed, or repair-result data.

The participant must complete all 12 records and freeze Backup, JSONL, and timing exports before any feedback is shown. The result is a 12-hour delayed, reordered same-annotator re-annotation; memory carryover is an explicit limitation.

## Prepared analysis tooling

- `pct/pilot_analysis.py` — hierarchical nominal, FIT, hard-gate, and multilabel metrics;
- `scripts/p1_pass_b_agreement.py` — reproducible A/B JSON and CSV reports;
- `scripts/p1_prepare_adjudication_packet.py` — pre-author-opening disagreement packet;
- `scripts/p1_verify_author_opening.py` — verifies both human passes and author commitment before opening.

## Boundaries

- No Fixture Author Expectations before raw Pass B and raw A/B report are frozen.
- No case-level Pass-A semantic correction before Pass B.
- No online stop interception.
- No effectiveness claim.
- Same-human A/B results are developmental intra-rater feasibility, not independent inter-rater validation or Gold-label validation.
