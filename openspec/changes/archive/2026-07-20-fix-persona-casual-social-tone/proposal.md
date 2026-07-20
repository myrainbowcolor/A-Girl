## Why

无 open `dialogue-quality` Issue，对话质量 26 场景全绿。但 `build_system_prompt` 的「本轮侧重」对早安寒暄、友好问候、无聊摸鱼、轻松正向闲聊等社交句误判为通用「分享好事」侧重（因 `analyze_lexicon` 返回 sentiment≈0.38>0.3）。真实 LLM 路径会收到「真心替 ta 高兴」指引，与 `morning_checkin`、`bored_smalltalk`、`stranger_first_greet` 等场景的自然寒暄/轻松闲聊不符，削弱拟真度。

## What Changes

- `persona.py`：在 `_user_turn_tone_hint` 中为早安寒暄、友好问候、无聊/社交探问、轻松正向闲聊增加独立「本轮侧重」，优先于通用正向分支
- `test_persona.py`：补充对应 prompt 断言（含早安不误走报喜侧重）
- 不改 compose/mock 话术、调度、安全策略

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：用户轮次语气侧重须区分社交寒暄/轻松闲聊与真·分享好事

## Impact

- `backend/app/persona.py`
- `backend/tests/test_persona.py`
- 影响 LLM system prompt 构建；mock/compose 规则路径行为不变
