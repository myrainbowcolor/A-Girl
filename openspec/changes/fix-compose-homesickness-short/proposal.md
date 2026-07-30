## Why

无 open `dialogue-quality` Issue，基线 26/26 全绿；但探针发现「想家了」「想家」「好想家」「想爸妈」「想回家」等想家短句 `compose_contextual_reply` 返回 `None`，落入问卷式 open 兜底。既有「节日孤独 / 想家」分支仅覆盖「落寞 / 团圆 / 过年 / 一个人」，单独说「想家了」时缺少先接住思念与空落感的共情。

## What Changes

- `dialogue_compose.py`：在通用 open 兜底之前新增短句想家/思乡分支（len≤12，关键词：想家 / 想爸妈 / 想回家 / 想父母），先接住思念与空落感，至多一个轻问
- `llm/mock.py`：场景分支与 compose 对齐
- `test_dialogue_compose.py`：补充探针单测
- 不改节日孤独既有分支触发条件、调度频率、安全策略、记忆/编排主路径

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：补充短句想家/思乡口语的 compose/mock 共情接话要求

## Impact

- `backend/app/dialogue_compose.py`
- `backend/app/llm/mock.py`
- `backend/tests/test_dialogue_compose.py`
- 影响模块：dialogue_compose/mock 场景分支；不影响 `safety.py`、危机干预、记忆编排
