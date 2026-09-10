# PCT-P2-I04：D19 / D20 Cordis 组合配置加载失败

## 状态

```text
DIAGNOSED_NO_MODEL_REPAIR_CANDIDATE_VALIDATED_D21_PENDING
```

## 发生了什么

D19 首次工程 Smoke 与 D20 同样本修复重跑都在产生任何 SessionEvent、Provider 请求或模型 Token 之前退出。两次失败均已保留，未被覆盖。

随后运行了不接触真实 Secret、不执行模型 Turn 的确定性诊断：冻结的 DeepSeek Harness 基线配置可以启动；D19 / D20 使用的 root-include 组合配置无论放在 PCT 仓库还是复制进冻结 DSH 仓库都会失败，精确错误为：

```text
extension "" not supported
```

## 根因

失败配置把：

```yaml
path: !!js process.env.PCT_DSH_BASE_CONFIG
```

放在 Include 插件自身的 `path` 字段。冻结版本的 Include 只会对承载的子树数据执行 lazy evaluation；它自己的 `path` 被当作字面配置使用。因此路径在扩展名解析时不是有效字符串，形成空扩展名。

## 已验证的修复候选

不再嵌套 root include，而是采用冻结 DSH 已提供的官方用户 Patch 路径：

```text
examples/headless-agent/cordis.yml
+
config/p2/dsh-engineering-smoke.patch-v0.2.yml
+
loadOptionalPatches() + boot()
```

不执行模型 Turn 的验证已确认：

- 配置可加载；
- 模型可见工具精确为 `edit / read / write`；
- Bash、Subagent、Workflow、Ralph、Todo 和 Goal 工具保持禁用；
- 模型、上下文、输出和重试配置与冻结 Profile 一致；
- Provider 请求、正式 Fixture 和主要轨迹运行均为 0。

## 治理影响

该证据足以证明新的启动配置在**无模型边界**上可执行，但不能自行授权新的生成式重跑。下一步必须由 Research Owner 对 `PCT-P2-D21` 作出决定。

Incident digest：

```text
d9ac09c47d9dd44808689aa390ee0236bfb35fad83930daa5c9fd36c0128bc45
```
