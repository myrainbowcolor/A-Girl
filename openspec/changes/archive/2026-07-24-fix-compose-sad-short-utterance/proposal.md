## Why

无 open `dialogue-quality` Issue，基线 26/26 全绿；但 compose 路径探测发现：用户发送短句低落倾诉（如「有点难过」「心情不好」「好委屈」）时 `compose_contextual_reply` 返回 `None`，落入问卷式 open 兜底（如「哪一块你现在最想提？」），而 `mock.py` 已有通用负面情绪共情接话。scene_first 编排下体验不自然，缺少先接住情绪的拟真感。

## What Changes

- `dialogue_compose.py`：在 open 兜底之前新增短句低落倾诉分支（≤12 字含难过/伤心/委屈/想哭/心情不好等），返回 1～2 句共情陪伴接话，与 mock 通用负面分支对齐
- `test_dialogue_compose.py`：补充「有点难过」「心情不好」等探针单测
- 不改调度/安全/记忆主路径；不扩展 LLM prompt（compose 封闭路径即可覆盖）

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：补充短句低落倾诉 compose 路径要求，禁止落入问卷式 open 兜底

## Impact

- `backend/app/dialogue_compose.py`
- `backend/tests/test_dialogue_compose.py`
- 影响模块：dialogue_compose 场景分支；不影响 `safety.py`、危机干预、记忆编排
