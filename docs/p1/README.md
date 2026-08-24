# P1 — Process Annotation Feasibility

## Current state

P1 has completed Calibration, approved all method decisions D01–D14, finalized Codebook v0.2 Pilot, passed the 12-episode semantic regression, and frozen Human Development Pilot Pass A after the first 25 fixed-order episodes.

The originally generated package contained 30 episodes. Under Amendment `PCT-P1-A01`, positions 26–30 are unannotated administrative reserve Cases: they are not failures, are not imputed, and are excluded from Pass-A/Pass-B agreement denominators.

A deterministic reordered 12-case subset of the 25 completed Cases is committed for Human Pass B. Amendment `PCT-P1-A02` shortens only the minimum delay from approximately 72 hours to 12 hours. The selected Cases, reordered sequence, and commitment hash remain unchanged and undisclosed. Pass B must not be released before `2026-08-24T19:48:20Z`.

P1 remains open until Pass B, agreement analysis, author-expectation opening, adjudication, migration reporting, and the P1 Closure Gate are complete.

## Authoritative Pilot materials

- `annotation-codebook-v0.2.md`
- `post-calibration-decision-record-d11-d14.md`
- `development-pilot-pass-a.md`
- `amendment-PCT-P1-A01.md`
- `amendment-PCT-P1-A02.md`
- `pass-b-interface-requirements-v0.1.md`
- `pass-b-analysis-plan-v0.1.md`
- `p1-closure-report-template.md`
- `p1-exit-gate.md`
- `governance/p1-decision-register.json`
- `governance/p1-status.json`
- `data/p1/development-pilot/pass-a/bundle-manifest.json`
- `data/p1/development-pilot/pass-b/subset-commitment-v0.1.json` — preserved historical approximately 72-hour condition;
- `data/p1/development-pilot/pass-b/subset-commitment-v0.2.json` — effective 12-hour condition under A02.

Historical drafts, commitments, and original annotation records are retained as provenance and must not be overwritten.

## Prepared analysis tooling

The following non-contaminating tools are implemented before Pass B release:

- `pct/pilot_analysis.py` — hierarchical nominal, FIT, hard-gate, and multilabel agreement metrics;
- `scripts/p1_pass_b_agreement.py` — reproducible JSON and CSV A/B reports;
- `scripts/p1_prepare_adjudication_packet.py` — pre-author-opening disagreement packet;
- `scripts/p1_verify_author_opening.py` — verifies both human passes are frozen and the opened author file matches its commitment.

These tools use synthetic tests until the real Pass B is frozen. They do not contain the selected 12 identifiers or any author expectation.

## Development signal

Excluding the taught `cal-006` Case, Human and Blind Agent agreed on `ACCEPT` versus `DO_NOT_ACCEPT` in 10/11 Calibration Cases. Fine-grained Outcome and mechanism labels were less stable. The Pilot therefore evaluates layers hierarchically rather than treating the detailed Taxonomy as Gold.

Pass-A structural QC found 25 parseable records, one aggregate internal field conflict, and a systematic citation-capture gap. Case-specific feedback is embargoed until Pass B to avoid contaminating the re-annotation.

The amended 12-hour delay provides less memory separation than the superseded approximately 72-hour condition. All A/B results must explicitly report memory carryover as a threat to validity and remain developmental same-annotator intra-rater feasibility.

## P2 preparation

A non-operative Shadow-mode architecture and draft P2 Work Order are available under `docs/p2/`. They do not authorize P2, runtime intervention, or an effectiveness experiment.

## Boundaries

- No held-out or sealed data.
- No Fixture Author Expectations opened before both human passes and the raw A/B report are frozen.
- No case-level semantic correction of Pass A before Pass B.
- No change to the precommitted Pass-B Cases or order under A02.
- No online stop interception.
- This P1 work does not make an effectiveness claim.
- Same-human Pass A/Pass B results are intra-rater feasibility, not independent inter-rater reliability or Gold-label validation.
