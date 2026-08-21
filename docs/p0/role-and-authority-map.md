# Role and Authority Map

## Human roles

| Role | Final authority | P0 responsibility | Required separation |
|---|---|---|---|
| Research Owner | research purpose, claim scope, Goal Contract, phase gates, publication | approve D01, D03, D04, D06, D08, D10 | must not alone control sealed data and final certification claim |
| Methods / Statistics Lead | estimands, primary comparisons, margins, sample design, exclusions | approve D02 and D03; plan later thresholds | independent review required before confirmatory freeze |
| Domain Lead | severe process violations, procedural integrity, human-review semantics | approve D05 and later Codebook | must distinguish hard rules from preferences |
| Data Steward | trace fields, privacy, retention, release, schema semantics | approve D07 | keep facts, model claims, and human labels distinct |
| Independent Custodian | sealed tests, Gold labels, hashes, access logs, unsealing | approve and operate D09 | must be independent before sealed work |

## Agent roles

| Role | Main work | Prohibited authority |
|---|---|---|
| Research Builder Agent | formalization, code, schemas, tests, simulation, documentation | cannot approve normative rules or claims |
| Red-Team Agent | counterexamples, gaming attacks, leakage and loop analysis | cannot approve its own mitigation |
| Audit Agent | read-only protocol/code/data consistency, replay, evidence checks | cannot define Gold or edit task state |
| Experimental Agent | execute tasks and propose completion | cannot access hidden labels or certify success |

## Minimal viable staffing recommendation

During P0–P2, one person may provisionally combine Research Owner, Domain Lead, and Data Steward. The statistical plan should receive independent review before confirmatory freeze, and the Independent Custodian must be a separate person or genuinely isolated authority before sealed testing.

## Decision rule

Agent recommendations are inputs. A normative decision becomes effective only when the authorized human role records approval, rationale, rejected options, and accepted risks.
