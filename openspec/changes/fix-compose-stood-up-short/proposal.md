## Why

无 open `dialogue-quality` Issue，基线 26/26 全绿；但探针发现「被鸽了」「放鸽子了」「放我鸽子」「又被鸽了」等被放鸽子/爽约短句 `compose_contextual_reply` 返回 `None`，落入问卷式 open 兜底；`mock.py` 对同关键词返回空串。上一轮 `fix-compose-layoff-short` 明确未扩「被鸽」缺口。

成功标准：≤12 字被鸽/放鸽子短句走被鸽共情接话（非 open 兜底、非空串）；既有失恋分手 / 吵架冷战 / 短句低落路径不受破坏；pytest 全绿 + dialogue quality strict 26/26。

## What Changes

- `dialogue_compose.py`：新增 ≤12 字被鸽/放鸽子短句分支（被鸽/放鸽子/放我鸽子/爽约），置于通用 open 兜底之前
- `llm/mock.py`：同分支对齐
- `test_dialogue_compose.py` / `test_mock_llm.py`：补充探针与回归
- 不改安全策略、调度频率、记忆/编排主路径、avatar 映射

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：短句被鸽/放鸽子 compose/mock 共情接话

## Impact

- `backend/app/dialogue_compose.py`
- `backend/app/llm/mock.py`
- `backend/tests/test_dialogue_compose.py`
- `backend/tests/test_mock_llm.py`
- 影响模块：dialogue_compose/mock 场景分支；不影响 `safety.py`、危机干预、记忆编排
