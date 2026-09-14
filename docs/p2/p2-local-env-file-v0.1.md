# 本地环境变量文件

Work Order `PCT-P2-001`。按用户要求新增 env 文件读取入口，复用 D21-A01 已允许的父进程环境变量凭证方式；原冻结 runner、授权、模型、预算和单次执行限制保持不变。

本机配置文件：`~/.config/pct/deepseek.env`，位于仓库外，权限为 `600`。填写：

```dotenv
DEEPSEEK_API_KEY=你的实际密钥
```

支持空行、整行注释和成对的单/双引号。仅接受一个 `DEEPSEEK_API_KEY`，不执行 shell 表达式，不加载模型或 endpoint 设置。空值、重复字段或其他变量会在进入执行 runner 之前被拒绝。密钥不写入命令行、日志或 Git。

填写后由 Agent 从该文件读取并启动：

```sh
python3 scripts/run_p2_d21_env.py
```

添加 `--no-model` 时不读取文件，也不传入 API key。原 `scripts/run-p2-local.sh` 仍保留终端输入/私有单行文件接口。此适配不授予新尝试或新的研究权限。
