## Why

对话质量评测 26 场景全绿，无 open `dialogue-quality` Issue。但 `scene_first` 编排优先调用 `compose_contextual_reply`，在 `close_miss_you` 场景（「好久没聊了，有点想你」）时 compose 未命中任何分支（返回 None），虽由 mock 场景引擎兜底通过评测，生产路径与 mock 行为不一致；真实 LLM 路径下想念场景易落入 `compose_open_reply` 问卷式兜底，或「哈哈」报喜分支误路由，削弱情感拟真度。

修复前 compose 路径可能落入通用 open 兜底，而非 mock 已有的「我也想你呀～好久没聊了」依恋接话。

## What Changes

- 在 `backend/app/dialogue_compose.py` 的 `compose_contextual_reply` 中增加想念/好久未见分支（须在「哈哈」报喜之前），与 `mock.py` 场景分支对齐
- 根据上一轮 assistant 亲密标记（「亲爱的」等）区分亲密/朋友语气
- 补充 `test_dialogue_compose.py` 单测覆盖 `close_miss_you` 首轮
- 不改 orchestrator 调度、安全策略、API 契约

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: 用户表达想念或好久未见时，生产路径 `compose_contextual_reply` 与 mock 场景分支 MUST 行为一致，先柔软回应依恋，禁止落入问卷式 open 兜底或「开心起来了」报喜语气

## Impact

- `backend/app/dialogue_compose.py` — 想念/好久未见共情分支
- `backend/tests/test_dialogue_compose.py` — 回归测试
- 不影响 API 契约、安全策略、记忆检索、调度逻辑
