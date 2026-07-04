## Why

对话质量评测 26 场景全绿，无 open `dialogue-quality` Issue。但 `scene_first` 编排优先调用 `compose_contextual_reply`，在 `stranger_work_vent` 场景（「今天又加班到十点，好累好烦」）时 compose 未命中任何分支（返回 None），虽由 mock 场景引擎兜底通过评测，生产路径与 mock 行为不一致；真实 LLM 路径下加班疲惫倾诉易落入 `compose_open_reply` 问卷式兜底（如「是突然这样，还是已经有一阵子了？」），削弱情感拟真度。

## What Changes

- 在 `backend/app/dialogue_compose.py` 的 `compose_contextual_reply` 中增加加班/下班疲惫倾诉分支（须在通用负面 open 兜底之前），与 `mock.py` 场景分支对齐
- 陌生关系语气克制、有关怀，不过度亲昵
- 补充 `test_dialogue_compose.py` 单测覆盖 `stranger_work_vent`
- 不改 orchestrator 调度、安全策略、API 契约

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: 用户表达加班/下班疲惫（含「加班」「十点」「好累好烦」等）时，生产路径 `compose_contextual_reply` 与 mock 场景分支 MUST 行为一致，先接住疲惫与烦躁，禁止落入问卷式 open 兜底

## Impact

- `backend/app/dialogue_compose.py` — 加班疲惫共情分支
- `backend/tests/test_dialogue_compose.py` — 回归测试
- 不影响 API 契约、安全策略、记忆检索、调度逻辑
