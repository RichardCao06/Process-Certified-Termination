# P2 D20 工程 Smoke Remediation Protocol v0.1

根据 `PCT-P2-D20: A`，保留 D19 首次失败，仅修复获批工程问题，并在相同两条非主样本 Fixture 上重跑。

```text
Worker model: deepseek-v4-pro
Harness commit: b150a551b8d465e31e418e1b2eaf5e79bbb7d28e
Fixtures: PCT-P2-SMOKE-ENG-001, PCT-P2-SMOKE-ENG-002
Maximum trajectories: 2
Primary schedule runs: 0
Runtime tools: edit, read, write
Semantic Auditor: disabled
Reference opening: false
Runtime application: false
```

D19 v0.2 保持不变；D20 重跑生成追加式 v0.3 报告和 D21 Gate。
