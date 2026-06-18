# OpenSpec 命令速查

本项目已接入 OpenSpec。在 **Agent 聊天框**输入 `/` 可看到下列命令（文件名即命令名，用**连字符** `-`，不是冒号 `:`）：

| 输入 | 作用 |
|------|------|
| `/opsx-propose` | 新建变更：proposal + specs + design + tasks |
| `/opsx-explore` | 只探讨想法，不写文件 |
| `/opsx-apply` | 按 tasks.md 实现代码 |
| `/opsx-sync` | 同步 delta spec 到主 specs |
| `/opsx-archive` | 归档已完成变更 |

**示例**：`/opsx-propose 增加睡前晚安主动问候`

若列表里没有这些命令：
1. 确认已 `git pull` 到含 `.cursor/commands/` 的最新 main
2. **Developer: Reload Window** 重载 Cursor 窗口
3. 在 **Agent** 模式聊天框输入 `/`（不是 Inline Edit）

详细说明见 `docs/OPENSPEC.md`。
