# Human Pass B Interface Requirements v0.1

## Status

Pre-release engineering requirements. They are intentionally Case-neutral and do not disclose the selected 12 Cases or their order.

The Pass B interface may repair structural data-capture defects found in Pass A, but it must not change Codebook semantics or add Case-specific teaching.

## 1. Blinding requirements

The Pass B package must:

- contain only the precommitted 12-case subset;
- use the precommitted order;
- replace Pass A display IDs with new neutral Pass B IDs;
- display no Pass A label, rationale, confidence, timing, QC, or completion state;
- display no Fixture Author Expectation, reference answer, hidden evaluator output, or Agent annotation;
- avoid titles that reveal Case strata or injected-fault type;
- preserve the original `trajectory_id` only inside the exported machine record, not as a prominent memory cue;
- use a distinct Local Storage key from Pass A.

## 2. Semantic invariance

The following must remain unchanged from Codebook v0.2:

- Outcome `PASS / FAIL / UNKNOWN / NOT_APPLICABLE` meaning;
- Process verdict meaning;
- `ACCEPT / DO_NOT_ACCEPT` hierarchy;
- Recommendation states;
- FIT definition and D12 earliest-observable-invalid-decision rule;
- hard-gate catalog;
- `INCIDENT_ESCALATION` semantics;
- unknown recovery-authority rule;
- valid-alternative-path semantics.

The interface must not add a hint such as “this Case is about stale evidence” or “choose UNKNOWN here.”

## 3. Structural capture improvements

### Certification Effects

- `NONE` is mutually exclusive with every other effect;
- choosing a Hard Gate automatically adds `HARD_VIOLATION`;
- removing all Hard Gates does not silently remove a manually justified hard effect without warning.

### Event citations

- at least one Event citation is required before saving a complete annotation;
- clicking an Event adds or removes its ID from citations;
- setting FIT `EXACT` automatically cites that Event;
- setting FIT `RANGE` automatically cites both boundary Events;
- the annotator may cite additional intermediate Events.

### Evidence citations

- visible Evidence objects are selectable by ID;
- when Outcome, Process, or Evidence Assessment relies materially on an Evidence object, the interface prompts for at least one Evidence citation;
- an empty Evidence citation remains allowed only when the rationale explicitly states that no Evidence object exists or none is applicable;
- Evidence IDs are selected, not manually typed, to prevent case-sensitive entry errors.

### FIT structure

- `EXACT` requires one Event ID;
- `RANGE` requires ordered start and end Event IDs;
- `NONE` and `UNKNOWN` hide and clear locator fields;
- Event order is validated before export.

### Recommendation consistency

Warnings should be shown for:

- `ACCEPT` with Process `FAIL` or a Hard Gate;
- `ACCEPT` with Outcome other than `PASS` or approved `NOT_APPLICABLE`;
- `INCIDENT_ESCALATION` without incident-preservation action;
- `UNDETERMINED` when recovery authority is already explicit;
- `HUMAN_REQUIRED` when recovery authority is `SELF_SERVICE`, unless the rationale explains a separate normative Gate.

Warnings must not automatically change the label.

## 4. Save and export behavior

The interface must support:

- automatic draft save after field changes;
- explicit per-Case save;
- progress states: unstarted, incomplete, complete;
- complete Backup JSON export;
- annotations JSONL export;
- Timing CSV export;
- clipboard fallback when sandbox downloads are blocked;
- import of a Backup made by the same Pass B interface;
- a visible storage and download error message;
- export Manifest containing file hashes when browser APIs permit.

## 5. Timing

- timing begins when a Case becomes active;
- elapsed time is accumulated across visits;
- browser-hidden or long-idle periods may remain in wall-clock time and must be described as such;
- no default time or completion value is assigned to unannotated Cases.

## 6. Completion checks

A Case may be marked structurally complete only when:

- all core verdict fields are selected;
- Effects and Control Actions are non-empty;
- FIT has valid conditional fields;
- rationale meets the minimum length;
- at least one Event citation exists;
- Hard Gate relationships are internally consistent;
- no invalid ID is cited.

“Structurally complete” does not mean “semantically correct.”

## 7. Pre-release validation

Before delivery, the Builder Agent must verify:

- exactly 12 unique source trajectory IDs;
- neutral display IDs are unique and sequential;
- ordered-subset hash matches the precommitment using the original canonicalization procedure;
- the release time Gate has elapsed;
- no Pass A fields or semantic feedback are embedded;
- no author expectation or decryption key is present;
- HTML JavaScript parses;
- Backup, JSONL, CSV, and clipboard fallback work on synthetic data;
- ZIP and standalone HTML hashes are recorded;
- Fixture Author Expectations remain unopened.

## 8. Post-export freeze

After Human Pass B is uploaded:

- preserve the raw files unchanged;
- compute SHA-256 hashes;
- create a Pass B Freeze Manifest;
- verify the 12 committed Case identities and order;
- do not disclose Case-level semantic comparison until the raw A/B report is generated and frozen;
- do not open Fixture Author Expectations until the A/B report freeze is complete.
