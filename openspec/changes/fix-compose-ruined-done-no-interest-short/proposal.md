## Why

无 open 的 `dialogue-quality` Issue；按上一轮记忆探针「废了 / 完了 / 提不起兴趣」。实测短句「废了」「我废了」「好废」「完了」「我完了」「完蛋了」「提不起兴趣」「提不起兴趣来」时，`compose_contextual_reply` 返回 `None`，落入问卷式 open 兜底（如「你想从哪儿开始说」「好，我收到了」）；`mock.py` 返回空串。既有「没救了」「提不起劲」「心累」分支均未覆盖这些口语变体，情感陪伴拟真度受损。

## What Changes

- 在 `dialogue_compose.py` 新增 ≤12 字「废了 / 好废 / 完了（整句精确）/ 我完了 / 完蛋 / 提不起兴趣」短句共情分支，按关键词分流话术
- 裸子串「完了」不用于完成义短句（如「做完了」「写完了」），避免误路由
- `mock.py` 场景路径与 `_VENT` / `_user_tone` 对齐，禁止空串或问卷兜底
- 补充单元测试；同步 persona delta / 主 spec
- **不改** `safety.py`：口语「完了 / 废了」不视为危机信号（危机仍仅由既有关键词触发）

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: 新增短句「废了 / 完了 / 提不起兴趣」compose/mock 共情回应要求

## Impact

- `backend/app/dialogue_compose.py`
- `backend/app/llm/mock.py`
- `backend/tests/test_dialogue_compose.py`
- `backend/tests/test_mock_llm.py`
- `openspec/specs/persona/spec.md`（归档时 sync）
- 不改 API / DB / 安全策略 / 编排主路径
