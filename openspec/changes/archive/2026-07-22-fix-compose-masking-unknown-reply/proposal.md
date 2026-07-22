## Why

对话质量评测 26 场景全绿，无 open `dialogue-quality` Issue。但生产路径 `scene_first` 优先调用 `compose_contextual_reply`，在 `short_reply_user` 场景用户说「不知道」「说不上」时 compose 返回 `None`（仅覆盖「说不清」「说不上来」变体），落入问卷式 open 兜底；而 `mock.py` 场景分支已对整句「不知道」「说不清」「说不上」返回 masking 低落共情接话。与 persona spec 要求的极简 masking 口语处理不一致，真实 LLM 路径下体验偏弱。

## What Changes

- 在 `dialogue_compose.py` 扩展 masking 分支，覆盖整句「不知道」「说不上」，与 mock 行为对齐
- 回复模板：轻轻接住、不逼想清楚、可轻问一句，禁止问卷连珠炮；句首不以「嗯」开头
- 补充 `test_dialogue_compose.py` 探针用例

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: 生产路径 compose 对整句「不知道」「说不上」MUST 返回 masking 低落共情接话，与 mock 一致，禁止落入 open 兜底

## Impact

- `backend/app/dialogue_compose.py`：masking 分支扩展
- `backend/tests/test_dialogue_compose.py`：新增 compose 探针
- 不影响 safety、危机干预、记忆主路径
