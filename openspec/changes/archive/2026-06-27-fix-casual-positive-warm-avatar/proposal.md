## Why

`long_session_warmup` 场景第 2～3 轮用户分享「今天天气不错」「刚看完一部挺好的电影」时，NPC 话术已自然（「是吧，这种天出门心情都会好一点」「什么片子呀？好看的话给我也安利一下～」），但 avatar 仍为「平静/idle」，像客服复读而非朋友闲聊。`latest.json` transcript 显示这两轮 `avatar_expression` 为平静，与轻松正向闲聊的拟真目标不符（类比已修复的早安寒暄微笑问题）。

## What Changes

- 在情感词典中识别**轻松正向闲聊**句（天气夸赞、分享好看电影/片子等），返回温和正向 `user_sentiment`（约 0.38），驱动 avatar 微笑/nod
- 含负面标记的同类句（如「天气不错但心情不好」）仍走现有逻辑，行为不变
- 为 `long_session_warmup` 第 2～3 轮补充 `expect_warmth` 回归约束
- 补充 analyzer 与对话质量单测

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `emotion-relationship`：新增轻松正向闲聊整句温和正向情感标注需求
- `voice-avatar`：新增用户轻松正向闲聊时 avatar 微笑/nod 表现需求

## Impact

- `backend/app/sentiment_lexicon.py`：新增 `is_casual_positive_smalltalk` 辅助函数
- `backend/app/emotion/analyzer.py`：轻松正向闲聊分支
- `backend/app/dialogue_quality/scenarios.py`：`long_session_warmup` 轮次期望
- `backend/tests/test_analyzer_insight.py`：词典单测
