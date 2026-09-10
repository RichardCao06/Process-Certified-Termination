# P2 D21 官方 Patch 路径重跑 Preflight

当前状态：`PENDING_HUMAN_DECISION`

已完成的确定性工作：

- D19 v0.2 与 D20 v0.3 失败证据保持不变；
- 旧 root-include 组合配置的错误已确定性复现并定位；
- 官方 `loadOptionalPatches + boot` 路径已在零 Secret、零 Provider 请求、零模型 Turn 条件下通过；
- 最小工具边界为 `edit / read / write`；
- 旧 D19 活跃 Workflow 已改为 fail-closed tombstone，防止 PR synchronize 重复消耗授权；
- 20 个任务 / 60 条主要轨迹仍未运行。

只有 `PCT-P2-D21: A` 的明确人类批准，才允许物化一个新的受保护重跑 Workflow。
