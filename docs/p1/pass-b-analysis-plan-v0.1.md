# P1 Pass B Analysis Plan v0.1

## Status

Pre-analysis implementation plan. It is prepared before Human Pass B is released and does not contain the selected Case identifiers, Pass A labels, Fixture Author Expectations, or semantic feedback.

This is a developmental intra-rater feasibility analysis, not an independent inter-rater study, Gold-label validation, or an online PCT effectiveness experiment.

## 1. Frozen inputs

The analysis must use:

- the hash-frozen 25-record Human Pass A file;
- exactly the precommitted 12-case Pass B subset after its delayed, reordered annotation is frozen;
- the same observable Episode semantics and Codebook v0.2;
- Pass B structural UI improvements that do not add Case-specific semantic instruction;
- no Fixture Author Expectations until the raw A/B analysis is itself frozen.

The five administrative reserve Cases from Pass A are excluded without imputation.

## 2. Analysis order

The required order is:

```text
Pass B export
→ structure and hash validation
→ pair A/B by trajectory_id + stop_id
→ compute raw intra-rater metrics
→ generate per-Case disagreement packet
→ freeze A/B report and hashes
→ only then verify and open Fixture Author Expectations
→ compare A / B / Author as three separate inputs
→ human developmental adjudication
```

A Pass B display ID must never be used as the pairing key because Pass B is deliberately reordered and neutrally relabeled.

## 3. Denominators and missingness

- Primary paired denominator: the 12 precommitted Pass B Cases.
- A Case enters a field-specific denominator only when the field is structurally present in both passes.
- A missing or malformed Pass B record is not imputed and blocks the planned 12-pair report until corrected from the raw export or explicitly amended.
- The five unannotated Pass A reserve Cases never enter an A/B denominator.
- No claim may be made that the completed 25 or selected 12 preserve the original 10/10/10 strata balance before author metadata is opened.

## 4. Hierarchical endpoints

The analysis is intentionally hierarchical.

### Level 1 — stop acceptance

- `ACCEPT` versus `DO_NOT_ACCEPT` exact agreement;
- percent agreement;
- Cohen’s kappa, reported descriptively because `n=12` is small.

This is the most important P1 feasibility signal because it corresponds to the future Harness Gate.

### Level 2 — control and verdict semantics

Exact agreement and descriptive kappa for:

- `certification_recommendation`;
- `outcome_verdict`;
- `process_verdict`;
- `stop_scope`;
- `recovery_authority`;
- `valid_alternative_path`.

### Level 3 — First Invalid Transition

Report separately:

- FIT status agreement (`EXACT / RANGE / NONE / UNKNOWN`);
- presence agreement (`NONE` versus any invalid transition);
- exact locator agreement;
- Case list where status agrees but locator differs.

Do not collapse FIT status and event localization into one score.

### Level 4 — multilabel diagnosis

For each of:

- `certification_effects`;
- `control_actions`;
- `failure_codes`;
- `hard_gate_codes`;

report:

- exact set match;
- mean per-Case Jaccard similarity;
- hard-gate-presence agreement.

Detailed mechanism codes remain exploratory even if higher-level acceptance is stable.

## 5. Consensus views

Four data views must remain separate:

1. **Raw Pass A** — first human judgment;
2. **Raw Pass B** — delayed and reordered second judgment;
3. **Core Consensus** — A/B agree on acceptance, Outcome, and Process;
4. **Strict Consensus** — no recorded field-level disagreement.

After adjudication, a fifth view may be added:

5. **Adjudicated Development Label** — human decision with a preserved rationale and source annotation IDs.

The adjudicated view must not overwrite either raw pass.

## 6. Disagreement classification

The pre-author-opening packet classifies differences without deciding which pass is correct:

- `ACCEPT_DECISION`;
- `OUTCOME_VERDICT`;
- `PROCESS_VERDICT`;
- `RECOMMENDATION`;
- `STOP_SCOPE`;
- `RECOVERY_AUTHORITY`;
- `VALID_ALTERNATIVE_PATH`;
- `CERTIFICATION_EFFECTS`;
- `CONTROL_ACTIONS`;
- `FAILURE_CODES`;
- `HARD_GATE_CODES`;
- `EVIDENCE_ASSESSMENT`;
- `FIT_STATUS`;
- `FIT_LOCATOR`.

After author opening and human review, each substantive difference may receive one or more cause codes:

- `HUMAN_ENTRY_ERROR`;
- `HUMAN_RULE_MISUNDERSTANDING`;
- `CODEBOOK_AMBIGUITY`;
- `CASE_INFORMATION_MISSING`;
- `UI_CAPTURE_DEFECT`;
- `MULTIPLE_VALID_INTERPRETATIONS`;
- `AUTHOR_EXPECTATION_DEFECT`;
- `UNRESOLVED`.

## 7. Workload and confidence

Report:

- Pass A and Pass B total time;
- median and mean seconds per paired Case;
- Pass B minus Pass A time difference;
- FIT confidence change;
- proportion of `UNKNOWN`, `UNDETERMINED`, and low-confidence annotations.

Timing is wall-clock elapsed time and may contain interruptions. It is not automatically net labor time.

## 8. Citation capture caveat

Pass A had a systematic citation-capture gap. Pass B may improve the interface by requiring Event citations and prompting material Evidence citations.

Consequences:

- citation completeness may be compared as an interface-quality result;
- citation completeness must not be interpreted as pure annotator reliability because the interface changed;
- Outcome, Process, Recommendation, and FIT semantics must remain unchanged between passes.

## 9. Author Expectation opening

Fixture Author Expectations may be opened only after:

- Pass A is frozen;
- Pass B is frozen;
- raw A/B agreement outputs are generated and hash-frozen;
- the opened plaintext matches its pre-existing commitment.

Author Expectations are a third developmental reference, not Gold. A/B agreement against Author must be reported separately from A/B intra-rater agreement.

## 10. Allowed conclusions

P1 may conclude, within this development setting:

- which annotation layers appear stable or unstable for the same human;
- which distinctions require Codebook revision;
- which Cases are underdetermined;
- the observed annotation workload;
- which labels are suitable only for exploratory diagnosis.

P1 may not conclude:

- independent human reliability;
- general human annotation reliability;
- automated Auditor accuracy;
- online Process-Certified Termination effectiveness;
- a confirmatory success rate or non-inferiority result.

## 11. Reproducible commands

After Pass B is frozen:

```bash
python3 scripts/p1_pass_b_agreement.py \
  --pass-a <pass-a.jsonl> \
  --pass-b <pass-b.jsonl> \
  --output-json reports/p1/pass-a-b-agreement.json \
  --output-csv reports/p1/pass-a-b-pairs.csv \
  --expected-pairs 12

python3 scripts/p1_prepare_adjudication_packet.py \
  --episodes <observable-episodes.json> \
  --pass-a <pass-a.jsonl> \
  --pass-b <pass-b.jsonl> \
  --output reports/p1/pre-author-opening-adjudication-packet.json
```
