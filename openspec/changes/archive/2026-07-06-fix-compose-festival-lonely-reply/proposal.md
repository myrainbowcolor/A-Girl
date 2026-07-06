## Why

对话质量评测 26 场景全绿，无 open `dialogue-quality` Issue。但 `scene_first` 编排优先调用 `compose_contextual_reply`，在 `festival_lonely` 场景（「过年一个人，有点落寞」「看到别人团圆就更难受」）时 compose 未命中任何分支（返回 None），虽由 mock 场景引擎兜底通过评测，生产路径与 mock 行为不一致；真实 LLM 路径下节日孤独倾诉易落入 `compose_open_reply` 问卷式兜底（如「是突然这样，还是已经有一阵子了？」），削弱情感拟真度。

## What Changes

- 在 `backend/app/dialogue_compose.py` 的 `compose_contextual_reply` 中增加节日孤独/想家分支（须在通用负面 open 兜底之前），与 `mock.py` 场景分支对齐
- 覆盖一人过节、看到别人团圆更难受等续聊，先看见孤独感、陪伴倾听，禁止假热闹或问卷套话
- 补充 `test_dialogue_compose.py` 单测覆盖 `festival_lonely` 两轮话术
- 不改 orchestrator 调度、安全策略、API 契约

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: 用户表达节日孤独或想家（含「过年」「一个人」「落寞」「团圆」「更难受」等）时，生产路径 `compose_contextual_reply` 与 mock 场景分支 MUST 行为一致，先看见孤独感、陪伴倾听，禁止落入问卷式 open 兜底

## Impact

- `backend/app/dialogue_compose.py` — 节日孤独共情分支
- `backend/tests/test_dialogue_compose.py` — 回归测试
- 不影响 API 契约、安全策略、记忆检索、调度逻辑
