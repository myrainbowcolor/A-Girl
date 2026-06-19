## Why

对话质量评测 26 场景全绿，但 `build_system_prompt` 的「本轮侧重」对失眠/反刍类用户句（如 `insomnia_rumination` 场景「又失眠了，脑子停不下来」）与通用低落倾诉共用同一负向指引「先接住感受」。真实 LLM 路径下易生成数羊、早睡等建议式回复，与场景期望「少给解决方案、多陪伴」不一致，削弱深夜失眠场景的情感拟真度。

## What Changes

- 在 `backend/app/persona.py` 为失眠/反刍类用户句新增独立「本轮侧重」语气提示（关键词如失眠、睡不着、脑子停不下来、越躺越清醒等），优先于通用负向提示
- 纯低落或焦虑句（非失眠语境）保持现有负向/愤怒/怀旧逻辑不变
- 补充 `test_persona.py` 与 `insomnia_rumination` 场景相关断言
- 不改 mock 模板、安全策略、API 契约

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: system prompt 须区分用户失眠反刍与通用低落倾诉，注入对应的「本轮侧重」语气指引

## Impact

- `backend/app/persona.py` — `_user_turn_tone_hint()` 与 `_USER_TURN_TONE`
- `backend/tests/test_persona.py` — 失眠句 prompt 含反刍侧重
- 不影响 orchestrator、safety、avatar、mock 主路径
