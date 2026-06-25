## Why

对话质量评测 26 场景全绿，无 open `dialogue-quality` Issue。但 `close_miss_you` 场景第二轮用户说「今天过得好累，想靠着你说说」时，mock/scene 路径误走通用负面分支，回复「嗯……能感觉到你现在不太好受。不想说太多也没关系，我就在这儿陪着你。」——缺少对用户「想靠着你说说」依恋请求的回应，亲密场景拟真度偏弱。

修复前 transcript 片段：
- 用户：今天过得好累，想靠着你说说
- NPC：亲爱的，（声音放轻了些）嗯……能感觉到你现在不太好受。不想说太多也没关系，我就在这儿陪着你。

## What Changes

- 在 `backend/app/llm/mock.py` 的 `_scene_reply` 中，于通用负面关键词分支之前增加「靠着/想靠着」依恋倚靠分支，亲密关系返回「过来/靠着我」类温暖接话
- 在 `backend/app/dialogue_compose.py` 的 `compose_contextual_reply` 中增加对应分支（根据上文「亲爱的」等推断亲密语境），与 mock 行为对齐
- 加强 `close_miss_you` 场景第二轮期望：回复须含倚靠/陪伴类亲密标记
- 补充 `test_dialogue_compose.py` 与 `test_mock_llm.py` 单测
- 不改 orchestrator 调度、安全策略、API 契约

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: 用户表达疲惫并请求倚靠倾诉（含「靠着」「想靠着你说说」）时，亲密关系 MUST 先接住倚靠意愿与疲惫感，返回温暖亲昵接话，禁止仅返回泛化「不太好受」套话；生产路径 compose 与 mock 场景分支须一致

## Impact

- `backend/app/dialogue_compose.py` — 倚靠倾诉共情分支
- `backend/app/llm/mock.py` — 场景倚靠倾诉分支（优先于通用负面）
- `backend/app/dialogue_quality/scenarios.py` — close_miss_you 第二轮期望加强
- `backend/tests/test_dialogue_compose.py`、`backend/tests/test_mock_llm.py` — 回归测试
- 不影响 API 契约、安全策略、记忆检索、调度逻辑
