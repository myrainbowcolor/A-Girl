# 用 OpenSpec 开发 A-Girl

本项目已接入 [OpenSpec](https://github.com/Fission-AI/OpenSpec)（规范驱动开发，SDD）。先对齐「要做什么」，再写代码。

## 目录结构

```text
openspec/
  config.yaml          # 项目上下文与 artifact 规则（AI 会读取）
  specs/               # 当前系统的「真相源」——已实现能力的需求规格
    chat-orchestration/
    persona/
    memory/
    ...
  changes/             # 进行中的变更（proposal / specs / design / tasks）
    archive/           # 已完成并归档的变更
.cursor/
  commands/            # Cursor 斜杠命令：/opsx:propose 等
  skills/              # OpenSpec Agent Skills
```

## 日常流程（OPSX）

| 步骤 | 命令 | 说明 |
|------|------|------|
| 1. 提想法 | `/opsx:propose 你的功能描述` | 生成 change 文件夹：proposal、specs、design、tasks |
| 2. 探讨 | `/opsx:explore …` | 只讨论、不改文件（可选） |
| 3. 实现 | `/opsx:apply` | 按 tasks.md 逐项实现并勾选 |
| 4. 同步 | `/opsx:sync` | 将 delta spec 合并到主 specs（可选） |
| 5. 归档 | `/opsx:archive` | 变更移入 archive，更新真相源 specs |

### 示例

```text
/opsx:propose 增加 NPC 睡前晚安主动问候

# AI 创建 openspec/changes/bedtime-greeting/
#   proposal.md  — 为什么做、改什么
#   specs/       — ADDED/MODIFIED 需求
#   design.md    — 技术方案
#   tasks.md     — 实现清单

/opsx:apply

/opsx:archive
```

## 本地 CLI

```bash
# 安装（项目已含 devDependency）
npm install

# 初始化/更新 Cursor 集成（新 clone 后）
npx openspec update --tools cursor

# 查看变更状态
npx openspec status

# 校验 spec 格式
npx openspec validate
```

## 编写变更时的约定

1. **改行为先改 spec**：在 `openspec/changes/<name>/specs/` 写 delta（`## ADDED Requirements` 等），不要只改代码不留规格。
2. **对照现有能力**：修改前先读 `openspec/specs/<capability>/spec.md`，proposal 的 Capabilities 里写清 New / Modified。
3. **与架构文档一致**：设计细节参考 `docs/ARCHITECTURE.md`；OpenSpec 管「要什么」，架构文档管「为什么这样拆」。
4. **测试门禁**：tasks 最后一项永远是 `cd backend && python -m pytest`。

## 已有能力规格（baseline）

| Spec | 对应代码 |
|------|----------|
| `chat-orchestration` | `backend/app/orchestrator.py`, `memory_honesty.py`, `reply_polish.py` |
| `persona` | `backend/app/persona.py`, `domain.py` |
| `memory` | `backend/app/memory/` |
| `emotion-relationship` | `backend/app/emotion/` |
| `safety` | `backend/app/safety.py`, `compliance.py` |
| `proactivity` | `backend/app/proactivity.py`, `scheduler.py` |
| `user-insight` | `backend/app/user_insight.py` |
| `voice-avatar` | `backend/app/voice/`, `avatar.py` |

## 与 Cursor 的关系

- 重启 IDE 后可用 `/opsx:*` 斜杠命令。
- Agent 会自动加载 `.cursor/skills/openspec-*` 与 `openspec/config.yaml` 中的项目上下文。
- 云 Agent 开发同样遵循：先 propose，再 apply，最后 archive。

## 参考

- [OpenSpec 文档](https://github.com/Fission-AI/OpenSpec/tree/main/docs)
- [OPSX 工作流](https://github.com/Fission-AI/OpenSpec/blob/main/docs/opsx.md)
