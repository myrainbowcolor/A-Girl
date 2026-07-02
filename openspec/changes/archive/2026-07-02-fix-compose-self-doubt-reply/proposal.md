## Why

对话质量评测 26 场景全绿，无 open `dialogue-quality` Issue。但 `scene_first` 编排优先调用 `compose_contextual_reply`，在 `jealous_comparison` 场景（「同学都升职了，就我还原地踏步」「是不是我太差劲了」）时 compose 未命中任何分支（返回 None），虽由 mock 场景引擎兜底通过评测，生产路径与 mock 行为不一致；真实 LLM 路径下比较/自我怀疑场景易落入 `compose_open_reply` 问卷式兜底（如「突然还是一阵子」），削弱情感拟真度。

修复前 compose 路径可能回复「是突然这样，还是已经有一阵子了？」类问卷句，而非 mock 已有的「跟别人一比就否定自己，这种落差真的很难受」共情接话。

## What Changes

- 在 `backend/app/dialogue_compose.py` 的 `compose_contextual_reply` 中增加比较/自我怀疑分支（须在通用负面 open 兜底之前），与 `mock.py` 场景分支对齐
- 区分「升职/原地踏步」比较心态与「差劲/太差」自我怀疑追问
- 补充 `test_dialogue_compose.py` 单测覆盖 `jealous_comparison` 两轮
- 不改 orchestrator 调度、安全策略、API 契约

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: 用户表达比较心态或自我怀疑时，生产路径 `compose_contextual_reply` 与 mock 场景分支 MUST 行为一致，先承认落差感、不急着反驳或灌鸡汤，禁止落入问卷式 open 兜底或简单说「别比了」

## Impact

- `backend/app/dialogue_compose.py` — 比较/自我怀疑共情分支
- `backend/tests/test_dialogue_compose.py` — 回归测试
- 不影响 API 契约、安全策略、记忆检索、调度逻辑
