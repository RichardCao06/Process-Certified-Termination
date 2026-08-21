# P0 Threat Model

## Protected assets

- research question and claim scope;
- success semantics and hard process rules;
- primary endpoints and statistical protocol;
- sealed tests, hidden evaluator details, Gold labels, and root-cause annotations;
- raw trajectories and environment snapshots;
- evidence lineage and immutable failure records;
- repository and protocol history.

## Threats and mitigations

| ID | Threat | Failure mode | P0 mitigation |
|---|---|---|---|
| T01 | Circular self-certification | Worker implements, evaluates, and approves its own completion | separate `PROPOSED_COMPLETE` from trusted certification |
| T02 | Goal or metric drift | rules change after seeing favorable/unfavorable outcomes | Protocol Freeze + Amendment + decision history |
| T03 | Single-path process overconstraint | valid alternative workflows are rejected | partial-order obligations; hard/soft separation |
| T04 | Corrupt success | result passes while policy, integrity, or evidence is violated | non-compensatory hard gates + outcome/process dual channel |
| T05 | Evidence staleness | old passing evidence is reused after later edits | goal revision and snapshot-bound evidence lineage |
| T06 | Hidden-evaluator leakage | worker learns sealed failures and overfits | offline copied-snapshot labeling; isolated custodian |
| T07 | CoT faithfulness risk | fluent explanation is treated as true causal history | audit observable actions/state; treat explanations as claims |
| T08 | Infinite continuation | stop gate always objects and consumes budget | FCR metric, no-progress detector, round/time/token limits |
| T09 | Auditor monoculture | worker and auditor share the same blind spot | independent context, deterministic checks, human adjudication subset |
| T10 | Logging gaps | missing tool failures make trajectory look compliant | append-only event checks, replay completeness, sequence invariants |
| T11 | Evaluator tampering | tests or scoring rules are modified to pass | protected paths, hashes, diff audit, sealed evaluator isolation |
| T12 | Cost confounding | method wins only because it gets more model calls | matched-compute baselines and cost-to-certified-success reporting |
| T13 | Benchmark overfitting | process rules encode specific hidden tasks | development/held-out/sealed splits; abstract obligation classes |
| T14 | Role collapse | one actor defines, executes, evaluates, and approves | authority map and independent custodian requirement |
| T15 | Human rubber-stamping | fluent Agent draft is approved without scrutiny | decision pack with options, rejected alternatives, and explicit sign-off |
| T16 | False blocker | hard work is mislabeled impossible | blocker evidence, repeated condition signature, remaining-action check |
| T17 | Post-certification mutation | task changes after audit but before completion commit | snapshot digest recheck and compare-and-set goal revision |

## Red-team questions for every later phase

1. Can a worker obtain success by changing the test, denominator, or visibility rather than the task state?
2. Can an auditor force infinite work while appearing “safer”?
3. Can a valid alternate process be rejected because the contract encodes one preferred path?
4. Can hidden evaluator information reach the worker through logs, filenames, exceptions, or feedback?
5. Can a stale evidence item survive a later state-changing action?
6. Can a benchmark improvement be explained only by extra compute?
7. Can the same actor silently control both the rule and its approval?
