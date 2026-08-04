## Why

无 open `dialogue-quality` Issue，基线 26/26 全绿；但探针发现：「怕了」「我怕了」`compose_contextual_reply` 返回 `None`，落入问卷式 open 兜底；「好害怕」「害怕」虽已命中 compose 慌张分支，但 `mock.py` `_empathy_reply` 因关键词含「害怕」被误路由到育儿焦虑话术（「当家长担心孩子」）；「好怕」mock 返回空串。上一轮 `fix-compose-heart-cold-fed-up-short` 明确未扩「怕了」且未修「好害怕」误路由。

成功标准：≤10 字「怕了」类短句走慌张共情（非 open 兜底）；无育儿语境的「害怕/好害怕」mock 不得套用家长话术；既有育儿焦虑与「慌/好担心」路径不受破坏；pytest 全绿 + dialogue quality strict 26/26。

## What Changes

- `dialogue_compose.py`：扩展既有短句慌张/担心关键词，追加「怕了」
- `llm/mock.py`：收紧 `_empathy_reply` 育儿分支（「害怕」须有育儿语境才命中）；新增/对齐短句慌张场景分支；`_VENT` 补充相关词
- `test_dialogue_compose.py` / `test_mock_llm.py`：补充探针与回归
- 不改安全策略、调度频率、记忆/编排主路径、avatar 映射

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：短句「怕了」覆盖 + mock「害怕」无育儿语境不得误路由育儿

## Impact

- `backend/app/dialogue_compose.py`
- `backend/app/llm/mock.py`
- `backend/tests/test_dialogue_compose.py`
- `backend/tests/test_mock_llm.py`
- 影响模块：dialogue_compose/mock 场景分支；不影响 `safety.py`、危机干预、记忆编排
