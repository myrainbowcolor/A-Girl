# 用 OpenSpec 开发 A-Girl

本项目已接入 [OpenSpec](https://github.com/Fission-AI/OpenSpec)（规范驱动开发，SDD）。

## Cloud Agent 用户（没有本地仓库）

**Cloud Agent 远程跑代码，你本地的 `/` 菜单不会出现项目的 OpenSpec Skills**——这是正常的。你看到的只有内置 `summarize` 和插件（如 Figma），不代表 Cloud 上没有 OpenSpec。

**直接在 Cloud Agent 对话里用自然语言即可**，Agent 会读取远程仓库里的 `openspec/`、`.cursor/skills/` 和规则文件。

| 你想做什么 | 直接发给 Cloud Agent |
|-----------|---------------------|
| 新功能 / 改需求 | `用 OpenSpec propose：增加睡前晚安主动问候` |
| 先讨论不写代码 | `用 OpenSpec explore：讨论主动对话频率怎么调` |
| 开始写代码 | `用 OpenSpec apply：实现当前 change 的 tasks` |
| 功能做完 | `用 OpenSpec archive：归档当前变更` |

Agent 会在远程 VM 执行 `npx openspec ...`，产物在 `openspec/changes/` 和 PR 里，无需本地 `git pull`。

---

## 本地 Cursor 用户

**Cursor 2.5+ 使用 Skills，不是 Commands。**

若本地 clone 了仓库，`/` 菜单的 **Skills** 区搜索 `openspec` 可手动触发；Cloud Agent 用户可跳过本节。

### 第一步：拉最新代码

```bash
git pull origin main
ls .cursor/skills/
# 应看到：openspec-propose、openspec-apply-change 等文件夹
```

### 第二步：重载 Cursor

命令面板 → **Developer: Reload Window**

### 第三步：在 Skills 里找 OpenSpec

1. 打开 **Agent** 聊天框
2. 输入 `/`
3. 看 **Skills** 区域（不是 Commands）
4. 搜索 **`openspec`**

应出现：

| Skill | 作用 |
|-------|------|
| `/openspec-propose` | 新建变更：proposal + specs + design + tasks |
| `/openspec-explore` | 只讨论方案，不写代码 |
| `/openspec-apply-change` | 按 tasks 实现 |
| `/openspec-sync-specs` | 同步 delta spec |
| `/openspec-archive-change` | 归档已完成变更 |

### 不用斜杠也可以

直接对 Agent 说：

```text
用 OpenSpec propose：增加睡前晚安主动问候
```

项目规则（`.cursor/rules/openspec.mdc`）会让 Agent 自动走 OpenSpec 流程。

## 目录结构

```text
openspec/
  config.yaml          # 项目上下文（AI 会读）
  specs/               # 当前系统「真相源」
  changes/             # 进行中的变更
.cursor/skills/        # Cursor Skills（/openspec-propose 等）
AGENTS.md              # Agent 总览
```

## 日常流程

```text
/openspec-propose 增加 NPC 睡前晚安主动问候
/openspec-apply-change
/openspec-archive-change
```

## 本地 CLI

```bash
npm install
npx openspec validate --specs
npx openspec status
npx openspec update --force   # 刷新 Cursor Skills
```

## 已有 Spec 与代码

| Spec | 代码 |
|------|------|
| chat-orchestration | orchestrator.py |
| persona | persona.py |
| memory | memory/ |
| emotion-relationship | emotion/ |
| safety | safety.py |
| proactivity | proactivity.py |
| user-insight | user_insight.py |
| voice-avatar | voice/, avatar.py |

## 仍看不到 Skills？

1. 确认打开的是 **仓库根目录**（含 `openspec/` 和 `backend/`，不是只开 `backend/`）
2. 确认分支是 **main** 且已 pull
3. 运行 `npm install && npx openspec update --force` 后再次 Reload
4. 或用 `@openspec-propose` 手动附加 Skill 到对话
