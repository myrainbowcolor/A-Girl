## Why

无 open `dialogue-quality` Issue，基线 26/26 全绿；但探针发现「心灰了」「好心灰」「心死了」「好心死」「麻了」「我麻了」「麻木了」等短句 `compose_contextual_reply` 返回 `None`，落入问卷式 open 兜底；`mock.py` 对同关键词返回空串或未覆盖。上一轮 `fix-compose-fear-short` 明确未扩「心灰/心死/麻了」缺口；既有短句低落含「灰心」但不覆盖词序相反的「心灰」，亦不含「心死」「麻了/麻木」。

成功标准：≤12 字心灰/心死/麻了/麻木短句走对应共情接话（非 open 兜底、非空串）；既有「灰心了」「心凉了」与短句低落路径不受破坏；pytest 全绿 + dialogue quality strict 26/26。

## What Changes

- `dialogue_compose.py`：在通用 open 兜底之前，新增 ≤12 字心灰/心死/麻了/麻木短句分支，按关键词轻分流
- `llm/mock.py`：同分支对齐，并补充 `_VENT` / `_user_tone` 倾诉标记
- `test_dialogue_compose.py` / `test_mock_llm.py`：补充探针与回归
- 不改安全策略、调度频率、记忆/编排主路径、avatar 映射

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：短句心灰/心死/麻了/麻木 compose/mock 共情接话

## Impact

- `backend/app/dialogue_compose.py`
- `backend/app/llm/mock.py`
- `backend/tests/test_dialogue_compose.py`
- `backend/tests/test_mock_llm.py`
- 影响模块：dialogue_compose/mock 场景分支；不影响 `safety.py`、危机干预、记忆编排
