## Why

无 open `dialogue-quality` Issue，基线 26/26 全绿；但 compose 路径探测发现：用户发送短句「考砸了」「没考好」「挂科了」等考试失利口语时，`compose_contextual_reply` 返回 `None`，落入问卷式 open 兜底（如「好，我接住了。慢慢讲~」「我在。你想到什么就说什么~」），缺少先接住失利挫败感的共情。既有考试焦虑分支覆盖「高考/考试/紧张」等考前语境，不覆盖考后失利短句；默认受众为未成年人/学生，该缺口影响情感陪伴拟真度。

## What Changes

- `dialogue_compose.py`：在通用 open 兜底之前新增短句考试失利分支（len≤12，关键词：考砸/没考好/挂科等），先接住挫败感，至多一个轻问；须排除家长育儿语境（含「孩子/儿子/女儿」）
- `llm/mock.py`：场景分支与 compose 对齐
- `test_dialogue_compose.py`：补充探针单测
- 不改调度频率、安全策略、记忆/编排主路径、既有考前焦虑分支

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：补充短句考试失利口语的 compose/mock 共情接话要求

## Impact

- `backend/app/dialogue_compose.py`
- `backend/app/llm/mock.py`
- `backend/tests/test_dialogue_compose.py`
- 影响模块：dialogue_compose 场景分支 + mock 对齐；不影响 `safety.py`、危机干预、记忆编排
