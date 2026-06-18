# A-Girl Agent 指南

## OpenSpec（规范驱动开发）

新功能或较大改动请走 OpenSpec，不要直接改代码：

1. **Propose** — 用 Skill `/openspec-propose` 或口述「用 OpenSpec propose：xxx」
2. **Apply** — `/openspec-apply-change` 按 tasks 实现
3. **Archive** — `/openspec-archive-change` 归档

规格真相源：`openspec/specs/`。详细说明见 [docs/OPENSPEC.md](docs/OPENSPEC.md)。

**Cursor Automations**：定时「NPC训练」见 [docs/AUTOMATIONS-NPC-TRAINING.md](docs/AUTOMATIONS-NPC-TRAINING.md)（OpenSpec + 测通后 PR）；「情感 NPC 测试」见 [docs/AUTOMATIONS-DIALOGUE-QUALITY.md](docs/AUTOMATIONS-DIALOGUE-QUALITY.md)（只测不开 PR）。

## 在 Cursor 里怎么找到 OpenSpec？

### Cloud Agent（无本地仓库）

**不需要斜杠命令。** 在 Agent 对话里直接说，例如：

```text
用 OpenSpec propose：优化主动对话文案
```

### 本地开发（已 clone 仓库）

输入 `/` 后看 **Skills**，搜索 `openspec`。若看不到：`git pull origin main` → Reload Window。

## 项目要点

- 后端：`backend/app/`，测试 `cd backend && python -m pytest`
- 默认受众未成年人，安全优先
- 回复风格：口语化，每轮最多一个问句
