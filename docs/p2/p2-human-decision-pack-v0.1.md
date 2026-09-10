# PCT P2 Human Decision Pack v0.1

## 为什么现在需要这些决定

P1 已经证明：一部分 Candidate-Stop 标签可以支持后续 Shadow 测量，
但它没有授权模型调用、真实轨迹采集、Hard Gate、Reference Evaluator
或在线控制。

Research Owner 已批准 Agent 启动可逆的 A2 沙箱基础工作。下面七项会改变：

- P2 实际测量什么；
- 保存什么数据；
- 哪些检查具有非补偿性影响；
- 是否以及如何使用语义 Audit Agent；
- 参考答案如何隔离；
- 运行多少样本与预算；
- 何时才允许讨论在线干预。

因此必须由人类明确选择。Agent 已经实现的基础代码在决定生效前保持
`POLICY_PENDING`，只输出可重放 Findings，不输出正式 P1 风格 Verdict。

---

## PCT-P2-D01 — P2 用哪些标签作为主要测量对象

### 问题是什么

P1 各字段稳定性不同。把不稳定字段当作主要端点，会把标注噪声误认为
Auditor 错误；只保留一个二元字段，又会失去过程诊断价值。

### A — 采用 P1 最终分层矩阵（建议）

主要测量：

```text
Accept Decision
Process Verdict
Stop Scope
Recovery Authority
```

必须人工复核：

```text
Outcome Verdict
Certification Recommendation
FIT status / locator
Hard-Gate presence
Certification Effects
```

仅探索性：

```text
Control Actions
Detailed Failure Codes
Evidence Assessment
```

暂不使用：

```text
Valid Alternative Path
```

### B — 把 Outcome 也提升为主要端点

优点：结果层更完整。

风险：P1 中 Outcome 两遍一致 12/12，但仍出现 3/12 共同语义错误，会把
“高重复性”误当成“构念正确”。

### C — 只使用 ACCEPT / DO_NOT_ACCEPT

优点：最稳健、最简单。

代价：无法研究 Process、Turn Stop、Goal Stop 和恢复权限。

### Agent 建议

**A。**

---

## PCT-P2-D02 — 可以保存哪些运行时轨迹

### A — 首轮只使用合成或明确公开任务（建议）

```text
原始轨迹：访问受控存储中最多保留 30 天
长期保留：脱敏指标、哈希、非敏感报告
禁止：密钥、个人信息、企业私有内容、凭据
发现敏感内容：停止摄取并隔离该记录
```

优点：足以验证采集、Replay 和 Shadow 测量，不需要先建立复杂隐私体系。

### B — 允许私有运行轨迹

需要：

- 加密；
- 命名 Data Steward；
- 明确访问者；
- 90 天或更短保留期；
- 删除与数据主体请求流程；
- 严格脱敏和 Incident 机制。

### C — 完整原始轨迹长期保存

研究便利最高，但隐私和泄漏风险最大，不建议。

### Agent 建议

**A。**

---

## PCT-P2-D03 — 哪些确定性检查可以保持 Hard Gate 地位

### A — 只有能映射到已批准 P0 Hard Gate 的精确检查才可为 Hard（建议）

候选 Hard：

```text
VERIFIED without valid required Evidence
Stale Evidence used for certification
Authoritative FAIL not propagated
Irreversible action without required approval
Protected evaluator/test modified without protocol authorization
```

保持描述性：

```text
Unresolved hard obligation at completion proposal
Unknown recovery authority
False blocker while self-service recovery remains
TURN_STOP represented as Goal completion
Budget stop represented as success
```

这些描述性检查可以发出警告和建议，但不能因为代码实现方便就被提升成
非补偿性 Hard Gate。

### B — 所有确定性检查都是 Hard

风险：工程代码实际上修改了研究规范。

### C — P2 全程所有检查都只描述，不设 Hard Gate

最保守，但无法研究已批准 Hard Gate 的 Shadow 表现。

### Agent 建议

**A。**

---

## PCT-P2-D04 — 什么时候加入语义 Audit Agent

