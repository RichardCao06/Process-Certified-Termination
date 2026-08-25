# P1 Closure Report — Template

## Status

Do not mark this report approved until Human Pass B, raw A/B analysis, author-expectation opening verification, developmental adjudication, and the P1 Exit Gate are complete.

## 1. Phase purpose

State the P1 question:

> Can Candidate-Stop outcome, process, evidence, control, and localization judgments be represented and annotated with enough stability to support a later Shadow Auditor experiment?

P1 does not test online PCT effectiveness.

## 2. Frozen inputs

Record:

- Protocol and Codebook versions;
- Pass A raw-file name and SHA-256;
- Pass B raw-file name and SHA-256;
- paired Case count;
- administrative reserve count;
- Pass B subset commitment and release time;
- annotation interface versions;
- author-expectation commitment and opening verification record;
- all Amendments.

## 3. Workload

Report separately for Pass A and Pass B:

- completed Cases;
- total wall-clock seconds;
- median and mean seconds per Case;
- interruptions or known timing limitations;
- fields that caused the highest reported uncertainty.

## 4. Raw intra-rater results

### Level 1

- `ACCEPT / DO_NOT_ACCEPT` agreement;
- descriptive Cohen’s kappa.

### Level 2

- Recommendation;
- Outcome;
- Process;
- Stop Scope;
- Recovery Authority;
- Valid Alternative Path.

### Level 3

- FIT status;
- invalid-transition presence;
- exact locator.

### Level 4

- Certification Effects exact/Jaccard;
- Control Actions exact/Jaccard;
- Failure Codes exact/Jaccard;
- Hard Gates exact/Jaccard and presence.

All denominators must be explicit.

## 5. Consensus and ambiguity

Report:

- Core Consensus count;
- Strict Consensus count;
- disagreement Cases by field;
- `UNKNOWN` and `UNDETERMINED` frequency;
- retained ambiguity Cases;
- Cases excluded from a field-specific result and why.

## 6. Author Expectation comparison

After opening verification, compare:

```text
Pass A versus Author
Pass B versus Author
A/B Consensus versus Author
```

Do not call Author Expectations Gold. Record Cases where both human passes agree against the Author and assess possible Fixture defects.

## 7. Developmental adjudication

For each disagreement, preserve:

- raw Pass A annotation ID;
- raw Pass B annotation ID;
- author expectation ID when available;
- disagreement fields;
- cause code;
- selected or synthesized developmental label;
- retained ambiguity;
- rationale;
- Codebook, Schema, UI, or Fixture change required.

## 8. Reliability matrix

Classify each layer as one of:

- `PILOT_STABLE_ENOUGH_FOR_SHADOW_MEASUREMENT`;
- `USABLE_WITH_HUMAN_REVIEW`;
- `EXPLORATORY_ONLY`;
- `NOT_RELIABLY_ANNOTATABLE_IN_CURRENT_FORM`.

Required rows:

- Accept Decision;
- Recommendation;
- Outcome;
- Process;
- Stop Scope;
- Recovery Authority;
- FIT status;
- FIT locator;
- Hard-Gate presence;
- detailed Failure Codes;
- Evidence Assessment;
- Valid Alternative Path.

## 9. Migration record

Describe:

- Codebook changes;
- Schema changes;
- UI changes;
- Case repairs or exclusions;
- old-to-new code mappings;
- which earlier labels remain valid;
- whether any analysis must be rerun.

Never overwrite the raw passes.

## 10. Threats to validity

At minimum address:

- one human performed both passes;
- finite delay and possible Case recognition;
- Pass B interface changes for citation capture;
- Pass A right truncation at 25;
- 12-pair sample size;
- synthetic development Cases;
- non-independent developmental adjudicator;
- Author Expectations are not Gold;
- no confirmation on a separate held-out human annotation set.

## 11. P1 conclusions

Use conditional language. Examples:

- “Within the tested developmental setting, Accept Decision appeared more stable than detailed mechanism codes.”
- “The current FIT locator was not stable enough to serve as an unreviewed training target.”
- “The results support or do not support proceeding to a Shadow-mode P2 measurement study.”

Prohibited claims:

- automated Auditor accuracy;
- general human reliability;
- online PCT effectiveness;
- cross-model or cross-Harness generality;
- confirmatory statistical support.

## 12. P2 recommendation

Choose one:

- proceed to P2 Shadow capture with the stable label layers only;
- proceed after a targeted Codebook regression;
- repeat a smaller annotation study;
- pause because the core `ACCEPT / DO_NOT_ACCEPT` distinction is not stable enough.

List every human decision required for the P2 Work Order.

## 13. Approval

```text
Research Owner:
Methods / Statistics reviewer:
Date:
Status: APPROVED / APPROVED WITH LIMITATIONS / NOT APPROVED
Accepted limitations:
Required follow-up:
```
