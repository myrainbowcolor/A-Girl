## Why

对话质量评测 26 场景全绿，无 open `dialogue-quality` Issue。但 `scene_first` 编排优先调用 `compose_contextual_reply`，在 `impulse_regret` 场景（「我又乱花钱了，买了根本用不上的东西」「觉得自己好没用，管不住手」）时 compose 未命中任何分支（返回 None），虽由 mock 场景引擎兜底通过评测，生产路径与 mock 行为不一致；真实 LLM 路径下冲动消费后悔场景易落入 `compose_open_reply` 问卷式兜底，削弱情感拟真度。

修复前 compose 路径可能回复「是突然这样，还是已经有一阵子了？」类问卷句，而非 mock 已有的「后悔的时候最容易骂自己，我心疼你」共情接话。

## What Changes

- 在 `backend/app/dialogue_compose.py` 的 `compose_contextual_reply` 中增加冲动消费/自责分支（须在通用负面 open 兜底之前），与 `mock.py` 场景分支对齐
- 区分「乱花钱/后悔」首轮倾诉与「没用/管不住手」自责追问
- 补充 `test_dialogue_compose.py` 单测覆盖 `impulse_regret` 两轮
- 不改 orchestrator 调度、安全策略、API 契约

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: 用户表达冲动消费后悔或自责（含「乱花钱」「管不住」「后悔」等）时，生产路径 `compose_contextual_reply` 与 mock 场景分支 MUST 行为一致，先理解后悔、不急着说教或贴标签，禁止落入问卷式 open 兜底

## Impact

- `backend/app/dialogue_compose.py` — 冲动消费后悔共情分支
- `backend/tests/test_dialogue_compose.py` — 回归测试
- 不影响 API 契约、安全策略、记忆检索、调度逻辑
