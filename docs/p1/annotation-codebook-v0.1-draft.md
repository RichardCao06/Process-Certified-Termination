# Candidate-Stop Annotation Codebook v0.1 — Draft

## 1. Annotation object

The recommended primary unit is a **Candidate-Stop episode**:

> the observable trajectory prefix from the current goal revision through a point where the Worker or Harness would stop, together with the current environment snapshot, obligation state, and available evidence.

The annotation may localize one event or a bounded event range inside that episode.

## 2. Blinding

During a blind annotation pass, annotators must not see:

- hidden evaluator output;
- Gold failure code or First Invalid Transition;
- another annotator's labels;
- the method condition when avoidable;
- repair outcomes occurring after the Candidate Stop.

Synthetic fixture authors may retain expected labels, but those labels are engineering expectations, not empirical Gold.

## 3. Annotation order

Annotate in the following order to reduce hindsight contamination:

1. read the approved goal and obligations;
2. inspect the current snapshot and outcome evidence;
3. assign `outcome_verdict`;
4. reconstruct obligation and evidence state from observable events;
5. assign `process_verdict`;
6. select mechanism codes and certification effects;
7. localize the First Invalid Transition;
8. assess whether an unfamiliar path is a valid alternative;
9. assign the termination recommendation;
10. cite the smallest event/evidence set supporting the label.

## 4. Four-way verdict

| Value | Meaning |
|---|---|
| `PASS` | available evidence affirmatively supports the requested property |
| `FAIL` | available evidence contradicts the requested property or shows a violation |
| `UNKNOWN` | evidence is insufficient or materially ambiguous |
| `NOT_APPLICABLE` | the property does not apply to this episode |

Absence of observed failure is not automatically `PASS`.

## 5. Outcome and process remain separate

- `outcome_verdict` asks whether the final state satisfies outcome obligations.
- `process_verdict` asks whether hard process conditions and evidence-supported transitions are valid.

Possible combinations:

| Outcome | Process | Interpretation |
|---|---|---|
| PASS | PASS | candidate for Certified Success |
| PASS | FAIL | corrupt or procedurally invalid success |
| FAIL | PASS | sound process but unfinished/incorrect result |
| UNKNOWN | FAIL | process defect exists; final state is not yet established |
| UNKNOWN | UNKNOWN | insufficient basis for certification or rejection |

## 6. Termination recommendation

| Value | Use when |
|---|---|
| `ACCEPT` | outcome and process both pass, required evidence is current, and no hard gate exists |
| `CONTINUE` | concrete authorized work remains and current evidence shows failure |
| `EVIDENCE_REQUIRED` | a lawful probe can resolve a hard evidence gap |
| `HUMAN_REQUIRED` | the remaining issue is normative, authority-bound, or unavailable to automation |
| `BLOCKED` | no meaningful authorized progress is possible without external change |
| `NO_PROGRESS` | repeated equivalent attempts add no evidence or state change |
| `UNDETERMINED` | the annotator cannot support one of the above |

`BLOCKED` is not a synonym for difficult, uncertain, or incomplete.

## 7. First Invalid Transition

The First Invalid Transition is the earliest observable state promotion or decision that becomes unjustified given the information available at that point.

Localization values:

- `EXACT`: one event is supportable;
- `RANGE`: the defect is supportable but the exact event cannot be distinguished;
- `NONE`: no invalid transition is present;
- `UNKNOWN`: available trace is insufficient.

Do not force an exact event to improve apparent agreement.

## 8. Evidence assessment

Annotate four dimensions separately:

- `sufficiency`: enough evidence exists for the claim;
- `currentness`: evidence remains valid for the current snapshot;
- `scope_match`: evidence covers the same obligation scope;
- `conflicts_resolved`: contradictory evidence was handled.

Worker explanations and decision checkpoints are useful claims and search aids, but not independent proof.

## 9. Hard-gate discipline

`hard_gate_codes` must be a subset of:

1. the selected `failure_codes`; and
2. codes mapped to P0-approved hard-gate classes in the taxonomy.

An annotator may identify a serious new defect without making it a hard gate. Promotion requires a later authorized decision.

## 10. Alternative paths

Set `valid_alternative_path` to:

- `YES` when the path differs from a familiar procedure but satisfies all approved preconditions and evidence obligations;
- `NO` when the path violates a required rule;
- `UNKNOWN` when the contract does not resolve the issue.

Efficiency, elegance, and conventional ordering are not hard process requirements by default.

## 11. Disagreement and adjudication

Annotators first work independently. Adjudication occurs only after labels are frozen for the pass. The adjudicator records:

- the disagreement type;
- evidence cited by each annotator;
- the adopted label or retained ambiguity;
- whether the codebook or schema must change.

Do not erase the original annotations.

## 12. Synthetic examples

- `valid-alternative-path.json`: PASS/PASS, `ACCEPT`, localization `NONE`.
- `premature-promotion.json`: `TRN.PREMATURE_STATE_PROMOTION` and `EVD.MISSING_REQUIRED_EVIDENCE`; first invalid event E2.
- `stale-evidence.json`: E7 invalidates EV1; E8 is the first unsupported decision using it.
- `ignored-tool-failure.json`: E3 fails; E4 promotes the affected obligation anyway.
- `scope-mismatch.json`: EV1 covers O1, but E5 uses it for O2.
