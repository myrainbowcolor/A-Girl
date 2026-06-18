# Cursor Automations 与自动 Merge

## 现象

Automations / Cloud Agent 改完代码开了 PR，但没有自动合并进 `main`。

## 常见原因

| 原因 | 说明 |
|------|------|
| **PR 作者不是 `cursor[bot]`** | Automations 可能以 `app/cursor` 或你的 GitHub 账号开 PR，旧 workflow 会 skip |
| **Draft PR** | Cloud Agent 默认开 Draft，需先 mark ready 才能 merge |
| **只 enable 了 auto-merge** | `gh pr merge --auto` 需要仓库开启 Auto-merge + 检查全绿，不会立刻合并 |
| **分支有冲突 (DIRTY)** | 与 main 冲突时无法 merge，需 Agent 先 rebase |

## 仓库内已配置的修复

`.github/workflows/auto-merge-cursor.yml` 会：

1. 匹配所有 **`cursor/*` 分支**的 PR（不限作者）
2. Draft → 自动 `gh pr ready`
3. 等待 CI 检查（best effort）
4. **直接 `gh pr merge --squash --delete-branch`** 合并

Dialogue Quality 跑完后也会再次尝试 merge（`workflow_run` 触发）。

## 你需要在 GitHub 检查的

1. **Settings → Actions → General**：Workflow 有 read/write 权限  
2. **Settings → General → Pull Requests**：建议勾选 **Allow auto-merge**（作 fallback）  
3. **Branch protection**：若 `main` 要求人工 Review，Actions 的 `GITHUB_TOKEN` 可能无法 bypass，需在规则里允许 GitHub Actions 合并，或去掉 mandatory review

## Automations 走 OpenSpec SDD

若希望 **Automations 自动迭代先写 spec 再写代码**，见 **[AUTOMATIONS-SDD.md](AUTOMATIONS-SDD.md)**：

- 可复制 **通用 Prompt 前缀** + 定时 / CI / PR 评论 / Issue 四类模板
- 循环：**Propose → Apply → Verify → Archive → PR**
- Cloud Agent 用自然语言「用 OpenSpec propose/apply/archive」，无需斜杠命令

## Automations 侧建议

Cursor Automations **没有内置 merge 工具**，可选：

1. **依赖本仓库 GitHub Action**（推荐）：保持 `cursor/*` 分支命名，开 PR 即可  
2. **Automation 加 GitHub MCP**：prompt 里写「开 PR 后调用 merge_pull_request」  
3. **不开 PR**：prompt 要求直接 push 到 `main`（需关闭 branch protection）

## 排查命令

```bash
gh pr list --state open
gh run list --workflow=auto-merge-cursor.yml --limit 5
gh pr view <number> --json mergeable,mergeStateStatus,statusCheckRollup,author
```

若 workflow 显示 **skipped**，看 `head.ref` 是否以 `cursor/` 开头。
