## Why

对话质量评测 26 场景全绿，无 open `dialogue-quality` Issue。但 `scene_first` 编排优先调用 `compose_contextual_reply`，在 `angry_at_boss` 场景（「老板今天当众骂我，气死了！」「真想立刻辞职不干了」）时 compose 未命中任何分支（返回 None），虽由 mock 场景引擎兜底通过评测，生产路径与 mock 行为不一致；真实 LLM 路径下愤怒发泄场景易落入 `compose_open_reply` 问卷式兜底，削弱情感拟真度。

修复前 compose 路径可能回复「是突然这样，还是已经有一阵子了？」类问卷句，而非 mock 已有的「当众被骂真的太过分了……先别急着做决定，我陪你把这股火慢慢说出来」共情接话。

## What Changes

- 在 `backend/app/dialogue_compose.py` 的 `compose_contextual_reply` 中增加被责骂/愤怒发泄分支（须在通用负面 open 兜底之前），与 `mock.py` 场景分支对齐
- 区分首轮当众被骂倾诉与续轮冲动辞职念头
- 补充 `test_dialogue_compose.py` 单测覆盖 `angry_at_boss` 两轮
- 不改 orchestrator 调度、安全策略、API 契约

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: 用户愤怒发泄或被当众责骂（含「气死」「骂我」「老板」等）及冲动辞职念头时，生产路径 `compose_contextual_reply` 与 mock 场景分支 MUST 行为一致，先接住火气、陪着听，禁止说教式劝冷静或落入问卷式 open 兜底

## Impact

- `backend/app/dialogue_compose.py` — 愤怒发泄共情分支
- `backend/tests/test_dialogue_compose.py` — 回归测试
- 不影响 API 契约、安全策略、记忆检索、调度逻辑
