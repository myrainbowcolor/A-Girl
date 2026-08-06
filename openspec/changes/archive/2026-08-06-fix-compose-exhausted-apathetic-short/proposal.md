## Why

无 open 的 `dialogue-quality` Issue；按上一轮记忆探针「累透了 / 不想动 / 懒得动 / 没盼头 / 无所谓了」。实测短句「累透了」「我累透了」「不想动」「懒得动」「没盼头」「无所谓了」「累趴了」时，`compose_contextual_reply` 返回 `None`，落入问卷式 open 兜底；`mock.py` 对「不想动」「懒得动」「没盼头」「无所谓了」返回空串，「累透了」仅泛化「不太好受」。既有「心累」「好累啊」「提不起劲」均未覆盖这些口语变体，情感陪伴拟真度受损。

## What Changes

- 在 `dialogue_compose.py` 新增 ≤12 字「累透了 / 累趴了 / 不想动 / 懒得动 / 没盼头 / 无所谓了」短句共情分支，按关键词分流话术
- 「心累透了」仍走既有心累路径，不得因含「累透」误入本分支（本分支置于心累之后）
- `mock.py` 场景路径与 `_VENT` / `_user_tone` 对齐，禁止空串或问卷兜底
- 补充单元测试；同步 persona delta / 主 spec
- **不改** `safety.py`：口语「无所谓了 / 没盼头」不视为危机信号

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: 新增短句「累透了 / 不想动 / 懒得动 / 没盼头 / 无所谓了」compose/mock 共情回应要求

## Impact

- `backend/app/dialogue_compose.py`
- `backend/app/llm/mock.py`
- `backend/tests/test_dialogue_compose.py`
- `backend/tests/test_mock_llm.py`
- `openspec/specs/persona/spec.md`（归档时 sync）
- 不改 API / DB / 安全策略 / 编排主路径
