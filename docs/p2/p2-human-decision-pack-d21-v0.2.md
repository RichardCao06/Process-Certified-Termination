# PCT-P2-D21：是否授权一次官方 Patch 路径的同样本受控重跑

## 为什么现在需要人类决定

D19 与 D20 的失败已被追加式保留。新的不调用模型诊断已经把问题定位到旧 Cordis root-include 组合配置，并验证了冻结 DeepSeek Harness 提供的官方 Patch 路径可以在无模型边界下正常启动，同时保持精确的最小工具权限。

这项证据证明“新的启动路径可执行”，但**不等于**自动获得再次调用 Worker 模型的授权。D21 只决定是否允许一次新的工程性重跑，不决定是否启动 60 条正式自然任务。

## 已冻结、不允许改变的条件

```text
Worker model: deepseek-v4-pro
Frozen DSH commit: b150a551b8d465e31e418e1b2eaf5e79bbb7d28e
System prompt: unchanged
Engineering fixtures: PCT-P2-SMOKE-ENG-001 / 002 only
Maximum trajectories: 2
Context cap: 128000 tokens
Output cap: 16000 tokens per request
Cumulative cap: 200000 tokens per trajectory
Monetary cap: 30 CNY per trajectory
Model-facing tools: edit / read / write only
Semantic Auditor: disabled
Reference opening: false
Runtime application: false
Online intervention: false
Primary 20-task / 60-trajectory schedule: unauthorized
```

## 新证据

### 旧组合配置诊断

- 冻结 DSH 基线：PASS；
- 旧 overlay 在仓库外和复制到 DSH 内部均：FAIL；
- 根因分类：`ROOT_INCLUDE_OWN_PATH_JS_EXPRESSION_NOT_EVALUATED`；
- Provider 请求和模型 Turn：0。

### 官方 Patch 路径验证

- `examples/headless-agent/cordis.yml + dsh-engineering-smoke.patch-v0.2.yml`：PASS；
- 模型可见工具精确为 `edit / read / write`；
- Bash、Subagent、Workflow、Ralph、Todo 和 Goal 工具全部关闭；
- Model/Profile、上下文、输出和重试配置一致；
- Provider 请求和模型 Turn：0。

## 方案 A — 推荐：批准一次追加式受控重跑

允许在 `p2-natural-pilot` Environment Gate 下：

1. 只运行原来的两条非主样本工程 Fixture；
2. 使用已经通过无模型验证的官方 Patch 路径；
3. 每条 Fixture 只运行一次，不做质量型重试；
4. 输出新的 `v0.4` 追加式结果，绝不覆盖 D19 v0.2 或 D20 v0.3；
5. 无论成功或失败，都冻结脱敏证据并返回下一项人类 Gate；
6. 不触发、也不授权 60 条正式轨迹。

**优点**：最小范围检验修复是否真正到达模型请求、工具调用、Candidate Stop 与确定性 Validator 链路。  
**风险**：会产生最多两条工程模型调用及相应费用；修复仍可能在更后面的运行阶段失败。  
**补偿措施**：同样本、单次尝试、原预算、Environment 审批、追加式证据、零自动扩大。

## 方案 B — 停在无模型证明

不再进行生成式调用。保留“配置与权限边界可启动”的证据，但不验证完整 Worker 执行链路，也不能进入正式自然任务 Pilot。

## 方案 C — 放弃当前 DSH 执行路线并重新设计

停止当前冻结 Harness 上的工程重跑，另行建立新的 Harness / Adapter / Worker 配置 Work Order。该方案改变研究实施路线，需要新的范围、兼容性和预算决策。

## Agent 建议

选择 **A**。当前修复候选已经通过无模型的基线、Patch、插件挂载、工具边界和 Profile 检查；一次同样本、同预算、追加式重跑是最小且可证伪的下一步。

## PR 评论模板

接受建议时，在 PR #3 评论：

```text
PCT-P2-D21: A

Additional constraints or amendments:
```

不批准任何新模型调用时：

```text
PCT-P2-D21: B

Additional constraints or amendments:
```

重新设计路线时：

```text
PCT-P2-D21: C

Additional constraints or amendments:
```
