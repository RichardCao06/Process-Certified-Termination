# Role and Authority Map — P0 Approved

## Human assignments

| Role | Identity | Status | Current authority | Mandatory later gate |
|---|---|---|---|---|
| Research Owner | RichardCao06 | Assigned | project purpose, claim scope, Goal Contract, P0/P1 gates | cannot alone certify sealed claims |
| Domain Lead | RichardCao06 | Provisional | candidate hard-process semantics and development interpretation | hard-gate revisions remain explicit human decisions |
| Data Steward | RichardCao06 | Provisional | development trace schema, privacy/retention drafts | cannot serve as independent sealed custodian |
| Methods / Statistics Lead | Unassigned | Deferred | none yet | independent appointment or review required before confirmatory protocol freeze and statistical threshold approval |
| Independent Custodian | Unassigned | Deferred | none yet | separate authority required before held-out/sealed evaluator creation, access, or unsealing |

The minimum viable separation approved in PCT-P0-D08 is sufficient for P1 descriptive, taxonomy, annotation-feasibility, and development work. It is not sufficient for confirmatory or sealed-test claims.

## Agent roles

| Role | Main work | Prohibited authority |
|---|---|---|
| Research Builder Agent | formalization, code, schemas, tests, simulation, documentation | cannot approve normative rules or claims |
| Red-Team Agent | counterexamples, gaming attacks, leakage and loop analysis | cannot approve its own mitigation |
| Audit Agent | read-only protocol/code/data consistency, replay, evidence checks | cannot define Gold or edit task state |
| Experimental Agent | execute tasks and submit `PROPOSED_COMPLETE` | cannot access hidden labels or commit `COMPLETE` |

## Authority invariant

No single actor may define the success rule, implement the method, produce the only evidence, evaluate that evidence, approve the rule, and announce success.

## Decision effectiveness

Agent recommendations are inputs. A normative decision becomes effective only after the authorized human role records the selected option, rationale, rejected alternatives, accepted risks, identity, and effective date.
