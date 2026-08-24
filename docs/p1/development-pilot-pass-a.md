# P1 Development Pilot Pass A v0.2

## Status

**Authorized and ready for Human Pass A.**

The four post-calibration decisions D11–D14 were approved as A in PR #2 on 2026-08-24. The Codebook v0.2 regression passed all 12 approved core expectations.

## Participant package

- File: `PCT_P1_Development_Pilot_Pass_A_v0.2.zip`
- SHA-256: `3d60e0a31f1e7e8a4ad157930facbecd5acc19db62a3245258ea9dc0335ee5ec`
- Episodes: 30
- Declared composition: 10 clean/acceptable, 10 controlled single-fault, 10 compound/development analogues
- Public package contains no Fixture Author Expectations, reference answers, hidden evaluator details, Gold labels, held-out data, or sealed data.

The repository stores a base64-split, hash-verified copy under `data/p1/development-pilot/pass-a/`.

## Blinding

The author key and the delayed Pass B order are not committed. The repository contains only SHA-256 commitments:

- Author key: `824fdf8cdabba9d2fb6de6ba41c411e93807d056abd1ef04fd923bf993098b69`
- Pass B order: `fc55d6e78240f6565571f9b21c19204d99f8263c8220b9489c81b1086328e492`

Pass B must not be released before Pass A is frozen and the planned delay is observed.

## Human action

1. Materialize or download the participant ZIP.
2. Extract it.
3. Open `PCT_P1_Development_Pilot_Annotator_v0.2.html`.
4. Import `PCT_P1_Development_Pilot_Pass_A_Episodes_v0.2.json`.
5. Complete all 30 episodes without viewing reference material.
6. Export annotations JSONL, active timing CSV, and full backup JSON.
7. Preserve the three files and return them for structural QC.

## Interpretation

This Pilot estimates development-stage annotation feasibility and ambiguity. It does not establish inter-rater reliability, automated Auditor accuracy, or online PCT effectiveness.