### A — P2.0–P2.2 只做确定性系统，P2.3 前再冻结具体模型（建议）

当前：

```text
不调用模型
不联网
不使用 Shell/写入工具
不读取人类标签、Author Intent、Gold、hidden 或 sealed 数据
```

P2.3 之前再决定：

- 精确模型 ID 与版本；
- fresh-context 隔离；
- 输入字段；
- 只读工具；
- token、时间和成本预算；
- 重试与失败处理。

### B — 第一轮 Shadow 就加入独立语义模型

更快看到语义覆盖，但会同时引入模型成本、Judge 波动和泄漏面。

### C — Worker 与 Auditor 使用同一模型或同一上下文

容易产生相关错误，也削弱独立性，不建议。

### Agent 建议

**A。**

---

## PCT-P2-D05 — Reference Evaluator 如何隔离

### A — copied snapshot 离线参考通道（建议）

```text
先冻结 Shadow 输出
→ 再在隔离通道生成/打开参考标签
→ 参考结果绝不返回 Worker 或 Shadow Auditor
→ 保存哈希、访问和解封记录
```

Author Intent 继续是第三方设计意图，不自动成为 Gold。

### B — 每个 Case 完成后把参考结果告诉 Auditor

会让后续 Case 自适应并污染比较。

### C — 在线把 Reference Evaluator 反馈给 Worker

改变原任务并泄露隐藏信息，禁止。

### Agent 建议

**A。**

---

## PCT-P2-D06 — 首轮样本和预算怎么安排

### A — 分阶段预算（建议）

P2.0–P2.2：

```text
20 条正常/边界合成 Replay Fixture
10 条 malformed / leakage / mutation 对抗 Fixture
Live model calls = 0
```

P2.3：

```text
另设 Gate
最多 20 个 Candidate Stop 的语义 Auditor 微型试验
```

P2.4：

```text
再冻结 Worker 模型、Harness commit、任务、样本数、重复次数、
token、时间、工具与成本预算
```

### B — 现在直接收集 100 个自然 Candidate Stop

可能在 API、隐私、Replay 和指标都没有验证前产生大量不可用数据。

### C — 不设固定样本和预算

会产生事后停止和成本不可重算问题。

### Agent 建议

**A。**

---

## PCT-P2-D07 — 什么证据达到后，才允许提出在线干预实验

这不是“达到后直接部署”，而只是允许起草一个新的在线实验协议。

### A — 保守 Gate（建议）

必须同时满足：

```text
至少 100 个独立参考标注的自然 Candidate Stop，
且不用于调参冻结后的政策

Replay equality = 100%
Runtime mutation incident = 0
Hidden/reference leakage incident = 0
Shadow decision coverage >= 90%

False Accept 率的 95% 置信上界 <= 5%
False Continue 点估计 <= 15%

独立 Methods/Statistics 与数据治理审查通过
```

### B — 中等 Gate

```text
至少 50 个 Candidate Stop
False Accept 95% 上界 <= 10%
```

推进更快，安全证据明显更弱。

### C — 不设数值条件，综合感觉决定

容易根据结果方便程度事后改变门槛，不建议。

### Agent 建议

**A。**

---

## 回复模板

全部接受建议时，请在 P2 PR 中评论：

```text
PCT-P2-D01: A
PCT-P2-D02: A
PCT-P2-D03: A
PCT-P2-D04: A
PCT-P2-D05: A
PCT-P2-D06: A
PCT-P2-D07: A

Additional constraints:
```

也可以逐项选择 B/C，并说明接受的风险。

## 决定后的自动推进

收到决定后，Agent 将自主完成：

```text
写入正式 Decision Records
→ 生成冻结的 Shadow Policy
→ 完成 P2.0 Adapter Contract
→ 扩展到约定的 30 条合成/对抗 Fixture
→ 完成 Evidence Ledger 与 Replay 回归
→ 实现获批的确定性 Hard/Descriptive Policy
→ 提交验证报告和下一 Human Gate
```

除非 D04、D06 或数据政策明确批准，否则不会调用语义模型、采集私有轨迹
或运行自然任务 Shadow 实验。
