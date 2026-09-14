# D21-A：批准后的工程执行

Work Order: `PCT-P2-001`。批准记录：[D21 human approval](../../governance/p2-human-approval-d21-v0.1.json)。用户在当前任务明确回复“批准”；此记录不冒充 PR 评论或 GitHub Deployment Review。

## 执行范围

只执行 `PCT-P2-SMOKE-ENG-001`、`002` 各一次。固定 `deepseek-v4-pro`、DSH commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`，使用原定官方 patch；不改提示、样本、模型或预算。每条上限为 1800 秒、20 个逻辑模型请求、50 次工具调用、2 个 Candidate Stop、128000 上下文、单次输出 16000、累计 200000 tokens、30 CNY；合计最多 60 CNY。金额是冻结策略的保守计费保护估算，不是实际账单。

沿用已批准的 transport 重试规则；不进行质量重试或 partial-stream 重试。若流中断、统计缺失或上限检查失败，停止该执行路径并保留失败。D21 新增的代理包装保证前一请求的用量记账完成后再接受下一请求，历史 D19/D20 脚本保持原样。

## 启动与授权

1. 静态检查批准、哈希、历史证据及研究范围。
2. 从冻结 DSH source 安装锁定依赖，用实际 D21 driver 和 dummy credential 启动官方 patch，不发起模型 turn；实际工具集合必须恰好为 `edit/read/write`，模型配置及禁用能力必须匹配。
3. 进入 `p2-natural-pilot` Environment，由 `RichardCao06` 在 GitHub 审核待执行的 commit。单一 Owner 的 `prevent_self_review=false` 允许 Owner 自己触发和审核；Agent 不代替这项人工 review。
4. 创建不可重复的 Git ref `refs/tags/pct-p2-d21-authorization-consumed`，绑定当前 commit；已存在即失败。工作流重跑（`run_attempt > 1`）拒绝执行；不要删除该标记。即使预模型阶段随后发生基础设施失败，也保留标记，避免自动重复消费授权。
5. 在受保护 runner 重复无模型检查，然后仅在执行步骤挂载 API key。先重新读取官方 `/models` 核对精确模型，再执行两条固定 fixture。

拉取请求仅运行无模型检查；首次推送批准记录或明确 workflow dispatch 才会申请受保护工程任务。修改普通文件不会自动触发额外模型执行。

## 证据与成功含义

结果使用新 v0.4 文件，每个文件以独占创建方式写入，保留成功、失败和异常。工作流只上传白名单中的 JSON：冻结绑定、计数、用量、哈希、确定性 artifact validator 结果、显式 Candidate-Stop sidecar 绑定及退出分类。原始模型/工具事件只在父进程内存和临时 Harness 工作目录流转；临时目录结束后删除，不上传原始 transcript、工具内容或密钥。

PASS 必须同时包含实际模型请求、精确工具边界、正确 artifact、显式 sidecar 绑定和无违规退出。此次只验证模型请求→工具→artifact→Candidate Stop 的工程链路，尚未完成实际任务上的完整 Shadow Auditor 接入或效果比较。`mode=SHADOW`、`applied_to_runtime=false`；60 条主样本、Semantic Auditor、Reference opening 和在线干预仍不获授权。

运行后下载脱敏证据，追加结果记录，绑定源 commit、Actions run 和后续证据 commit 的成功 CI，然后返回下一项研究决策。没有结果时不声称工程闭环完成。
