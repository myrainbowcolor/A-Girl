## Why

无 open `dialogue-quality` Issue，基线 26/26 全绿；但探针发现「心凉了」「好心凉」「寒心了」「好寒心」「受够了」「我受够了」等短句 `compose_contextual_reply` 返回 `None`，落入问卷式 open 兜底；`mock.py` 对同关键词返回空串。上一轮 `fix-compose-guilt-slacking-short` 明确未扩「心凉/寒心/受够了」缺口；既有「撑不住/受不了」分支不覆盖「受够了」，短句低落关键词亦不含心凉/寒心。

成功标准：≤12 字心凉/寒心/受够了短句走对应共情接话（非 open 兜底、非空串）；既有「撑不住/受不了」与短句低落路径不受破坏；pytest 全绿 + dialogue quality strict 26/26。

## What Changes

- `dialogue_compose.py`：在通用 open 兜底之前，新增 ≤12 字心凉/寒心/受够了短句分支，按关键词轻分流
- `llm/mock.py`：同分支对齐
- `test_dialogue_compose.py` / `test_mock_llm.py`：补充探针与回归
- 不改安全策略、调度频率、记忆/编排主路径、avatar 映射

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：短句心凉/寒心/受够了 compose/mock 共情接话

## Impact

- `backend/app/dialogue_compose.py`
- `backend/app/llm/mock.py`
- `backend/tests/test_dialogue_compose.py`
- `backend/tests/test_mock_llm.py`
- 影响模块：dialogue_compose/mock 场景分支；不影响 `safety.py`、危机干预、记忆编排
