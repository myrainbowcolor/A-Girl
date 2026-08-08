## Why

无 open 的 `dialogue-quality` Issue；按上一轮记忆探针「感觉空了 / 掏空了」。实测短句「感觉空了」「掏空了」「感觉掏空了」时，`compose_contextual_reply` 与 `mock.py` 均返回空/`None`（既有分支仅覆盖「整个人」+「空了」或「被掏空」），用户表达发空/被掏空感时无法被共情接住，情感陪伴拟真度受损。

示例失败：`compose_contextual_reply("感觉空了", []) → None`；`MockLLMProvider().generate(..., "掏空了") → ""`。

## What Changes

- 扩展 `dialogue_compose.py` 既有「整个人空了」短句分支：≤12 字命中「感觉空了」或「掏空了」时共情接住（仍不用裸「空了」）
- `mock.py` 同条件对齐；`_VENT` / `_user_tone` 补词，避免中性空串
- 补充 compose / mock 单元测试
- 同步 persona delta
- **不改** `safety.py`、危机词表、调度频率、avatar、API/DB

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: 短句「感觉空了 / 掏空了」口语要求 compose 与 mock 共情接住，并与既有「整个人空了 / 被掏空」路径兼容

## Impact

- `backend/app/dialogue_compose.py`
- `backend/app/llm/mock.py`
- `backend/tests/test_dialogue_compose.py`
- `backend/tests/test_mock_llm.py`
- `openspec/specs/persona/spec.md`（归档时 sync）
- 不改 API / DB / 安全策略 / 编排主路径结构
