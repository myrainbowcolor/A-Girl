## Context

上一轮变更 `fix-short-reply-avatar-comfort` 已在 `analyzer.py` 为「还好」「不知道」等整句极简口语增加偏负向判定，驱动 avatar comfort 表情。但 `persona.py` 的 `_user_turn_tone_hint()` 仍用 `len(t) <= 2` 将「还好」「累」判为 `closed`，与 avatar 及 mock 共情话术不一致；`reply_guard.user_is_closed()` 同样误伤，可能削弱轻柔共情。

## Goals / Non-Goals

**Goals:**

- persona prompt「本轮侧重」与 analyzer avatar 判定对齐
- reply_guard 仅对真正封闭句启用追问拦截
- 补充单测，26 场景 dialogue quality 保持全绿

**Non-Goals:**

- 不改 mock 模板、analyzer 词典、安全策略
- 不调整 `len(t) <= 2` 对「嗯」「哦」的封闭判定

## Decisions

1. **新增 `masked_low` 语气侧重**（persona `_USER_TURN_TONE`）
   - 覆盖 `analyzer._MINIMAL_MASKING`、`_MINIMAL_EVASIVE` 及单字「累」
   - 在 `_user_turn_tone_hint()` 中于 `closed` 判定之前检查
   - 理由：与已有回复要求第 7 条「极简句耐心陪着、轻问引导」一致

2. **reply_guard 排除 masking 句**
   - 在 `user_is_closed()` 开头排除整句 masking/evasive 与单字「累」
   - 理由：mock/LLM 对「还好」的轻柔共情含轻问句，不应被 `guard_closed_user_reply` 替换

3. **不抽取共享常量模块**
   - persona 与 reply_guard 各自维护 frozenset，与 analyzer 保持同名集合
   - 理由：最小 diff，避免新模块；三处集合小且稳定

## Risks / Trade-offs

- [误判「还好」为低落] → 仅整句精确匹配，不影响「今天还好啦」等长句
- [「累」单字在非疲惫语境] → 短句场景下共情优于封闭，风险可接受

## Migration Plan

纯逻辑增量，无数据迁移。部署后真实 LLM 路径 prompt 自动生效。

## Open Questions

（无）
