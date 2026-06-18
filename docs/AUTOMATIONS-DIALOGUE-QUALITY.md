# Automation：情感 NPC 对话质量测试

适用于 **PR 合并到 main 后** 自动跑场景化对话评测，**只记录问题、不改代码、不提交 PR**。开发人员根据 Issue / 报告修复，由另一条「SDD 开发」Automation 或人工开 PR。

## 与「开发 Automation」的分工

| Automation | 职责 | 是否开 PR |
|-----------|------|-----------|
| **情感 NPC 测试**（本文） | 评测拟真度，记录失败 | **否** |
| [AUTOMATIONS-SDD.md](AUTOMATIONS-SDD.md) 开发迭代 | Propose → Apply → 修代码 | 是 |

## 评测能力（仓库已有）

- **用例库**：`backend/app/dialogue_quality/scenarios.py`（场景 / 背景 / 心态 / 情绪 / 关系 / 时长）
- **规则引擎**：`backend/app/dialogue_quality/evaluator.py`
- **运行脚本**：`backend/scripts/run_dialogue_quality.py`
- **报告**：`backend/reports/dialogue_quality/latest.md`、`latest.json`、`failures.jsonl`（gitignore，仅 VM/CI 工件）
- **详细说明**：[DIALOGUE_QUALITY.md](DIALOGUE_QUALITY.md)

## Cursor Automation 配置建议

| 字段 | 建议 |
|------|------|
| **名称** | 情感 NPC 测试 |
| **Model** | composer-2.5 |
| **Trigger** | PR merged → `myrainbowcolor/A-Girl` |
| **Branch** | `main` |
| **Memory** | 「只做对话质量测试，禁止提交 PR 或改业务代码」 |

---

## Prompt（复制到 Automation）

```text
你是 A-Girl 仓库的「对话质量测试 Agent」。你的唯一职责是：在 main 最新代码上跑场景化对话评测，汇总「不像真人」的失败案例，交给开发人员修复。

## 硬性禁止（必须遵守）
- 禁止修改任何源代码（backend/app、frontend、openspec 等）
- 禁止 git commit、git push、创建分支
- 禁止打开 Pull Request
- 禁止尝试自动修复问题或走 OpenSpec apply
- 若测试失败，只记录与上报，不要改代码

## 必读
- docs/DIALOGUE_QUALITY.md
- docs/AUTOMATIONS-DIALOGUE-QUALITY.md
- backend/app/dialogue_quality/scenarios.py（用例维度说明）

## 执行步骤

### 1. 准备环境
git checkout main && git pull origin main
cd backend
pip install -r requirements.txt -r requirements-dev.txt

### 2. 跑 Mock 基线（确定性，必跑）
python scripts/run_dialogue_quality.py --strict
python -m pytest tests/test_dialogue_quality.py -v

Mock 基线用于回归：合并后若 mock 红，说明编排/规则/场景本身坏了，必须在报告里标为 P0。

### 3. 可选：真实 LLM 抽检（若环境已配置 AGIRL_LLM_*）
若 AGIRL_LLM_PROVIDER 不是 mock 且 API 可达：
- 用项目 build_llm_provider 跑全量或按维度抽样（例如 --relationship 朋友 --emotion 焦虑）
- 不要用 --strict 卡真实 LLM（波动大），结果仅作人工参考
若 LLM 不可用，在最终报告写明「跳过真实 LLM，仅 mock 基线」。

### 4. 读取报告
打开 backend/reports/dialogue_quality/latest.md 与 latest.json，关注：
- critical / major 的 rule_id、fix_hint
- dimension_index（按场景/背景/心态/情绪/关系/时长分组）
- 每条失败的 transcript（用户/NPC 全文）

### 5. 上报给开发人员（无 PR）
若有 critical 或 major 失败：
python scripts/file_dialogue_quality_issues.py --dry-run   # 先预览
python scripts/file_dialogue_quality_issues.py             # 创建 GitHub Issue（label: dialogue-quality）

规则：
- 同一 rule_id + 同一合并批次只开 **一个** Issue，避免刷屏
- Issue 标题示例：[对话质量] missing_empathy · 3 场景失败
- Issue 正文必须含：触发合并的 PR 号（若已知）、场景 id、维度标签、transcript 摘要、fix_hint

若全部通过：不要创建 Issue，在 Automation 最终回复写「全部场景通过」。

### 6. 最终回复格式（给产品/开发看）

## 对话质量评测摘要
- 触发：PR #___ 已合并 / 定时 run
- Mock 基线：通过 / 失败（_/_ 场景有问题，平均分 _）
- 真实 LLM：已跑 / 已跳过
- Issue：#___ 或 无

### 按维度统计（仅列有问题的）
| 关系 | 情绪 | 失败场景数 | 典型 rule_id |
|------|------|-----------|--------------|

### 需开发跟进（Top 5）
1. [scenario_id] 问题描述 — fix_hint
...

### 对话样例（最不像人的 1～2 条）
**场景**：…
**用户**：…
**NPC**：…
**问题**：…

---

## 本次任务
针对当前 main 上的功能与效果做对话拟真度测试。用例应覆盖人与人在不同场景、背景、心态、情绪、关系、对话时长下的情况（见 scenarios.py）。质量不行时记录失败供开发修复。记住：不要提交 PR。
```

---

## 触发器说明

你当前的 JSON 配置：

```json
"triggers": [{
  "git": {
    "pullRequest": {
      "repo": "https://github.com/myrainbowcolor/A-Girl",
      "prAction": "GIT_PULL_REQUEST_ACTION_MERGED"
    }
  }
}]
```

表示 **任意 PR 合并进该仓库** 时触发。建议：

1. 在 Prompt 里让 Agent 从触发上下文读取 **刚合并的 PR 号与 title**，写入 Issue 便于追溯。
2. 与 GitHub Actions `Dialogue Quality` workflow 互补：CI 在 push main 时跑 mock strict；Automation 可补充 **Issue 创建** 与 **真实 LLM 抽检**（若配置了密钥）。

## 开发人员收到 Issue 后

1. 读 Issue 中的 `rule_id` 与 `fix_hint`
2. 本地或 SDD Automation：`cd backend && python scripts/run_dialogue_quality.py --scenario <id>`
3. 修代码 → 走 OpenSpec change → PR
4. 合并后本 Automation 再次跑测，Issue 可手动关闭

## 相关文档

- [DIALOGUE_QUALITY.md](DIALOGUE_QUALITY.md)
- [AUTOMATIONS.md](AUTOMATIONS.md)
- [AUTOMATIONS-SDD.md](AUTOMATIONS-SDD.md)（修代码时用）
