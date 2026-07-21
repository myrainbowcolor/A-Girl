## Why

无 open 的 `dialogue-quality` Issue 时，基线评测 26/26 全绿，但探针发现极简口语「早」「好累」在 `scene_first` 生产路径下 `compose_contextual_reply` 返回 `None`，落入 `compose_open_reply` 问卷式兜底（如「是突然这样，还是已经有一阵子了？」）或泛化接话，拟真度不足。单字「累」已有专属分支，「好累」与单字「早」应同等覆盖。

## What Changes

- `dialogue_compose.py`：为整句「好累」扩展疲惫共情分支（与单字「累」并列）；为整句「早」扩展早安寒暄分支（与「早呀/早安」并列）
- `mock.py`：对齐上述分支，避免「好累」落入通用负面「嗯……不太好受」套话
- 补充 `test_dialogue_compose.py` 单测
- 更新 `openspec/specs/persona/spec.md` delta

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：口语化回复约束中补充极简「早」「好累」的 compose/mock 行为要求

## Impact

- `backend/app/dialogue_compose.py`
- `backend/app/llm/mock.py`
- `backend/tests/test_dialogue_compose.py`
- 不影响安全、危机干预、记忆主路径
