## Why

无 open `dialogue-quality` Issue，基线 26/26 全绿；但探针发现「好没用」「我好没用」「没用」等自我否定短句被冲动消费分支误路由，回复套用「管不住手 / 这次最让你后悔」话术，与用户语境不符。根因：冲动消费条件两侧都含「没用」，导致无消费语境的「好没用」也命中。上一轮 `fix-compose-inferiority-short` 明确未修此误路由。

成功标准：无消费语境的「好没用」类短句走自我否定共情；含「管不住手 / 乱花钱」的既有场景仍走冲动消费话术；pytest 全绿 + dialogue quality strict 26/26。

## What Changes

- `dialogue_compose.py`：收紧冲动消费分支的消费语境判定；无消费语境的 ≤12 字「没用」短句走自我否定共情话术
- `llm/mock.py`：同分支对齐，避免误套消费后悔话术
- `test_dialogue_compose.py` / `test_mock_llm.py`：补充探针与回归（含消费语境仍命中）
- 不改安全策略、调度频率、记忆/编排主路径、avatar 映射

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：短句「好没用」compose/mock 共情接话与冲动消费分流修正

## Impact

- `backend/app/dialogue_compose.py`
- `backend/app/llm/mock.py`
- `backend/tests/test_dialogue_compose.py`
- `backend/tests/test_mock_llm.py`
- 影响模块：dialogue_compose/mock 场景分支；不影响 `safety.py`、危机干预、记忆编排
