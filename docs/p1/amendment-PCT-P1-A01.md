# PCT P1 Amendment A01 — Development Pilot Workload Reduction

| Field | Value |
|---|---|
| Amendment ID | `PCT-P1-A01` |
| Phase | P1 |
| Effective date | 2026-08-24 |
| Human authority | Research Owner `RichardCao06` |
| Trigger | The Research Owner reported that 30 annotations were too burdensome, completed the first 25 fixed-order episodes, and instructed the project to continue. |
| Results seen before change | The annotator had seen and labeled Pass-A positions 1–25. No Human–Agent comparison, Fixture Author Expectation, hidden evaluator, Gold, sealed data, or Pass-B result had been opened. |
| Confirmatory status | Development-only; no confirmatory claim is permitted. |

## Approved operational change

1. Human Pass A is frozen at the first **25** episodes in the pre-generated fixed randomized order.
2. Positions 26–30 remain unannotated reserve cases:
   `P1-DEV-A-26, P1-DEV-A-27, P1-DEV-A-28, P1-DEV-A-29, P1-DEV-A-30`.
3. The five reserve cases are not failures, zeros, or negative labels. They are excluded from every Pass-A and Pass-B denominator and are not imputed.
4. The missingness is reported as **administrative right truncation**, not assumed missing at random.
5. Delayed blind Human Pass B is reduced to a deterministic **12-episode subset** of the 25 completed Pass-A cases, consistent with the previously approved “pilot subset” fallback.
6. Pass B must not be released before `2026-08-27T07:48:20Z` and must use a different order and neutral display identifiers.
7. The exact Pass-B ordered subset is precommitted by SHA-256:
   `1465d1b21da860660a90a24b5e9c1bc8673c49f4052fbf8d647c15f55e026e86`.
8. The 30-case encrypted Fixture Author Expectations remain unopened until Pass A and the 12-case Pass B are frozen. Only expectations corresponding to completed/selected cases may enter the later comparison; the five reserve cases remain descriptive author fixtures without human labels.

## Consequences

- P1 may estimate only developmental feasibility and intra-rater stability on the completed data.
- The 25-case Pass-A distribution may not preserve the planned 10/10/10 strata balance; no balanced-strata claim is allowed until author metadata is opened after Pass B.
- The 12-case Pass-B agreement estimate will be imprecise and reported descriptively.
- Any later expansion to the five reserve cases creates a new annotation pass and must not be silently pooled with Pass A.

## Rationale

The annotation burden was empirically high: the 25 completed cases required 7669 seconds (about 2.13 hours), with a median of 284 seconds per case. Reducing re-annotation burden preserves the core P1 question—whether the label system is usable and reasonably stable—without pretending the development pilot has confirmatory power.
