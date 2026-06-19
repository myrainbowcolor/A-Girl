## Context

`persona.py` 的 `_user_turn_tone_hint()` 已支持封闭、身份质疑、怀旧、愤怒等独立侧重。失眠场景（`insomnia_rumination`）描述要求「少给解决方案，多陪伴」，但当前失眠句仍走通用负向提示，真实 LLM 易输出助眠建议。

## Goals / Non-Goals

**Goals:**

- 为失眠/反刍关键词增加独立 `_USER_TURN_TONE["insomnia"]` 条目
- 在 `_user_turn_tone_hint()` 中于通用负向分析之前匹配失眠关键词（愤怒之后、analyze_lexicon 之前）
- 补充 `test_persona.py` 断言；跑通全量 pytest 与 dialogue quality

**Non-Goals:**

- 不改 `mock.py` 模板（已有失眠分支）
- 不改调度、安全、avatar、API
- 不新增场景或改评测规则

## Decisions

1. **关键词列表**：`失眠`、`睡不着`、`脑子停`、`越躺越清醒`、`躺不住` — 与 mock `_scene_reply` 及 `scenarios.py` 用语对齐。
2. **优先级**：愤怒 > 失眠 > 通用负向 — 避免「气死了睡不着」被失眠覆盖（含「气死」仍走愤怒）。
3. **提示文案**：强调陪伴、禁止助眠建议，与 anger hint 风格一致的一两句指引。

## Risks / Trade-offs

- [误判] 「今天没失眠」等否定句可能误触发 → 关键词偏具体（「睡不着」而非单字「睡」），风险可接受。
- [与 mock 重复] mock 已有分支，本改动主要服务真实 LLM → 可接受，评测仍全绿。
