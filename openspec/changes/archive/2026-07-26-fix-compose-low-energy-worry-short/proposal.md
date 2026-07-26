## Why

无 open `dialogue-quality` Issue，基线 26/26 全绿；但 compose 路径探测发现：用户发送短句没劲/没意思（如「没劲」「好没劲」）、心里堵/堵心（如「心里堵」「堵得慌」）或短句慌张/担心（如「慌」「害怕」「好担心」）时 `compose_contextual_reply` 返回 `None`，落入问卷式 open 兜底（如「好，我收到了。不用一次说完~」），而 `mock.py` 的 `_LOW`/`_VENT` 关键词已覆盖相关情绪。scene_first 编排下体验不自然，缺少先接住情绪的拟真感。

## What Changes

- `dialogue_compose.py`：扩展 emo/低落分支覆盖「没劲」「没意思」「低落」；新增心里堵/堵心短句分支；新增短句慌张/担心分支（排除育儿语境，与既有分支不冲突）
- `test_dialogue_compose.py`：补充「没劲」「心里堵」「堵得慌」「慌」「好担心」探针单测
- 不改调度/安全/记忆主路径

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：补充没劲/堵心/短句慌张担心 compose 路径要求，禁止落入问卷式 open 兜底

## Impact

- `backend/app/dialogue_compose.py`
- `backend/tests/test_dialogue_compose.py`
- 影响模块：dialogue_compose 场景分支；不影响 `safety.py`、危机干预、记忆编排
