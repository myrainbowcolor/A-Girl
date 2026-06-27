## Why

`morning_checkin` 场景首轮用户说「早呀，今天又要上班了」时，NPC 话术已自然（「早！今天也要上班呀，先给自己鼓鼓劲～」），但 avatar 仍为「平静/idle」，像客服打卡而非朋友互道早安。`latest.json` transcript 显示该轮 `avatar_expression` 为平静，与场景描述「早安闲聊应自然，不要像客服打卡」的拟真目标不符。

## What Changes

- 在情感词典中识别**无困倦标记**的早安寒暄句（含「早呀」「早安」「早上好」等），返回温和正向 `user_sentiment`（约 0.38），驱动 avatar 微笑/nod
- 含「困」「困死」「不想起床」等困倦标记的早安句仍走现有负向/comfort 路径，行为不变
- 为 `morning_checkin` 首轮补充 `expect_warmth` 回归约束
- 补充 analyzer 与对话质量单测

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `emotion-relationship`：新增早安寒暄整句温和正向情感标注需求
- `voice-avatar`：新增用户早安寒暄时 avatar 微笑/nod 表现需求

## Impact

- `backend/app/sentiment_lexicon.py`：新增 `is_morning_greeting_utterance` 辅助函数
- `backend/app/emotion/analyzer.py`：早安寒暄分支
- `backend/app/dialogue_quality/scenarios.py`：`morning_checkin` 首轮期望
- `backend/tests/test_analyzer_insight.py`：词典单测
