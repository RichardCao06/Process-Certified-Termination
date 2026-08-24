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
- `p1-exit-gate.md`
- `governance/p1-decision-register.json`
- `governance/p1-status.json`
- `data/p1/development-pilot/pass-a/bundle-manifest.json`
- `data/p1/development-pilot/pass-b/subset-commitment-v0.1.json`

Historical drafts and original annotation records are retained as provenance and must not be overwritten.

## Development signal

Excluding the taught `cal-006` case, Human and Blind Agent agreed on `ACCEPT` versus `DO_NOT_ACCEPT` in 10/11 Calibration cases. Fine-grained Outcome and mechanism labels were less stable. The Pilot therefore evaluates layers hierarchically rather than treating the detailed Taxonomy as Gold.

Pass-A structural QC found 25 parseable records, one aggregate internal field conflict, and a systematic citation-capture gap. Case-specific feedback is embargoed until Pass B to avoid contaminating the delayed re-annotation.

## Boundaries

- No held-out or sealed data.
- No Fixture Author Expectations opened before both human passes are frozen.
- No case-level semantic correction of Pass A before Pass B.
- No online stop interception.
- No effectiveness claim.
- Same-human Pass A/Pass B results are intra-rater feasibility, not independent inter-rater validation.
