# P1 Human Decision Pack

These decisions define how the first annotation feasibility study will be interpreted. The Agent has prepared reversible tooling and recommendations but cannot approve these methodological and normative choices.

## D01 — What exactly is one annotation unit?

### A — Candidate-Stop episode plus transition localization

Annotate the trajectory prefix ending at one Candidate Stop, then identify the earliest invalid event or range inside it.

**Effect:** directly aligns labels with the later termination decision while retaining diagnostic localization.

### B — Whole trajectory only

Give one label to the entire run.

**Effect:** simpler, but multiple stops and repairs become hard to separate and First Invalid Transition is less precise.

### C — Each step independently

Label every action/observation pair without a stop-level episode.

**Effect:** granular but expensive; local labels may miss whether the complete goal was actually certifiable.

**Agent recommendation:** **A.**

---

## D02 — How should failure categories be organized?

### A — Multi-axis

Record non-exclusive mechanism codes, certification effects, and localization separately.

### B — One mutually exclusive root-cause code

Force every episode into one main category.

### C — Checklist only

Use yes/no questions without a reusable taxonomy.

**Effect:** B is easy to tabulate but cannot represent common compound failures. C helps annotation but weakens cross-task analysis and migration.

**Agent recommendation:** **A.**

---

## D03 — What verdict scale should annotators use?

### A — Four-way verdict plus separate recommendation

Use `PASS / FAIL / UNKNOWN / NOT_APPLICABLE` for outcome and process, then separately select `ACCEPT / CONTINUE / EVIDENCE_REQUIRED / HUMAN_REQUIRED / BLOCKED / NO_PROGRESS / UNDETERMINED`.

### B — Binary pass/fail

### C — One 1–5 quality score

**Effect:** B forces missing evidence into an unsupported pass or failure. C permits serious hard violations to be averaged against soft strengths.

**Agent recommendation:** **A.**

---

## D04 — How precise must First Invalid Transition be?

### A — Exact when supportable; otherwise range or unknown

### B — Always force one exact event

### C — Do not localize

**Effect:** B creates artificial precision and unreliable labels. C gives up the repair-signal research question.

**Agent recommendation:** **A.**

---

## D05 — Which P1 process labels may block certification?

### A — Only P0-approved hard-gate classes

New taxonomy codes remain descriptive until another human decision promotes them.

### B — Every taxonomy code is a hard blocker

### C — No process code can block during P1

**Effect:** B would over-constrain valid work and likely inflate False Continue. C would prevent testing corrupt-success semantics already approved in P0.

**Agent recommendation:** **A.**

Current hard-class candidates are the P0-approved classes: unauthorized action, evaluator/test/Gold tampering, ignored authoritative failure, missing/stale/scope-inadequate mandatory evidence, false environment-state claim, hidden-evaluator leakage, adverse-evidence suppression, irreversible action without approval, and bypassed human gate.

---

## D06 — What data may enter the P1 pilot?

### A — Controlled synthetic fixtures plus public/development traces

No held-out or sealed material.

### B — Natural traces only

### C — Hidden evaluator traces immediately

**Effect:** A gives known controlled counterexamples and some ecological realism without contaminating later evaluation. B makes true first-error location difficult to establish. C violates the approved sealed boundary and confounds the method with oracle access.

**Agent recommendation:** **A.**

---

## D07 — How independent must human annotation be?

### A — Two independent passes plus adjudication

When two people are unavailable, one human may perform a delayed, reordered, blind second pass, but the result must be described as intra-rater feasibility rather than independent inter-rater agreement.

### B — One unblinded pass

### C — Agent annotations only

**Effect:** B cannot estimate stability and is vulnerable to fixture expectations. C evaluates the Builder against its own definitions.

**Agent recommendation:** **A.**

Please also state the practical staffing plan:

```text
Pilot annotator 1:
Pilot annotator 2 or delayed second-pass plan:
Adjudicator:
```

---

## D08 — How large should the exploratory pilot be?

### A — Staged 12 + 30 design

- 12 calibration episodes;
- 30 blinded development episodes;
- target 10 clean/acceptable, 10 controlled single-fault, and 10 compound or natural episodes.

### B — Ten or fewer convenience episodes

### C — At least one hundred before codebook revision

**Effect:** B is fast but too fragile to reveal taxonomy overlap. C delays useful iteration and gives false formality before the codebook is stable.

**Agent recommendation:** **A.** This is an exploratory development design, not a confirmatory sample-size claim.

---

## D09 — Should structured decision checkpoints be required?

### A — Optional generally; required only in synthetic or explicitly instrumented studies

Treat checkpoint text as a Worker claim, never as independent evidence.

### B — Require detailed reasoning at every step

### C — Exclude checkpoints completely

**Effect:** B risks process performance, unavailable private reasoning, faithfulness problems, and excessive data. C removes a potentially useful link between evidence and state promotion.

**Agent recommendation:** **A.**

---

## D10 — What must happen before P1 can be declared complete?

### A — Human decisions + pilot + revision Gate

Require an approved taxonomy/codebook, preserved calibration and blinded annotations, agreement/ambiguity report, adjudication, migration log, and signed P1 Exit Gate.

### B — Schemas and tooling are enough

### C — P1 remains open until the online PCT plugin is implemented

**Effect:** B would confuse engineering readiness with annotation feasibility. C mixes P1 with later shadow/online system phases.

**Agent recommendation:** **A.**

---

## Suggested PR reply

```text
D01: A / B / C — notes:
D02: A / B / C — notes:
D03: A / B / C — notes:
D04: A / B / C — notes:
D05: A / B / C — hard-code edits:
D06: A / B / C — allowed data sources:
D07: A / B / C
  Pilot annotator 1:
  Pilot annotator 2 or delayed second-pass plan:
  Adjudicator:
D08: A / B / C — notes:
D09: A / B / C — notes:
D10: A / B / C — notes:

Other P1 constraints or risks:
```

The human record should preserve rejected alternatives and accepted limitations, especially when the same person performs multiple provisional roles.
