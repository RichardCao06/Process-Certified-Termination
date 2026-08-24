# PCT P1 Amendment A02 — Shorten the Pass-B Minimum Delay to 12 Hours

| Field | Value |
|---|---|
| Amendment ID | `PCT-P1-A02` |
| Phase | P1 |
| Effective date | 2026-08-24 |
| Human authority | Research Owner `RichardCao06` |
| Trigger | The Research Owner explicitly requested that the Pass-B minimum delay be shortened to 12 hours so the project can proceed sooner. |
| Supersedes | Only the Pass-B `release_not_before` condition in `PCT-P1-A01`; all other A01 terms remain effective. |
| Results seen before change | Human Pass A was frozen at 25 cases. Aggregate structural QC and non-contaminating tooling were available. No Pass-B labels, Fixture Author Expectations, hidden evaluator, Gold, sealed data, or case-specific Pass-A semantic feedback had been opened. |
| Confirmatory status | Development-only and exploratory; no confirmatory claim is permitted. |

## Approved operational change

1. The minimum delay between the frozen Pass A and release of Pass B is changed from approximately 72 hours to **12 hours**.
2. Pass A freeze reference time remains `2026-08-24T07:48:20Z`.
3. The new Pass-B release-not-before time is:
   `2026-08-24T19:48:20Z`.
4. The precommitted selected count, selected cases, reordered sequence, and ordered-subset commitment remain unchanged:
   `1465d1b21da860660a90a24b5e9c1bc8673c49f4052fbf8d647c15f55e026e86`.
5. Pass B must still use neutral display identifiers and must not reveal Pass-A labels, rationales, confidence, timing, QC, Fixture Author Expectations, or case-specific semantic feedback.
6. Fixture Author Expectations remain unopened until both Human Pass A and Human Pass B are frozen and the raw A/B report is preserved.
7. The Pass-B study must be described as a **12-hour delayed, reordered same-annotator re-annotation**, not as satisfying the originally planned approximately 72-hour memory-decay condition.

## Accepted consequences

- The shorter interval increases the risk that the annotator remembers specific Cases or prior answers.
- A high A/B agreement may partly reflect memory carryover rather than reproducible application of the Codebook.
- The resulting metrics remain developmental intra-rater feasibility only; they are not independent inter-rater reliability, Gold-label validation, or evidence of PCT effectiveness.
- Analyses must report the actual interval and treat memory carryover as an explicit threat to validity.
- The 12-case subset and order cannot be changed to compensate for the shorter delay.

## Unchanged protections

- The five Pass-A reserve Cases remain unannotated and excluded without imputation.
- No case-specific Pass-A feedback may be shown before Pass B is frozen.
- No author expectation, hidden evaluator, held-out, sealed, Gold, or repair-result information may enter the Pass-B annotation context.
- Raw Pass A and Pass B records must remain append-only and separately hash-frozen.

## Rationale

P1 is a development-stage feasibility study, not a confirmatory reliability study. A 12-hour interval preserves some temporal separation and the stronger protections of reordering, neutral relabeling, hidden prior labels, and a precommitted subset/order, while materially reducing project delay. The cost is weaker protection against answer recall, which is explicitly accepted and must constrain the interpretation of the results.
