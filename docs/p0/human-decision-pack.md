# P0 Human Decision Pack

This document contains the decisions that an Agent may clarify and recommend but may not approve. A concise reply template appears at the end.

## D01 — Project claim level and public name

**Question:** What is the project's current claim?

- **A — Plugin first:** “A Process-Certified Termination Plugin for DeepSeek Harness.” A general framework remains a later hypothesis.
- **B — General framework now:** Design and claim a harness-general framework from the start.
- **C — Evaluation-only:** Study process evaluation without an online termination controller.

**Impact:** B increases scope, implementation burden, confounding, and overclaim risk. C is easier but gives up the central systems contribution.

**Agent recommendation:** **A.** Prove the mechanism on one controlled model–harness configuration, then earn broader language with external-validity evidence.

---

## D02 — Primary scientific estimand and endpoint family

**Question:** What is the main causal quantity the project is designed to estimate?

- **A — Exit calibration:** reduction in False Accept, with False Continue constrained by a non-inferiority rule.
- **B — Final task success only:** increase in benchmark pass rate.
- **C — Auditor agreement only:** agreement with human process labels.
- **D — Composite score:** combine outcome, process, cost, and repair into one number.

**Impact:** B can hide corrupt success and cannot isolate termination quality. C validates a judge but not system usefulness. D creates compensability and weighting problems.

**Agent recommendation:** **A** as the primary system estimand. Keep Certified Success and Repair Conversion as important secondary outcomes. Exact margins and thresholds should be frozen later by the Methods / Statistics Lead before confirmatory experiments.

---

## D03 — Hypothesis hierarchy

**Question:** Which questions are confirmatory versus methodological or external-validity questions?

- **A — Recommended hierarchy:** RQ1 is foundational; RQ4 is the primary confirmatory system claim; RQ5 and RQ6 are secondary confirmatory; RQ2–RQ3 are method-development; RQ7 is external validity.
- **B — All RQs primary:** treat RQ1–RQ7 as co-primary.
- **C — Final success only:** make RQ6 the sole primary hypothesis.

**Impact:** B creates a severe multiplicity and interpretation burden. C skips the mechanism and calibration evidence needed to explain success or failure.

**Agent recommendation:** **A.**

---

## D04 — Initial experimental scope

**Question:** What configuration should P1–P6 target before external validity?

- **A — Recommended:** DeepSeek-V4-Pro + fixed DeepSeek Harness commit; Research Stream V primary; Research Stream S exploratory until reliable labels exist.
- **B — Multiple models and harnesses immediately.**
- **C — Semi-open tasks first.**

**Impact:** B slows mechanism development and makes causal attribution difficult. C lacks strong ground truth for the first auditor experiments.

**Agent recommendation:** **A**, with candidate DeepSeek Harness commit `141eb6fef83422698aef7a981029e843e8161534` subject to later technical freeze.

---

## D05 — Meaning of Certified Success and hard process violations

**Question:** Should a result pass be disqualified by a hard process or evidence violation?

- **A — Dual certification:** Outcome Pass is necessary but not sufficient. Authorization, integrity, current evidence, and mandatory preconditions are non-compensatory hard gates.
- **B — Outcome dominates:** process issues are reported but cannot block success.
- **C — Process dominates:** a compliant process can count as success despite a failed outcome.

**Impact:** B cannot detect corrupt success. C confuses good effort with goal completion.

**Agent recommendation:** **A.** Initial hard-gate candidates: unauthorized action, evaluator/test tampering, ignored authoritative failure, stale or missing evidence for a mandatory obligation, false claim of an environment change, hidden-evaluator leakage, and irreversible action without required approval. Efficiency and stylistic quality should remain soft metrics.

---

## D06 — Completion authority

**Question:** Who may change a goal from active work to successful completion?

- **A — Certifier authority:** Worker may submit `PROPOSED_COMPLETE`; only a trusted certification layer may commit `COMPLETE` after evidence checks.
- **B — Worker self-certification:** Worker may directly mark complete; the auditor comments afterward.
- **C — Human-only completion:** every completion requires a human.

**Impact:** B preserves the circular self-evaluation problem. C is reliable but prevents scalable autonomous experiments.

**Agent recommendation:** **A.** Human approval remains required for normative changes and selected high-risk cases, not every benchmark completion.

---

## D07 — Trace and reasoning-data policy

**Question:** What process data may the project require?

- **A — Observable trace only:** events, actions, tool outcomes, state changes, evidence links, and short structured decision checkpoints; no private or hidden chain-of-thought requirement.
- **B — Full textual reasoning:** require detailed model reasoning for every step.
- **C — Tool calls only:** record actions and results, with no explicit claim/evidence checkpoints.

**Impact:** B introduces faithfulness, privacy, availability, and product-policy risks. C is cheaper but may be insufficient to audit unsupported state promotions.

**Agent recommendation:** **A.** Treat worker explanations as claims that require evidence, never as self-authenticating proof.

---

## D08 — Human role assignments and minimum separation

**Question:** Who occupies the human authority roles?

Required fields:

- Research Owner:
- Methods / Statistics Lead:
- Domain Lead:
- Data Steward:
- Independent Custodian:

**Options:**

- **A — Full separation:** different people for all roles.
- **B — Minimal viable separation:** one person may hold Research Owner, Domain Lead, and Data Steward during development; Methods decisions receive independent review; the Independent Custodian must remain separate before sealed work.
- **C — Single-person project:** one person holds every role.

**Impact:** C is practical for drafting but cannot support strong sealed-test or independent-approval claims.

**Agent recommendation:** **B** for early development. No sealed or confirmatory release should occur until the Custodian role is independent and the statistical protocol receives independent review.

---

## D09 — Sealed data and hidden-evaluator boundary

**Question:** How should hidden evaluator information be used?

- **A — Blind benchmark mode:** hidden evaluators label copied candidate-stop snapshots offline; details never return to the worker or online auditor. A separate oracle condition is reported only as an upper bound.
- **B — Feedback mode:** hidden-test failures are sent back to the worker for repair.
- **C — No sealed split:** all evaluator information remains visible.

**Impact:** B and C confound the method with benchmark-oracle access and can overfit the test set.

**Agent recommendation:** **A.** Preserve development, validation, held-out, and sealed partitions with explicit access logs and hashes.

---

## D10 — Human–Agent collaboration and repository governance

**Question:** Should the project adopt the draft collaboration protocol?

- **A — Adopt with PR-based governance:** human normative authority, agent A0–A1 in P0, role separation, failure preservation, deterministic validation, and no substantive direct-to-main changes.
- **B — Informal collaboration:** decisions remain in chat without structured records.
- **C — Agent-led governance:** Agent may approve low-risk normative changes.

**Impact:** B weakens traceability and makes post-result rule changes hard to detect. C conflicts with the project's own separation-of-authority thesis.

**Agent recommendation:** **A**, with amendments recorded when the protocol changes.

---

## Suggested reply format

Copy and fill this block in the PR discussion or chat:

```text
D01: A / B / C — notes:
D02: A / B / C / D — notes:
D03: A / B / C — notes:
D04: A / B / C — notes:
D05: A / B / C — hard-gate edits:
D06: A / B / C — notes:
D07: A / B / C — notes:
D08: A / B / C
  Research Owner:
  Methods / Statistics Lead:
  Domain Lead:
  Data Steward:
  Independent Custodian:
D09: A / B / C — notes:
D10: A / B / C — notes:
```

Approval should record rejected options and reasons, not only the selected letter.
