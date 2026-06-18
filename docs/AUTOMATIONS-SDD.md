# Automations 走 OpenSpec SDD 流程

Cursor Automations / Cloud Agent **没有**本地 `/openspec-propose` 斜杠菜单，但远程 VM 上有完整仓库（`openspec/`、`.cursor/skills/`、`.cursor/rules/openspec.mdc`）。只要在 **Automation Prompt** 里写清楚 SDD 步骤，Agent 就会按规范驱动开发迭代。

## 核心原则

| 原则 | 说明 |
|------|------|
| **先 spec 后代码** | 新功能 / 较大改动必须先 Propose，禁止直接改业务逻辑 |
| **自然语言触发** | Prompt 写「用 OpenSpec propose/apply/archive」，Agent 会读对应 Skill |
| **分支命名** | 必须用 `cursor/<描述>-381d`，才能被 [auto-merge workflow](AUTOMATIONS.md) 自动合并 |
| **验证再归档** | Apply 后跑 pytest；全部 tasks 勾选后再 Archive |
| **产物进 PR** | `openspec/changes/` 与代码改动同一 PR，便于 review |

## SDD 循环（Automation 必走）

```text
Propose → Apply → Verify → Archive → PR
```

| 阶段 | Agent 动作 | CLI / Skill |
|------|-----------|-------------|
| **Propose** | 读 `openspec/config.yaml`、相关 `openspec/specs/`，创建 change | `npx openspec new change "<kebab-name>"`，按 `.cursor/skills/openspec-propose/SKILL.md` 生成 proposal / specs / design / tasks |
| **Apply** | 按 tasks 逐项实现，勾选 `- [x]` | 读 `.cursor/skills/openspec-apply-change/SKILL.md`，`npx openspec instructions apply --change "<name>" --json` |
| **Verify** | 后端测试 + OpenSpec 校验 | `cd backend && python -m pytest --ignore=tests/test_dialogue_quality.py`；`npx openspec validate --specs` |
| **Archive** | 同步 delta spec 后归档 | `.cursor/skills/openspec-archive-change/SKILL.md`，必要时 `.cursor/skills/openspec-sync-specs/SKILL.md` |
| **PR** | `cursor/*` 分支 push 并开 Draft PR | 依赖 `.github/workflows/auto-merge-cursor.yml` 自动 squash merge |

## 通用 Prompt 前缀（复制到每条 Automation）

把下面整段放在 Automation Prompt **最前面**，再追加具体任务描述：

```text
你是 A-Girl 仓库的 Cloud Agent。必须严格走 OpenSpec 规范驱动开发（SDD），禁止跳过 spec 直接改业务代码。

## 必读
- docs/OPENSPEC.md
- docs/AUTOMATIONS-SDD.md（本流程）
- openspec/config.yaml
- AGENTS.md

## SDD 流程（按顺序执行，不可跳步）

### 1. Propose（若无进行中的 change）
- 读取 .cursor/skills/openspec-propose/SKILL.md 并按步骤执行
- npx openspec new change "<kebab-case-name>"
- 生成 proposal.md、specs/、design.md、tasks.md，直到 apply-ready
- change 名从任务描述推导，kebab-case，例如「优化主动对话频率」→ improve-proactive-frequency

### 2. Apply
- 读取 .cursor/skills/openspec-apply-change/SKILL.md
- npx openspec status --change "<name>" --json
- npx openspec instructions apply --change "<name>" --json
- 逐项完成 tasks.md，每完成一项将 - [ ] 改为 - [x]
- 最小 diff，匹配现有代码风格

### 3. Verify
- cd backend && python -m pytest --ignore=tests/test_dialogue_quality.py
- npx openspec validate --specs
- 测试失败则修复后再继续，不要 Archive

### 4. Archive（仅当 tasks 全部完成且测试通过）
- 读取 .cursor/skills/openspec-archive-change/SKILL.md
- 有 delta spec 时先评估是否 sync 到 openspec/specs/
- 归档到 openspec/changes/archive/YYYY-MM-DD-<name>/

### 5. Git / PR
- 分支名必须为 cursor/<简短描述>-381d（小写）
- git commit -m "描述性中文或英文 commit message"
- git push -u origin <branch>
- 开 Draft PR 到 main（workflow 会自动 ready + squash merge）

## 约束
- 默认受众未成年人，安全优先
- 回复风格相关改动需对齐 openspec/specs/persona/spec.md
- 若已有 openspec/changes/ 下未归档 change 且与本次任务相关，继续该 change 而非新建
- 若任务只是 typo / 纯文档 / 单行配置，可说明理由后跳过 Propose，但仍需 PR

---

## 本次任务
```

---

## 按触发器选用模板

### A. 定时迭代（Scheduled）

**适用**：每周质量改进、主动对话调优、洞察模块增强等。

