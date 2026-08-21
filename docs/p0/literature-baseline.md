# Literature and Engineering Baseline — P0 Snapshot

Verified on **2026-08-21**. This is a positioning baseline, not an exhaustive review. Primary sources are preferred.

## Closest research directions

### Process evaluation as a separate dimension

- Gritta et al. (2026), **Process Evaluation for Agentic Systems**, Findings of EACL 2026. The paper argues that outcome-only evaluation can hide skipped steps, hallucinated tool use, and outdated-knowledge shortcuts; it reports a small feasibility study of automatic process evaluation.  
  Primary source: https://aclanthology.org/2026.findings-eacl.140/

**Implication:** “process matters” is not the novelty. The project must test incremental value and online termination control.

### Procedure-aware corrupt-success detection

- Cao, Driouich, and Thomas (2026), **Beyond Task Completion: Revealing Corrupt Success in LLM Agents through Procedure-Aware Evaluation**, arXiv:2603.03116. It formalizes complementary procedural dimensions and reports that outcome success can conceal process violations in its benchmark setting.  
  Primary source: https://arxiv.org/abs/2603.03116

**Implication:** Process constraints should be non-compensatory only when they are human-approved hard requirements.

### Runtime assurance through harness hooks

- Lu et al. (2026), **SkillSentry: Reliable Skill Execution for LLM Agents via Runtime Assurance**, arXiv:2608.09253. It extracts procedural guidance, monitors execution, and uses runtime checks to improve skill reliability across Claude Code and Codex configurations.  
  Primary source: https://arxiv.org/abs/2608.09253

**Implication:** Hook-based monitoring is feasible. The open gap is evidence-grounded, multi-path-compatible completion certification and its incremental value over strong outcome verifiers.

### Environment-aware Agent-as-a-Judge

- Shi et al. (2026), **AJ-Bench: Benchmarking Agent-as-a-Judge for Environment-Aware Evaluation**, arXiv:2604.18240. It evaluates information acquisition, state verification, and process verification, finding gains over text-only judges while retaining substantial challenges.  
  Primary source: https://arxiv.org/abs/2604.18240

**Implication:** The auditor should be able to inspect authoritative state, but must remain bounded and independently calibrated.

### External task state and read-only audit

- Ma et al. (2026), **LongHorizon-Harness: Advancing Long-Horizon Agents for Real-World Tasks**, arXiv:2608.01964. It separates task-state management, fresh execution, and read-only audit; the paper reports gains across multiple long-horizon benchmarks and model/harness configurations.  
  Primary source: https://arxiv.org/abs/2608.01964

**Implication:** Separating execution from state certification is a strong engineering precedent, but it does not by itself answer PCT's exit-calibration and process-feedback questions.

### Failure localization from execution trajectories

- Barke et al. (2026), **AgentRx: Diagnosing AI Agent Failures from Execution Trajectories**, arXiv:2602.02475. It provides annotated failed trajectories and a constraint-based diagnostic framework for localizing critical failure steps.  
  Primary source: https://arxiv.org/abs/2602.02475

**Implication:** First Invalid Transition localization is plausible but remains an empirical challenge, especially on long trajectories.

## DeepSeek Harness engineering baseline

The current candidate upstream baseline is:

- repository: `deepseek-ai/deepseek-harness`;
- branch: `master`;
- commit: `141eb6fef83422698aef7a981029e843e8161534`;
- commit date: 2026-08-19;
- release merge: `dsh@0.1.0-rc.8`.

Relevant extension points already documented upstream include:

- `session/event` for durable trajectory facts;
- `tools/result` for frozen authoritative tool outcomes;
- `agent/turn-stopping` for the natural-stop checkpoint and steering continuation;
- goal state and goal-round plugins, which currently defer independent evaluator-backed certification.

The upstream commit is only a candidate until the human project owner approves the initial configuration and a technical compatibility check is completed.

## P0 gap statement

The project targets a narrower unresolved question:

> In a harness that already has outcome verification and tool-loop control, does a separate, evidence-grounded process-certification channel add measurable information, improve stop calibration, and produce repair feedback that increases trustworthy task completion under matched compute and evaluator visibility?
