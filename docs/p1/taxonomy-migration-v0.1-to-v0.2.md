# P1 Annotation Migration v0.1 to v0.2 Draft

## Purpose

Calibration showed that coarse stop acceptance was more stable than detailed diagnosis. This migration changes derived annotation semantics without modifying either original annotation pass.

## Migration table

| v0.1 behavior | v0.2 draft behavior |
|---|---|
| Outcome sometimes included evidence or process defects | Outcome evaluates OUTCOME, DELIVERABLE, and INVARIANT obligations only |
| Missing, stale, or narrow evidence was sometimes labeled Outcome FAIL | Use Outcome UNKNOWN unless current authoritative evidence establishes failure |
| Candidate Stop had no scope | Add `stop_scope` to separate turn stop, completion proposal, human escalation, blocker, and budget stop |
| Certification effects and controller actions were mixed | Keep `certification_effects` bounded and add `control_actions` |
| FIT locator was optional | EXACT requires event ID; RANGE requires start and end IDs |
| Alternative path had no N/A value | Add `NOT_APPLICABLE` |
| Permission recovery was implicit | Add `recovery_authority` and do not infer it from error text alone |
| No incident-specific recommendation | PCT-P1-D13 proposes `INCIDENT_ESCALATION` |

## Preservation

- Human Pass 1 remains unchanged.
- Agent Blind Pass 1 remains unchanged.
- Comparison and QC reports remain unchanged.
- Adjudication and regression expectations are new derived records.
- Any migrated record must cite its source annotation IDs and the approving decision.

No v0.1 failure code is deleted in this draft. Detailed mechanism labels remain developmental until later reliability evidence supports a freeze.
