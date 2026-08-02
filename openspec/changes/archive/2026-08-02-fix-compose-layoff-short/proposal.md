## Why

无 open `dialogue-quality` Issue，基线 26/26 全绿；但探针发现「被裁了」「裁员了」「被开除了」「失业了」等失业/裁员短句 `compose_contextual_reply` 返回 `None`，落入问卷式 open 兜底；「丢工作了」虽命中分支，却被通用工作话题话术误路由（「忙不过来 / 不公平」），与失业语境不符。上一轮 `fix-compose-useless-feeling-short` 明确未扩「被裁」缺口。

成功标准：≤12 字失业/裁员短句走裁员共情接话（非 open 兜底、非通用工作话题）；既有加班疲惫 / 冲动辞职 / 工作话题路径不受破坏；pytest 全绿 + dialogue quality strict 26/26。

## What Changes

- `dialogue_compose.py`：新增 ≤12 字失业/裁员短句分支（被裁/裁员/被开除/失业/丢工作），置于通用工作话题分支之前，避免「丢工作了」误路由
- `llm/mock.py`：同分支对齐
- `test_dialogue_compose.py` / `test_mock_llm.py`：补充探针与回归
- 不改安全策略、调度频率、记忆/编排主路径、avatar 映射

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：短句失业/裁员 compose/mock 共情接话

## Impact

- `backend/app/dialogue_compose.py`
- `backend/app/llm/mock.py`
- `backend/tests/test_dialogue_compose.py`
- `backend/tests/test_mock_llm.py`
- 影响模块：dialogue_compose/mock 场景分支；不影响 `safety.py`、危机干预、记忆编排
