## Context

persona spec 与 `persona.py` system prompt 均明确禁止 NPC 以「嗯」开头，但 `dialogue_compose.py`、`reply_guard.py`、`safety.py` 等模板仍大量保留句首「嗯」。`reply_guard._FILLER_HEAD_RE` 仅在 `reply_is_filler_heavy` 触发回退时剥离，未覆盖 compose 直出路径。`latest.json` 显示 4 条高可见 transcript 仍违规。

架构上所有用户消息回复经 `orchestrator` → `polish_reply` 后处理（见 `docs/ARCHITECTURE.md` scene_first 编排），因此在 `polish_reply` 末段统一处理可覆盖 compose、mock、LLM 三条路径，无需改编排接口。

## Goals / Non-Goals

**Goals:**

- 生产路径 NPC 回复（去动作括号与亲昵前缀后）不以「嗯」「嗯嗯」「嗯…」开头
- 修正已知高可见 compose/safety 模板
- 对话质量评测可自动检出句首「嗯」回归

**Non-Goals:**

- 不批量改写 `mock.py` 全部历史模板（由 polish 兜底 + 高可见 compose 修正）
- 不改用户说「嗯」时的 avatar 平静规则
- 不改安全拦截逻辑，仅优化话术口吻

## Decisions

1. **在 `polish_reply` 末段调用 `strip_npc_leading_um(reply)`**
   - 复用 `_FILLER_HEAD_RE` 剥离 `(嗯+…)` 前缀；若剥离后为空则保留原句
   - 理由：单点兜底，覆盖 LLM 偶发输出；与现有 `test_polish_filler_complaint` 方向一致

2. **源头修正 3 处 compose 模板 + safety 边界句**
   - 孤独失眠、masking「还好」、异地恋第二选项、安全边界
   - 理由：减少 polish 剥离后语义断裂风险

3. **evaluator 新增 `reply_starts_with_um` major 检查**
   - 去括号后与 `_normalize_reply` 一致判定
   - 理由：防止回归；与 persona 禁止规则对齐

## Risks / Trade-offs

- [剥离后句子过短] → 仅当剥离后 ≥4 字才采用；否则保留并依赖 compose 修正
- [用户投诉「别嗯嗯」的道歉句] → `user_complains_filler` 路径的「抱歉/对不起」句豁免检查
- [mock 内部模板仍含嗯] → polish 兜底；不在本轮大规模改 mock
