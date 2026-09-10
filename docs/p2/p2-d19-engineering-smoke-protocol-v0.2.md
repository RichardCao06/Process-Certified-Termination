# P2 D19 工程 Smoke 协议 v0.2

## 目的

只验证真实 DeepSeek API、冻结 DeepSeek Harness、最小工具面、显式 Candidate-Stop Sidecar、事件日志、资源闸门和脱敏结果持久化能否贯通。

## 范围

- 最多 2 条公开合成 Fixture；
- 不属于冻结 20 个任务，也不属于 60 条正式运行计划；
- 不进入主要分析分母；
- Worker 只看到 `read/write/edit`；
- 无 Bash、Job、Subagent、Workflow、Ralph、Todo、Reference 或 Semantic Auditor；
- Candidate Stop 通过 `.pct/candidate-stop-proposal.json` 显式声明，由只读 Task Adapter 绑定；
- Worker 子进程只获得随机本地代理凭据，真实 DeepSeek Key 不进入其环境。

## Gate

任何一项不满足都保留为 `BLOCKED` 或 `FAIL`：

- 完整仓库验证；
- 精确 DSH Commit；
- 当前 Profile 的新鲜 Provider 绑定；
- 实际 Wire Tool Catalog 与 Request Header Tool Catalog 均精确匹配；
- Usage 存在且所有资源上限满足；
- 产物 Validator 通过；
- Candidate-Stop Proposal 与 Fixture 预期完全一致；
- `applied_to_runtime=false`。

通过也不授权 60 条正式 Pilot；下一步仍是 `PCT-P2-D20` 人类 Gate。
