# P1 Human Developmental Adjudication Gate v0.1

## Purpose

Only material disagreements in core verdicts, specialized termination recommendation, valid-alternative interpretation, or First Invalid Transition require human adjudication. Fixture Author Expectations are a developmental third reference and are not Gold.

## Allowed dispositions

For each material field, the Research Owner may select:

- `PASS_A`;
- `PASS_B`;
- `AUTHOR_INTENT`;
- `CUSTOM`;
- `RETAIN_UNRESOLVED`.

A field may remain `UNKNOWN`, `UNDETERMINED`, or unresolved when the observable trace does not support a unique answer.

## Required evidence order

1. Goal Contract and obligations;
2. observable events and authoritative evidence;
3. Pass A and Pass B rationales;
4. Fixture Author Intent;
5. Agent proposal as a non-Gold recommendation.

Do not select an answer merely because the Fixture Author intended it or because the Agent recommended it.

## Data preservation

Raw Pass A, raw Pass B, Fixture Author Intent, and the adjudicated layer must remain separate and append-only. Fine-grained Failure Code differences remain exploratory unless they alter a hard-gate interpretation.

## Participant artifact

The interactive adjudication artifact exports:

```text
PCT_P1_human_developmental_adjudication_v0.1.json
```

That export becomes the human input for the final reliability matrix, taxonomy migration, and P1 Closure Report.
