## Why

对话质量评测 26 场景全绿，无 open `dialogue-quality` Issue。但 `scene_first` 编排优先调用 `compose_contextual_reply`，在 `long_distance_miss` 场景（「刚跟他视频完，挂掉电话好空」「有时候觉得异地恋好难」）时 compose 未命中任何分支（返回 None），虽由 mock 场景引擎兜底通过评测，生产路径与 mock 行为不一致，真实 LLM 路径下异地恋想念场景易落入 `compose_open_reply` 问卷式兜底，削弱情感拟真度。

修复前 compose 路径可能落入通用 open 兜底，而非 mock 已有的「挂电话空落落 / 异地恋难熬」共情话术。

## What Changes

- 在 `backend/app/dialogue_compose.py` 的 `compose_contextual_reply` 中增加异地恋想念分支（挂电话空落落、异地恋好难），与 `mock.py` 场景分支对齐
- 补充 `test_dialogue_compose.py` 单测覆盖两轮续聊
- 不改 orchestrator 调度、安全策略、API 契约

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: 用户表达异地恋想念或视频挂断后的空落感时，生产路径 `compose_contextual_reply` 与 mock 场景分支 MUST 行为一致，先接住空落/难熬感，禁止落入问卷式 open 兜底

## Impact

- `backend/app/dialogue_compose.py` — 异地恋想念共情分支
- `backend/tests/test_dialogue_compose.py` — 回归测试
- 不影响 API 契约、安全策略、记忆检索、调度逻辑
