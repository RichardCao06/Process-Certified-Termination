# D21-A01：在本机调用模型

Work Order `PCT-P2-001`。用户要求“能不能改成在本地调用模型运行”，据此将尚未使用的 D21 执行授权迁到本机。原批准、无模型证据和历史状态保留。此项修订替代 GitHub Environment 人工点击要求；不增加一次实验机会。

本机运行冻结 DeepSeek Harness，通过 DeepSeek 官方 API 调用 `deepseek-v4-pro`。Worker、提示、工具、两条 fixture、单次尝试及全部预算保持原样：每条最多 30 CNY、总计 60 CNY。不启动正式 60 条轨迹、Semantic Auditor、Reference 或在线干预。

## 已准备的本地入口

在项目目录运行：

```sh
./scripts/run-p2-local.sh
```

入口先验证冻结记录、本机沙箱和真实 Harness 无密钥启动，再检查原云端任务已取消、生成工作流已停用，以及当前 commit 已推送且通过仓库 CI。随后终端隐藏提示输入 DeepSeek API key，密钥不保存。GitHub 环境中已有的 secret 不会被导出。

也支持用户指定的仓库外私有文件，文件只能含一行 key，权限须为 `600`：

```sh
./scripts/run-p2-local.sh --credential-file /absolute/private/path/deepseek-key
```

也可从父进程 `DEEPSEEK_API_KEY` 读取。不要把 key 放入命令参数、仓库、聊天、报告或普通日志。

无模型验证：

```sh
./scripts/run-p2-local.sh --no-model
```

## 隔离与防重复

macOS Seatbelt 将 Worker 文件内容访问限制为公开的 DSH/runtime、所需系统文件、精确 patch 文件与当前临时 fixture；只有 fixture 可写。只允许访问当前本地用量代理端口，真实 API key 留在父进程。使用公开哨兵文件验证目录外读写被拒绝，并验证代理端口可达、其他端口被拒绝。随后使用与云端相同的 driver/patch 实际启动。

原云端 run `34433128526` 已取消，`p2-d21-smoke.yml` 已在 GitHub 停用。模型访问前，本地独占标记和原来的共享 Git tag `pct-p2-d21-authorization-consumed` 一起防止重复使用授权。这个 tag 只做执行协调，不触发云端模型任务；无需 GitHub 页面审批。标记创建后，即使发生失败也不得删除或自动重跑。

原始 Harness 临时目录运行后删除。脱敏证据追加到 `.pct-local/results/d21/`，包括成功、失败、用量和显式 Candidate Stop。该目录不进入 Git；运行后由 Agent 审查脱敏 JSON，再追加证据 commit。失败不自动重试，成功不自动进入下一研究阶段。

## 运行环境

本机已准备 Node `22.19.0`、pnpm `11.7.0` 和 DSH commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`，位于 Git 忽略的 `.pct-local/`。换机需重新准备这三个固定版本并通过无模型验证。GitHub 只运行仓库和 macOS 无模型 CI，不持有新本地入口的模型执行权限。
