# P1 Taxonomy / Codebook Migration Record — Provisional v0.1

## Status

Provisional; finalization is blocked only by PCT-P1-D15.

## Raw layers preserved

- Human Pass A remains unchanged.
- Human Pass B remains unchanged.
- Fixture Author Intent remains a separate non-Gold reference.
- Agent advisory remains a separate non-blind, non-Gold reference.
- Human developmental adjudication remains unchanged.
- Any D15 correction will be a new append-only layer.

## Changes supported by the Pilot

### 1. Keep the two-stage stop decision

Retain:

```text
ACCEPT / DO_NOT_ACCEPT
→ specialized recommendation
```

Accept Decision was more stable than specialized Recommendation.

### 2. Retain separate Outcome and Process channels

The separation remains useful, but D15 must resolve three submitted Outcome labels that conflict with the current definition.

### 3. Keep Stop Scope and Recovery Authority as required observable fields

Both were identical in 12/12 same-annotator pairs and materially reduced Turn Stop and permission-recovery ambiguity.

### 4. Keep FIT but require review

FIT status was stable in 11/12 and exact locator in 9/12. It is suitable for Shadow diagnostics with human review, not unreviewed training Gold.

### 5. Demote detailed mechanism codes and Control Actions

Detailed Failure Codes and Control Actions remain exploratory. They should not be hard online gates in P2.

### 6. Repair Valid Alternative Path representation

Replace the current forced choice with:

```text
applicability: APPLICABLE / NOT_APPLICABLE / UNKNOWN
validity: YES / NO / UNKNOWN (only when applicable)
```

This removes the systematic `NOT_APPLICABLE` versus `UNKNOWN` collision.

### 7. Evidence Assessment requires dimension-specific examples

`scope_match` requires additional anchors and counterexamples. Evidence Assessment should remain exploratory during initial P2 Shadow capture.

## Analysis rerun

After D15:

- regenerate the adjudicated material-field layer;
- regenerate the final reliability matrix;
- update the P1 Closure Report;
- no raw A/B agreement metric is rerun or changed;
- no raw annotation is overwritten.
