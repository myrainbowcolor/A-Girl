## Why

无 open `dialogue-quality` Issue，基线 26/26 全绿；但 compose 路径探测发现：用户发送短句绝望/迷茫/破防/憋屈/心痛等低落口语（如「好绝望」「迷茫」「破防了」「憋屈」「心痛」）或单字「烦」「烦啊」时 `compose_contextual_reply` 返回 `None`，scene_engine 亦未命中，最终落入 `compose_open_reply` 问卷式兜底（如「好，我收到了。不用一次说完~」），缺少先接住情绪的拟真感。mock 通用负面情绪分支已覆盖相关关键词，scene_first 编排下 compose 应与 mock 对齐。

## What Changes

- `dialogue_compose.py`：在 open 兜底之前扩展短句低落倾诉分支关键词（绝望/无助/迷茫/空虚/破防/憋屈/心痛/心碎/泪目/要哭等），扩展单字「烦」「烦啊」短句分支，并将「绷不住」并入倦怠极限分支
- `test_dialogue_compose.py`：补充「好绝望」「迷茫」「破防」「憋屈」「烦」探针单测
- 不改调度/安全/记忆主路径

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：补充绝望/迷茫/破防等短句低落口语及单字「烦」compose 路径要求，禁止落入问卷式 open 兜底

## Impact

- `backend/app/dialogue_compose.py`
- `backend/tests/test_dialogue_compose.py`
- 影响模块：dialogue_compose 场景分支；不影响 `safety.py`、危机干预、记忆编排
