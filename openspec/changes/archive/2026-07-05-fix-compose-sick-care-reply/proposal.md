## Why

对话质量评测 26 场景全绿，无 open `dialogue-quality` Issue。但 `scene_first` 编排优先调用 `compose_contextual_reply`，在 `acquainted_sick_care` 场景（「我感冒了，头好痛」）时 compose 未命中任何分支（返回 None），虽由 mock 场景引擎兜底通过评测，生产路径与 mock 行为不一致；真实 LLM 路径下用户生病求关心易落入 `compose_open_reply` 问卷式兜底（如「是突然这样，还是已经有一阵子了？」），削弱情感拟真度。

## What Changes

- 在 `backend/app/dialogue_compose.py` 的 `compose_contextual_reply` 中增加生病/身体不适关心分支（须在通用负面 open 兜底之前），与 `mock.py` 场景分支对齐
- 覆盖感冒、头痛、发烧等常见表述，表达关心与陪伴，语气随关系亲密度适度调整（compose 无 stage 参数，用 prior_assistant 亲密标记近似）
- 补充 `test_dialogue_compose.py` 单测覆盖 `acquainted_sick_care` 话术
- 不改 orchestrator 调度、安全策略、API 契约

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: 用户表达生病/身体不适（含「感冒」「头痛」「发烧」「不舒服」等）时，生产路径 `compose_contextual_reply` 与 mock 场景分支 MUST 行为一致，先表达关心与陪伴，禁止落入问卷式 open 兜底

## Impact

- `backend/app/dialogue_compose.py` — 生病关心分支
- `backend/tests/test_dialogue_compose.py` — 回归测试
- 不影响 API 契约、安全策略、记忆检索、调度逻辑
