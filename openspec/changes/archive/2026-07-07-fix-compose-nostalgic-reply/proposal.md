## Why

对话质量评测 26 场景全绿，无 open `dialogue-quality` Issue。但 `scene_first` 编排优先调用 `compose_contextual_reply`，在 `nostalgic_childhood` 场景（「突然想到小时候外婆做的汤圆，好怀念」「那时候日子简单，现在好难静下来」）时 compose 未命中任何分支（返回 None），虽由 mock 场景引擎兜底通过评测，生产路径与 mock 行为不一致；真实 LLM 路径下怀旧倾诉易落入 `compose_open_reply` 问卷式兜底（如「是突然这样，还是已经有一阵子了？」），削弱情感拟真度。

## What Changes

- 在 `backend/app/dialogue_compose.py` 的 `compose_contextual_reply` 中增加怀旧/童年分支（须在通用负面 open 兜底之前），与 `mock.py` 场景分支对齐
- 覆盖怀念旧时光、续聊「现在好难静下来」等话术，语气柔软顺着回忆共鸣，禁止转移话题或问卷套话
- 补充 `test_dialogue_compose.py` 单测覆盖 `nostalgic_childhood` 两轮话术
- 不改 orchestrator 调度、安全策略、API 契约

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: 用户表达怀旧/童年回忆（含「怀念」「小时候」「外婆」「童年」「汤圆」等）时，生产路径 `compose_contextual_reply` 与 mock 场景分支 MUST 行为一致，顺着回忆共鸣，禁止落入问卷式 open 兜底

## Impact

- `backend/app/dialogue_compose.py` — 怀旧童年共情分支
- `backend/tests/test_dialogue_compose.py` — 回归测试
- 不影响 API 契约、安全策略、记忆检索、调度逻辑
