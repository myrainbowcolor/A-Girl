## Why

`bored_smalltalk` 场景评测虽 100 分通过，但 transcript 显示用户说「好无聊啊」「你在干嘛」时 NPC 话术自然、avatar 却仍为「平静 idle」，与轻松闲聊的口语温度不符。此前已为早安寒暄、夸赞天气等补了温和正向标注；无聊摸鱼闲聊属于同类社交场景，应复用同一模式驱动微笑/nod，而非误走负面安慰或呆板平静脸。

当前 transcript 片段：
- 用户：「好无聊啊」→ 回复自然，avatar：平静
- 用户：「你在干嘛」→ 回复自然，avatar：平静

## What Changes

- 在 `sentiment_lexicon.py` 新增 `is_casual_social_smalltalk`：识别无聊摸鱼（「好无聊啊」）与社交探问（「你在干嘛」）口语
- 在 `analyzer.py` 对该类句返回温和正向 sentiment（≈0.38、label「闲聊」），**不**将「无聊」加入 `_NEGATIVE`（避免担心脸误判）
- 为 `bored_smalltalk` 场景首轮与末轮补充 `expect_warmth`，锁定 avatar 微笑表现
- 补充 analyzer/avatar 单元测试

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `emotion-relationship`：新增「无聊/社交探问闲聊」温和正向标注需求
- `voice-avatar`：新增对应 avatar 微笑/nod 映射需求

## Impact

- `backend/app/sentiment_lexicon.py`
- `backend/app/emotion/analyzer.py`
- `backend/app/dialogue_quality/scenarios.py`
- `backend/tests/test_analyzer_insight.py`
- `backend/tests/test_avatar.py`
- 不影响 safety、危机干预、记忆主路径；persona 侧 `_user_turn_tone_hint` 将随 sentiment>0.3 自动追加同频侧重

## 成功标准

- `bored_smalltalk` 场景「好无聊啊」「你在干嘛」轮次 avatar 为微笑/nod
- `python3 -m pytest` 全绿
- `run_dialogue_quality.py --strict` 26/26 通过
