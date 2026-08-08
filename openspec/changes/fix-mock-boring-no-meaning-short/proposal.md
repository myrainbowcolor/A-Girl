## Why

无 open 的 `dialogue-quality` Issue；按上一轮记忆探针「没意思了 / 好没意思」。实测短句「没意思了」「好没意思」「真没意思」时，`compose_contextual_reply` 已能共情接住，但 `mock.py` 返回空串（`_LOW` / 低落场景分支含「没劲」却缺「没意思」），CI mock 路径与生产 compose 不一致，情感陪伴拟真度受损。

示例失败：`compose_contextual_reply("没意思了", []) → "低落的时候不用硬撑…"`；`generate_scene_reply(..., "没意思了") → ""`。

## What Changes

- 扩展 `mock.py` emo/低落场景分支：与 compose 对齐，≤12 字命中「没劲」「没意思」「低落」时返回低落共情话术
- `_LOW` / `_user_tone` 补「没意思」，避免中性空串
- 补充 mock 单元测试；compose 侧扩展「没意思了」等变体回归
- 同步 persona delta
- **不改** `safety.py`、危机词表、调度频率、avatar、API/DB

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: 短句「没意思 / 没意思了」口语要求 mock 与既有 compose 低落共情路径一致，不得返回空串

## Impact

- `backend/app/llm/mock.py`
- `backend/tests/test_mock_llm.py`
- `backend/tests/test_dialogue_compose.py`（变体回归，可选）
- `openspec/specs/persona/spec.md`（归档时 sync）
- 不改 API / DB / 安全策略 / 编排主路径结构
