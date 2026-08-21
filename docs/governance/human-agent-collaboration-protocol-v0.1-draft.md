# Human–Agent Collaboration Protocol v0.1 — Draft

## Independence and provenance

This protocol is written for the independent Process-Certified Termination project. It borrows governance mechanisms from an external human–Agent collaboration charter supplied by the project owner—decision-right separation, role isolation, evidence priority, failure preservation, staged autonomy, independent verification, and explicit amendments—but does not inherit that external project's research goals, hypotheses, experiments, terminology, or conclusions.

## 1. Decision rights

- Humans retain final authority and responsibility for goals, hard constraints, risk, main scientific claims, statistical rules, sealed data, and publication.
- Agents expand the candidate space, formalize concepts, implement code and schemas, run reversible tests, construct counterexamples, and perform consistency audits.
- A recommendation does not become authorized because it is persuasive or technically superior.

## 2. Separation of functions

No single human or Agent should unilaterally complete this full loop:

```text
define success -> change system/rule -> evaluate change -> approve change -> declare success
```

At minimum, proposal, implementation, evaluation, and normative approval must be visibly separated.

## 3. P0 autonomy

During P0, Agents operate at A0–A1:

- generate alternatives and drafts;
- create reversible repository artifacts;
- run deterministic validation;
- identify missing decisions and risks;
- submit a draft PR.

Agents may not approve the protocol, assign human authority to themselves, freeze the main experiment, or claim empirical effectiveness.

## 4. Evidence and communication

- deterministic evidence takes priority over fluent explanation;
- Agent claims must distinguish verified, not independently verified, inferred, and unresolved content;
- failures, rejected proposals, and negative results must be preserved;
- complex work should provide concise progress updates focused on decisions and risks rather than low-level logs.

## 5. Repository governance

- substantive work enters through feature branches and PR review;
- normative changes and ordinary implementation changes should be separable;
- every PR states scope, tests, research-validity risks, rollback, and unresolved human decisions;
- direct-to-main substantive changes are prohibited except unavoidable repository initialization or explicitly authorized emergency repair;
- protocol changes after freeze require an Amendment.

## 6. Experimental isolation

Experimental Agents must not access hidden evaluator details, Gold failure labels, other condition outputs, sealed tests, or Audit conclusions intended only for adjudication.

## 7. Human obligations

Human authority carries responsibility to:

- make normative decisions explicitly rather than delegating them silently;
- record why options were accepted or rejected;
- avoid lowering evidence requirements because an Agent output is fluent;
- protect sealed information;
- preserve adverse evidence;
- ensure published claims do not exceed the Capability Envelope.

## 8. Escalation

Agents must escalate changes to success semantics, hard gates, primary metrics, evaluator visibility, permissions, sealed data, irreversible operations, or publication claims.

## 9. Amendment

After approval, deviations require an Amendment Record with reason, timing relative to observed results, affected artifacts, old/new hashes, approver, and impact on confirmatory status.
