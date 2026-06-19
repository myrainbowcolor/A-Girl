## Why

对话质量评测 26 场景全绿，但 `build_system_prompt` 的「本轮侧重」仅区分正/负/怀旧三类。用户愤怒发泄（如 `angry_at_boss` 场景「老板今天当众骂我，气死了！」）与低落倾诉共用同一负向指引「先接住感受」，真实 LLM 路径下易生成偏安抚、说教式回复，与 mock 已实现的「先陪发火、不急着劝冷静」不一致，削弱愤怒场景的情感拟真度。

## What Changes

- 在 `backend/app/persona.py` 为愤怒/发泄类用户句新增独立「本轮侧重」语气提示（关键词如气死、骂我、生气、辞职冲动等），优先于通用负向提示
- 中性或纯低落句保持现有负向/怀旧/正向逻辑不变
- 补充 `test_persona.py` 与 `angry_at_boss` 场景相关断言
- 不改 mock 模板、安全策略、API 契约

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: system prompt 须区分用户愤怒发泄与低落倾诉，注入对应的「本轮侧重」语气指引

## Impact

- `backend/app/persona.py` — `_user_turn_tone_hint()` 与 `_USER_TURN_TONE`
- `backend/tests/test_persona.py` — 愤怒句 prompt 含发泄侧重
- 不影响 orchestrator、safety、avatar、mock 主路径
