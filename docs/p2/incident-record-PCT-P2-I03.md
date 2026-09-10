# PCT-P2-I03 — D19 工程 Smoke 启动与证据持久化事件

## 状态

`OPEN_REMEDIATION_AUTHORIZED`

## 首次运行

- Workflow Run：`33036996278`
- 首次失败报告：`reports/p2/engineering-smoke-run-v0.2.json`
- 首次失败 `report_digest`：`53f3779c64fe225790cc2c7117241b1d04c2d922d1a87c2477590af40278cef8`

两条工程 Fixture 都在约 0.2 秒内以退出码 1 结束；没有 SessionEvent、Request Header、Provider Chat Completion 请求、输出产物或 Candidate Stop。Key 注入和 `/models` 身份绑定成功。冻结 DSH 的 source-mode helper 要求 `TSX_TSCONFIG_PATH` 和隔离的 `DSH_AGENTS_HOME`，D19 Runner 未提供。另一个已确认问题是证据 Push 因远端并发推进而 `non-fast-forward`。

D20-A 只允许修复 source-mode 绑定、脱敏错误分类和追加式证据持久化，然后在原两条 Fixture 上重跑。正式任务、模型、Prompt、指标、分母和 Reference 规则均不得改变。
