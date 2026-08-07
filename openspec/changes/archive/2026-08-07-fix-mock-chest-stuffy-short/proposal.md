## Why

无 open 的 `dialogue-quality` Issue；按上一轮记忆探针「心好堵 / 堵得慌」。实测短句「心好堵」「好心堵」「堵得慌」「心里堵得慌」「心堵得慌」「心里堵」「堵心」「心堵」「好堵」时，`compose_contextual_reply` 已能共情接住，但 `mock.py` 返回空串，CI/mock 路径与 compose 不一致，情感陪伴拟真度在 mock 评测侧受损。

## What Changes

- 在 `mock.py` 新增 ≤10 字「堵得慌 / 心里堵 / 堵心 / 心堵 / 好堵」短句共情分支，话术与 compose 对齐
- `_VENT` / `_user_tone` 补充同关键词，避免误判为中性空串
- 补充 mock 单元测试；扩展 compose 回归覆盖「心好堵」等变体
- 同步 persona delta：明确 mock 与 compose 行为一致
- **不改** `safety.py`、compose 既有分支逻辑、调度频率、avatar

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: 短句心里堵/堵心口语要求 mock 与 compose 行为一致，并覆盖「心好堵」等变体

## Impact

- `backend/app/llm/mock.py`
- `backend/tests/test_mock_llm.py`
- `backend/tests/test_dialogue_compose.py`（扩展既有参数化用例）
- `openspec/specs/persona/spec.md`（归档时 sync）
- 不改 API / DB / 安全策略 / 编排主路径 / `dialogue_compose.py` 关键词表
