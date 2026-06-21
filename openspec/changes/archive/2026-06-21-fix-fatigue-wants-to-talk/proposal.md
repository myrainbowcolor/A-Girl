## Why

对话质量评测 26 场景全绿，但 `close_miss_you` 场景第 2 轮 transcript 暴露拟真缺口：用户说「今天过得好累，想靠着你说说」，mock 通用疲惫分支却回复「不想说太多也没关系」，与用户明确想倾诉的意图相反，亲密陪伴感断裂。需在疲惫共情与「尊重封闭边界」之间区分「想聊」与「不想说」。

## What Changes

- 在 `backend/app/llm/mock.py` 的 `_scene_reply` 中，于通用疲惫兜底之前新增「疲惫 + 想倾诉/靠着聊」分支，亲密/朋友关系下先接住疲惫、邀请慢慢说
- 在 `backend/app/persona.py` 的 `_USER_TURN_TONE` 补充「疲惫但想聊」侧重，供真实 LLM 路径对齐
- 补充 `test_mock.py` 或 `test_persona.py` 单测；`close_miss_you` 场景 transcript 语义对齐
- 不改安全策略、API 契约、调度逻辑

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: 用户疲惫且表达想倾诉（靠着说/跟你说）时，prompt 须指引接住疲惫并邀请慢慢说，禁止套用「不想说也没关系」封闭边界话术

## Impact

- `backend/app/llm/mock.py` — 场景化疲惫倾诉分支
- `backend/app/persona.py` — `_user_turn_tone_hint()` 与 `_USER_TURN_TONE`
- `backend/tests/test_mock.py` 或 `test_persona.py` — 单测
- 不影响 orchestrator、safety、avatar、proactivity
