## Why

无 open `dialogue-quality` Issue，基线 26/26 全绿；但探针发现「好失望」「失落」「灰心了」「好心酸」等失望/灰心短句 `compose_contextual_reply` 返回 `None`，落入问卷式 open 兜底（如「好，我收到了。不用一次说完~」）。既有短句低落分支已覆盖难过/委屈/崩溃/绝望等，尚未覆盖「失望 / 失落 / 灰心 / 心酸」。

## What Changes

- `dialogue_compose.py`：短句低落倾诉关键词追加「失望」「失落」「灰心」「心酸」
- `llm/mock.py`：`_VENT` / 情绪低落相关分支对齐同关键词，避免 mock 空回复与问卷兜底
- `test_dialogue_compose.py`（及必要的 mock 单测）：补充探针
- 不改安全策略、调度频率、记忆/编排主路径、avatar 映射

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：短句低落倾诉 compose/mock 共情接话关键词补充失望/失落/灰心/心酸

## Impact

- `backend/app/dialogue_compose.py`
- `backend/app/llm/mock.py`
- `backend/tests/test_dialogue_compose.py`
- `backend/tests/test_mock_llm.py`（若需对齐）
- 影响模块：dialogue_compose/mock 场景分支；不影响 `safety.py`、危机干预、记忆编排
