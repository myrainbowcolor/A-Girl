## Why

对话质量场景 `morning_checkin` 首轮用户说「早呀，今天又要上班了」，当前 `scene_first` 路径下 `dialogue_compose.compose_contextual_reply` 因短句含「上班」误命中工作压力分支，回复「工作的事确实容易压着人。是忙不过来，还是心里觉得不公平？」——像问卷式工作压力疏导，而非自然早安寒暄，拟真度差。

## What Changes

- 在 `dialogue_compose.py` 增加早安/通勤寒暄分支，优先于短句「上班/工作」工作压力路由
- 收紧工作压力短句触发条件：含「早呀/早安/早上好」等问候时不走 vent 分支
- 补充 `test_dialogue_compose.py` 与 `morning_checkin` 场景断言（回复含早安语气、不含工作压力套话）
- 不改 orchestrator 主路径、安全策略、API 契约

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `chat-orchestration`: 开放话题拼装层须正确区分早安寒暄与工作压力倾诉

## Impact

- `backend/app/dialogue_compose.py` — 早安分支与工作压力触发条件
- `backend/tests/test_dialogue_compose.py` — 回归测试
- `backend/app/dialogue_quality/scenarios.py` — morning_checkin 首轮期望（可选加强）
- 不影响 safety、memory、avatar、proactivity