```text
<粘贴上方「通用 Prompt 前缀」>

## 本次任务
从 openspec/specs/ 与最近合并的 PR 中，挑选 **一个** 可衡量的改进点（例如：主动对话频率、回复自然度、user-insight 深度、TTS 同步）。

1. Propose 一个 change，在 proposal 里写清 Why / 成功指标
2. Apply 并实现
3. Verify 通过后 Archive
4. 开 PR，PR 描述里列出：change 名、改了哪些 spec、pytest 结果

不要一次做多个 unrelated 功能；一个 Automation 运行 = 一个 change。
```

### B. CI 失败（Workflow run failed）

**适用**：main 或 `cursor/*` PR 上 pytest / lint 红。

```text
<粘贴上方「通用 Prompt 前缀」>

## 本次任务
CI 失败，日志摘要：
{{failure_summary}}

1. 若是 **实现 bug**：可先小范围 fix；若 fix 涉及行为变更，必须补/更新 openspec change 中的 spec delta
2. 若是 **测试过时**：更新测试并在 tasks 中记录
3. 不要为修 CI 引入无关 refactor
4. 修复后 Verify，push 到原 cursor/* 分支或新建 cursor/fix-ci-<topic>-381d
```

### C. PR 评论 / `@cursor` 指令

**适用**：人工 review 要求改 spec 或继续 apply。

```text
<粘贴上方「通用 Prompt 前缀」>

## 本次任务
PR #{{pr_number}} 评论：
{{comment_body}}

- 若评论要求「先写 spec」：对该 PR 关联主题执行 Propose 或更新已有 change 的 specs/tasks
- 若评论要求「按 tasks 实现」：对已有 change 执行 Apply
- 在同一 PR 分支上追加 commit，不要另开无关分支
```

**快捷口令**（你在 PR 里评论，Automation 监听 `issue_comment`）：

| 评论 | Agent 行为 |
|------|-----------|
| `@cursor 用 OpenSpec propose：<描述>` | 仅 Propose，可只提交 openspec/changes/ |
| `@cursor 用 OpenSpec apply` | 对当前 PR 或最新 change Apply |
| `@cursor 用 OpenSpec archive` | Verify 通过后 Archive |

### D. Linear / Issue 驱动

**适用**：每个 issue 一个 change。

```text
<粘贴上方「通用 Prompt 前缀」>

## 本次任务
Issue：{{issue_title}}
{{issue_body}}

1. change 名与 issue 对齐，如 issue「深度用户洞察」→ deep-user-insight
2. Propose 时在 proposal Impact 里写 `Closes #{{issue_number}}`
3. 完整走 Apply → Verify → Archive → PR
```

---

## Automation 配置建议

| 配置项 | 建议值 |
|--------|--------|
| **Repository** | 本仓库根目录（含 `openspec/` 与 `backend/`） |
| **Branch 规则** | Agent 创建 `cursor/*`，不要直接 push main |
| **Tools** | 启用终端、Git；可选 GitHub MCP 用于看 PR/check |
| **Memory** | 可写「默认走 OpenSpec SDD，见 docs/AUTOMATIONS-SDD.md」 |

### 多条 Automation 分工

```text
Automation 1「SDD 定时迭代」  → 模板 A，cron 每周
Automation 2「SDD 修 CI」      → 模板 B，workflow_run failed
Automation 3「SDD PR 评论」    → 模板 C，pull_request_review_comment 或 issue_comment
Automation 4「SDD Issue」      → 模板 D，issues labeled openspec
```

给 Issue 打 label `openspec` 可让 Issue 自动化只处理规范驱动任务。

---

## 与 auto-merge 的配合

SDD PR 与普通 Agent PR 相同：

1. 分支 **`cursor/*`**
2. CI 全绿（含 pytest）
3. `.github/workflows/auto-merge-cursor.yml` 会 ready + squash merge

详见 [AUTOMATIONS.md](AUTOMATIONS.md)。

---

## 常见问题

**Q：Automation 里能用 `/openspec-propose` 吗？**  
不能。Cloud Agent 没有本地 Skills 菜单。用 Prompt 里的「用 OpenSpec propose」或 `@cursor 用 OpenSpec propose：…`。

**Q：可以跳过 Propose 吗？**  
仅当改动极小（typo、注释、纯文档）且不影响行为契约。任何改 orchestrator / persona / proactivity 等逻辑都必须 Propose。

**Q：一个 PR 可以有多个 change 吗？**  
不建议。一个 Automation 运行对应一个 change，便于 review 和 Archive。

**Q：Archive 前 spec 没 sync 会怎样？**  
主规格 `openspec/specs/` 会与代码漂移。Archive 前用 sync-specs skill 或手动合并 delta。

**Q：如何确认 Agent 真的走了 SDD？**  
看 PR 是否包含 `openspec/changes/`（Propose）或 `openspec/changes/archive/`（完成后），以及 `tasks.md` 勾选记录。

---

## 相关文档

- [OPENSPEC.md](OPENSPEC.md) — OpenSpec 日常用法
- [AUTOMATIONS.md](AUTOMATIONS.md) — 自动 merge 与排查
- [AGENTS.md](../AGENTS.md) — Agent 总览
