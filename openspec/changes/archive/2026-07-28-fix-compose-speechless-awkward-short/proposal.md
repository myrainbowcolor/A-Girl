## Why

无 open `dialogue-quality` Issue，基线 26/26 全绿；但 compose 路径探测发现：用户发送短句「无语」「好无语」「尴尬」「好尴尬」「社死了」「好社死」等社交尴尬/无语口语时，`compose_contextual_reply` 返回 `None`，落入问卷式 open 兜底（如「嗯，这事不急。你想从哪儿开始说？」「你先随便丢几个词给我也行~」），缺少先接住无语/尴尬感的共情，scene_first 编排下体验机械、不像真人陪伴。

## What Changes

- `dialogue_compose.py`：在通用 open 兜底之前新增短句无语/尴尬/社死分支（len≤12），先接住无语/尴尬感，至多一个轻问
- `llm/mock.py`：场景分支与 compose 对齐，避免 mock 基线与生产路径语气分裂
- `test_dialogue_compose.py`：补充探针单测
- 不改调度频率、安全策略、记忆/编排主路径

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：补充短句无语/尴尬/社死口语的 compose/mock 共情接话要求

## Impact

- `backend/app/dialogue_compose.py`
- `backend/app/llm/mock.py`
- `backend/tests/test_dialogue_compose.py`
- 影响模块：dialogue_compose 场景分支 + mock 对齐；不影响 `safety.py`、危机干预、记忆编排
