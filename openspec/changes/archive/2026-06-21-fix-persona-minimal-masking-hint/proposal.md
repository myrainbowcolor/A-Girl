## Why

`short_reply_user` 场景（用户情绪低落、极简回复）中，avatar 已通过 `analyzer.py` 将「还好」「不知道」等判为偏负向并展示 comfort 表情，但 `persona.py` 的 `_user_turn_tone_hint()` 因 `len(t) <= 2` 仍将「还好」「累」等误判为「封闭边界」侧重，真实 LLM 路径下 prompt 指引与多模态共情不一致；`reply_guard.py` 的 `user_is_closed()` 同样误伤这些句，可能把轻柔共情回复当成「追问」替换掉。

## What Changes

- 在 `persona.py` 为整句极简 masking/回避口语（「还好」「还行」「一般」「不知道」「说不清」「说不上」）及单字疲惫「累」新增独立「本轮侧重」，优先于 `closed` 判定
- 在 `reply_guard.py` 将上述句从 `user_is_closed()` 排除，保留真正封闭句（「嗯」「..」「不想说」等）的边界保护
- 补充 `test_persona.py` 与 `test_reply_guard.py` 单测
- 不改 mock 模板、安全策略、API 契约

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: system prompt 须区分「极简 masking 低落」与「真正封闭边界」，注入对应的「本轮侧重」语气指引

## Impact

- `backend/app/persona.py` — `_user_turn_tone_hint()` 与 `_USER_TURN_TONE`
- `backend/app/reply_guard.py` — `user_is_closed()`
- `backend/tests/test_persona.py`、`backend/tests/test_reply_guard.py` — 单测
- 不影响 orchestrator、safety、avatar、mock 主路径
