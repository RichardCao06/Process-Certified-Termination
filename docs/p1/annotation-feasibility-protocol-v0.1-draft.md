# Annotation Feasibility Protocol v0.1 — Draft

## Purpose

Test whether humans can apply the process taxonomy and localization rules with interpretable disagreement before any automated Auditor is treated as reliable.

This is a development feasibility study, not the confirmatory PCT experiment.

## Recommended staged design

### Stage 1 — calibration

- 12 controlled Candidate-Stop episodes;
- include clean success, clean failure, valid alternate paths, single-fault process errors, and ambiguous cases;
- annotators may discuss examples after independent first-pass labels;
- revise wording, examples, and UI/schema defects;
- preserve all original labels and revision mappings.

### Stage 2 — blinded development pilot

- 30 Candidate-Stop episodes;
- target balanced descriptive strata rather than population prevalence:
  - 10 clean or acceptably complete;
  - 10 controlled single-fault;
  - 10 compound or natural development trajectories;
- two independent annotations for the full set when staffing permits;
- if only one human is available, perform a temporally separated, reordered, blind second pass and report it as intra-rater feasibility, not independent inter-rater agreement;
- adjudicate only after both passes are frozen.

## Measures

Development diagnostics include:

- percent agreement and Cohen's kappa for nominal verdicts;
- multi-label Jaccard for failure and hard-gate codes;
- exact/range localization agreement;
- ambiguity and `UNKNOWN` rates;
- time per episode;
- codebook-change rate;
- disagreement categories;
- proportion of valid alternate paths incorrectly rejected.

No minimum agreement threshold is confirmatory or frozen in P1.

## Qualitative review

For every disagreement, classify whether it arose from:

- missing observable information;
- unclear goal/obligation;
- taxonomy overlap;
- hard/soft ambiguity;
- localization uncertainty;
- valid alternative-path disagreement;
- annotator error;
- schema or tooling defect.

## Pilot stop rules

Pause and return to human review if:

- a code repeatedly requires private reasoning rather than observable evidence;
- a valid alternative path is systematically rejected;
- P0 hard-gate mapping is insufficient or contradictory;
- hidden or held-out information would be needed;
- the annotation task requires a new normative success rule;
- sensitive data cannot be minimized.

## P1 output

The pilot should produce:

- frozen raw annotations from each pass;
- adjudication records;
- agreement and ambiguity report;
- revised taxonomy/codebook with migration table;
- an explicit list of classes that are and are not reliably annotatable;
- a recommendation on whether P2 trace infrastructure should proceed.
