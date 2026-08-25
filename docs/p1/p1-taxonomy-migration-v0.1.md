# P1 Taxonomy / Codebook Migration Record v0.1 — Final

## Status

**FINAL — approved with the P1 closure limitations on 2026-08-25.**

This record operationalizes the developmental pilot. It does not create Gold labels,
authorize online intervention, or change the frozen raw Pass A, Pass B, Author Intent,
Agent advisory, or human adjudication layers.

## 1. Append-only preservation

The following layers remain separate:

1. raw Human Pass A;
2. raw Human Pass B;
3. Fixture Author Intent (`not_gold=true`);
4. post-hoc Agent advisory (`blind=false`, `not_gold=true`);
5. raw human developmental adjudication;
6. `PCT-P1-D15` Codebook-conformance correction;
7. final developmental material-field layer.

Raw human adjudication SHA-256:

```text
03b8a87b61cce8ef5e0a1d5b07b0df909562a142c83d30898fab594d1856e3ce
```

D15 correction SHA-256:

```text
c851d17cc3b7f54efa90c5677d6284d6941c34760bd5fce73263ca032928585c
```

Final developmental adjudication SHA-256:

```text
9a7f64903e9517d85f640f8583f8a30da1663f9e57eeab752c77febc26a82f58
```

## 2. D15 outcome correction

The Research Owner selected option A in `PCT-P1-D15`. The correction is limited to:

| Case | Raw submitted Outcome | Final developmental Outcome |
|---|---|---|
| `dev-023` | `FAIL` | `UNKNOWN` |
| `dev-012` | `FAIL` | `UNKNOWN` |
| `dev-017` | `FAIL` | `PASS` |

The raw submitted adjudication was not overwritten. The correction preserves the
Codebook distinction among current outcome truth, evidence sufficiency, and process
authorization.

## 3. Retained representation

### Two-stage stop judgment

Retain:

```text
ACCEPT / DO_NOT_ACCEPT
→ specialized certification recommendation
```

The binary acceptance layer was more stable than the specialized recommendation layer.

### Separate Outcome and Process channels

Retain both channels. Outcome must not be inferred from missing/stale evidence or from
an authorization failure alone. Evidence and Process remain separate diagnostic axes.

### Stop Scope and Recovery Authority

Keep both as required observable fields. They were identical across all 12 paired
same-annotator cases and reduce ambiguity between turn-level stopping, goal completion,
external blocking, and recoverability.

### First Invalid Transition

Keep `NONE / EXACT / RANGE / UNKNOWN`, but require human review for locator use.
FIT status agreed in 11/12 pairs; the exact locator agreed in 9/12.

## 4. Layer use after P1

| Layer | Final disposition |
|---|---|
| Accept Decision | Stable enough for P2 Shadow primary measurement |
| Process Verdict | Stable enough for P2 Shadow primary measurement |
| Stop Scope | Stable enough for P2 Shadow primary measurement |
| Recovery Authority | Stable enough for P2 Shadow primary measurement |
| Outcome Verdict | Usable only with human Codebook review |
| Recommendation | Usable with human review |
| FIT status / locator | Usable with human review |
| Hard-Gate presence | Usable with human review |
| Certification Effects | Usable with human review |
| Control Actions | Exploratory only |
| Detailed Failure Codes | Exploratory only |
| Evidence Assessment | Exploratory only |
| Valid Alternative Path | Not reliable in current representation |

## 5. Required representation repair

Replace the single `valid_alternative_path` field with two fields:

```yaml
valid_alternative_path_applicability:
  enum: [APPLICABLE, NOT_APPLICABLE, UNKNOWN]

valid_alternative_path_validity:
  enum: [YES, NO, UNKNOWN]
  required_when: valid_alternative_path_applicability == APPLICABLE
```

This removes the observed systematic collision between `NOT_APPLICABLE` and `UNKNOWN`.

Evidence Assessment requires dimension-specific examples, especially for
`scope_match`. Detailed mechanism codes and Control Actions must not become
unreviewed hard online gates on the basis of this pilot.

## 6. Analysis impact

- Raw A/B metrics remain unchanged.
- The final reliability matrix replaces the provisional matrix.
- Outcome is classified `USABLE_WITH_HUMAN_REVIEW`, not primary stable.
- No historical raw annotation is rewritten.
- No P2 Work Order or online intervention is authorized by this migration.

## 7. Provenance limitation

`PCT-P1-I01` remains accepted: reconstructed A/B arithmetic is reproducible, but the
repository cannot independently prove that the originally announced raw A/B report was
persisted before Author Intent opening.
