# P1 — Process Annotation Feasibility

## Current state

P1 has completed Calibration, approved all method decisions D01–D14, finalized Codebook v0.2 Pilot, passed the 12-episode semantic regression, and frozen Human Development Pilot Pass A after the first 25 fixed-order episodes.

The originally generated package contained 30 episodes. Under Amendment `PCT-P1-A01`, positions 26–30 are unannotated administrative reserve cases: they are not failures, are not imputed, and are excluded from Pass-A/Pass-B agreement denominators.

A deterministic reordered 12-case subset of the 25 completed cases is committed for delayed Human Pass B. Its identifiers remain undisclosed and it must not be released before `2026-08-27T07:48:20Z`.

P1 remains open until Pass B, agreement analysis, author-expectation opening, adjudication, migration reporting, and the P1 Closure Gate are complete.

## Authoritative Pilot materials

- `annotation-codebook-v0.2.md`
- `post-calibration-decision-record-d11-d14.md`
- `development-pilot-pass-a.md`
- `amendment-PCT-P1-A01.md`
- `pass-b-interface-requirements-v0.1.md`
- `pass-b-analysis-plan-v0.1.md`
- `p1-closure-report-template.md`
- `p1-exit-gate.md`
- `governance/p1-decision-register.json`
- `governance/p1-status.json`
- `data/p1/development-pilot/pass-a/bundle-manifest.json`
- `data/p1/development-pilot/pass-b/subset-commitment-v0.1.json`

Historical drafts and original annotation records are retained as provenance and must not be overwritten.

## Prepared analysis tooling

The following non-contaminating tools are implemented before Pass B release:

- `pct/pilot_analysis.py` — hierarchical nominal, FIT, hard-gate, and multilabel agreement metrics;
- `scripts/p1_pass_b_agreement.py` — reproducible JSON and CSV A/B reports;
- `scripts/p1_prepare_adjudication_packet.py` — pre-author-opening disagreement packet;
- `scripts/p1_verify_author_opening.py` — verifies both human passes are frozen and the opened author file matches its commitment.

These tools use synthetic tests until the real Pass B is frozen. They do not contain the selected 12 identifiers or any author expectation.

## Development signal

Excluding the taught `cal-006` case, Human and Blind Agent agreed on `ACCEPT` versus `DO_NOT_ACCEPT` in 10/11 Calibration cases. Fine-grained Outcome and mechanism labels were less stable. The Pilot therefore evaluates layers hierarchically rather than treating the detailed Taxonomy as Gold.

Pass-A structural QC found 25 parseable records, one aggregate internal field conflict, and a systematic citation-capture gap. Case-specific feedback is embargoed until Pass B to avoid contaminating the delayed re-annotation.

## P2 preparation

A non-operative Shadow-mode architecture and draft P2 Work Order are available under `docs/p2/`. They do not authorize P2, runtime intervention, or an effectiveness experiment.

## Boundaries

- No held-out or sealed data.
- No Fixture Author Expectations opened before both human passes are frozen.
- No case-level semantic correction of Pass A before Pass B.
- No online stop interception.
- This P1 work does not make an effectiveness claim.
- Same-human Pass A/Pass B results are intra-rater feasibility, not independent inter-rater validation.
