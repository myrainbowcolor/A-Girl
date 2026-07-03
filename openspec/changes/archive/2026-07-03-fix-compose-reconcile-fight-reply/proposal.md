## Why

对话质量评测 26 场景全绿，无 open `dialogue-quality` Issue。但 `scene_first` 编排优先调用 `compose_contextual_reply`，在 `reconcile_after_fight` 场景（「跟对象吵架了，现在谁也不理谁」「其实也有我的问题，但就是拉不下脸」「你说我要不要先发消息」）时 compose 未命中任何分支（返回 None），虽由 mock 场景引擎兜底通过评测，生产路径与 mock 行为不一致；真实 LLM 路径下吵架和好场景易落入 `compose_open_reply` 问卷式兜底，削弱情感拟真度。

修复前 compose 路径可能回复「是突然这样，还是已经有一阵子了？」类问卷句，而非 mock 已有的「吵架后的沉默最磨人……现在心里是气多，还是委屈多？」共情接话。

## What Changes

- 在 `backend/app/dialogue_compose.py` 的 `compose_contextual_reply` 中增加吵架/冷战/和好分支（须在通用负面 open 兜底之前），与 `mock.py` 场景分支对齐
- 区分首轮吵架倾诉、拉不下脸别扭追问、是否先发消息求建议三轮
- 补充 `test_dialogue_compose.py` 单测覆盖 `reconcile_after_fight` 三轮
- 不改 orchestrator 调度、安全策略、API 契约

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: 用户表达吵架/冷战/和好别扭（含「吵架」「冷战」「拉不下脸」「先发消息」等）时，生产路径 `compose_contextual_reply` 与 mock 场景分支 MUST 行为一致，先接住别扭情绪、不站队评判对方，禁止落入问卷式 open 兜底

## Impact

- `backend/app/dialogue_compose.py` — 吵架和好共情分支
- `backend/tests/test_dialogue_compose.py` — 回归测试
- 不影响 API 契约、安全策略、记忆检索、调度逻辑
