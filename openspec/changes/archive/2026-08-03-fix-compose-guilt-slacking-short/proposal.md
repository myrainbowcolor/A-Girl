## Why

无 open `dialogue-quality` Issue，基线 26/26 全绿；但探针发现「好愧疚」「内疚」「好后悔」「摆烂了」等无消费语境短句 `compose_contextual_reply` 返回 `None`，落入问卷式 open 兜底；`mock.py` 对同关键词返回空串。上一轮 `fix-compose-stood-up-short` 明确未扩「愧疚/摆烂/内疚/好后悔」缺口；既有冲动消费分支仅在含「钱/买/手/花」时命中「后悔」，纯短句「好后悔」仍漏接。

成功标准：≤12 字愧疚/内疚/摆烂/无消费后悔短句走对应共情接话（非 open 兜底、非空串、非冲动消费话术）；既有冲动消费后悔路径（如「乱花钱好后悔」「好后悔买了」）不受破坏；pytest 全绿 + dialogue quality strict 26/26。

## What Changes

- `dialogue_compose.py`：在冲动消费分支之后、通用 open 兜底之前，新增 ≤12 字愧疚/内疚/摆烂/无消费后悔短句分支
- `llm/mock.py`：同分支对齐
- `test_dialogue_compose.py` / `test_mock_llm.py`：补充探针与回归（含消费后悔回归）
- 不改安全策略、调度频率、记忆/编排主路径、avatar 映射

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：短句愧疚/内疚/摆烂/无消费后悔 compose/mock 共情接话

## Impact

- `backend/app/dialogue_compose.py`
- `backend/app/llm/mock.py`
- `backend/tests/test_dialogue_compose.py`
- `backend/tests/test_mock_llm.py`
- 影响模块：dialogue_compose/mock 场景分支；不影响 `safety.py`、危机干预、记忆编排
