## Why

无 open `dialogue-quality` Issue，基线 26/26 全绿；但探针发现「好自卑」「自卑」「好自卑啊」「我好自卑」等自卑短句 `compose_contextual_reply` 返回 `None`，落入问卷式 open 兜底（如「好，我收到了。不用一次说完~」）。既有「比较 / 自我怀疑」分支已覆盖「升职 / 原地踏步 / 差劲 / 不如」，`persona` 本轮侧重与 mock `_VENT` 已含「自卑」，但 compose/mock 场景分支尚未把「自卑」接进该路径。上一轮 `fix-compose-shame-social-anxiety-short` 明确未扩此缺口。

## What Changes

- `dialogue_compose.py`：扩展比较/自我怀疑分支，追加「自卑」并按关键词分流话术（自卑专用，避免套用「升职比较」话术）
- `llm/mock.py`：同分支对齐，避免 mock 空回复与问卷兜底
- `test_dialogue_compose.py` / `test_mock_llm.py`：补充探针
- 不改安全策略、调度频率、记忆/编排主路径、avatar 映射

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：短句自卑 compose/mock 共情接话覆盖

## Impact

- `backend/app/dialogue_compose.py`
- `backend/app/llm/mock.py`
- `backend/tests/test_dialogue_compose.py`
- `backend/tests/test_mock_llm.py`
- 影响模块：dialogue_compose/mock 场景分支；不影响 `safety.py`、危机干预、记忆编排
