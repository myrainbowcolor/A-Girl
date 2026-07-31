## Why

无 open `dialogue-quality` Issue，基线 26/26 全绿；但探针发现「好丢脸」「丢脸」「好丢人」「丢人」「好羞耻」「羞耻」「社恐了」「好社恐」等丢脸/羞耻/社恐短句 `compose_contextual_reply` 返回 `None`，落入问卷式 open 兜底（如「好，我收到了。不用一次说完~」）；`mock.py` 对同关键词返回空串。既有「短句无语/尴尬/社死」分支已覆盖社交尴尬感，尚未覆盖「丢脸 / 丢人 / 羞耻 / 社恐」。

## What Changes

- `dialogue_compose.py`：扩展短句无语/尴尬/社死分支，追加「丢脸」「丢人」「羞耻」「社恐」并按关键词分流话术
- `llm/mock.py`：同分支与 `_VENT` / `_user_tone` 对齐，避免 mock 空回复与问卷兜底
- `test_dialogue_compose.py` / `test_mock_llm.py`：补充探针
- 不改安全策略、调度频率、记忆/编排主路径、avatar 映射

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：短句丢脸/羞耻/社恐 compose/mock 共情接话覆盖

## Impact

- `backend/app/dialogue_compose.py`
- `backend/app/llm/mock.py`
- `backend/tests/test_dialogue_compose.py`
- `backend/tests/test_mock_llm.py`
- 影响模块：dialogue_compose/mock 场景分支；不影响 `safety.py`、危机干预、记忆编排
