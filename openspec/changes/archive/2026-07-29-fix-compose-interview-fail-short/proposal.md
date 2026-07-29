## Why

无 open `dialogue-quality` Issue，基线 26/26 全绿；但探针发现两处相关缺口：
1. 「没通过」被 `is_positive_utterance` 误判为正向（命中关键词「通过」），compose/mock 返回「太棒了！替你开心～」，情感陪伴完全跑偏。
2. 「面试砸了」「面试挂了」「落选了」「搞砸了」等选拔/面试失利短句 `compose_contextual_reply` 返回 `None`，落入问卷式 open 兜底，缺少先接住挫败感的共情。

## What Changes

- `sentiment_lexicon.py`：为「通过」「录取」补充否定前缀（没通过/未通过/不通过、没录取/未录取），避免正向误判
- `dialogue_compose.py`：在通用 open 兜底之前新增短句选拔/面试失利分支（len≤12，关键词：面试砸/面试挂/没通过/落选/搞砸），先接住挫败感，至多一个轻问
- `llm/mock.py`：场景分支与 compose 对齐
- `test_sentiment_lexicon.py` / `test_dialogue_compose.py`：补充探针单测
- 不改调度频率、安全策略、记忆/编排主路径、既有考试失利分支

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：补充正向误判修复与短句选拔/面试失利口语的 compose/mock 共情接话要求

## Impact

- `backend/app/sentiment_lexicon.py`
- `backend/app/dialogue_compose.py`
- `backend/app/llm/mock.py`
- `backend/tests/test_sentiment_lexicon.py`
- `backend/tests/test_dialogue_compose.py`
- 影响模块：情感词典否定匹配 + dialogue_compose/mock 场景分支；不影响 `safety.py`、危机干预、记忆编排
