## Why

对话质量评测 26 场景全绿，但 `build_system_prompt` 的「本轮侧重」对自我怀疑/比较类倾诉（如 `jealous_comparison`「是不是我太差劲了」、`impulse_regret`「觉得自己好没用」）与通用低落倾诉共用同一负向指引。真实 LLM 路径下易生成「没事的」「别比了」等说教或空泛安慰，与 mock 已实现的「先承认落差感、不急着反驳或灌鸡汤」不一致，削弱比较心态场景的情感拟真度。

## What Changes

- 在 `backend/app/persona.py` 为自我怀疑/比较类用户句新增独立「本轮侧重」语气提示（关键词如差劲、没用、自卑、原地踏步、管不住等），优先于通用负向提示
- 纯低落倾诉、愤怒发泄、失眠等既有侧重逻辑不变
- 补充 `test_persona.py` 与 `jealous_comparison` / `impulse_regret` 场景相关断言
- 不改 mock 模板、安全策略、API 契约

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: system prompt 须区分用户自我怀疑/比较心态与通用低落倾诉，注入对应的「本轮侧重」语气指引

## Impact

- `backend/app/persona.py` — `_SELF_DOUBT_KEYWORDS`、`_USER_TURN_TONE["self_doubt"]`、`_user_turn_tone_hint()` 检测顺序
- `backend/tests/test_persona.py` — 自我怀疑句 prompt 含专用侧重
- 不影响 orchestrator、safety、avatar、mock 主路径
