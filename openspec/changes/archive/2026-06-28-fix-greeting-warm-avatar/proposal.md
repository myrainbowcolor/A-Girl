## Why

`stranger_first_greet` 与 `long_session_warmup` 首轮虽话术温暖（「你好呀，我是小语，很高兴认识你～」），但 `latest.json` transcript 显示 avatar 仍为「平静/idle」，像文字热情、表情冷淡。此前已为早安寒暄、轻松闲聊、无聊摸鱼补了温和正向情感标注；初次见面问候属于同类社交场景，应复用同一模式驱动微笑/nod。

当前 transcript 片段：
- 用户：「你好呀」→ 回复自然，avatar：平静
- 用户：「嗨，第一次来」→ 回复自然，avatar：平静

## What Changes

- 在 `sentiment_lexicon.py` 新增 `is_friendly_greeting_utterance`：识别短句初次问候（「你好呀」「嗨，第一次来」等）
- 在 `analyzer.py` 对该类句返回温和正向 sentiment（≈0.38、label「寒暄」），**不**与早安/困倦分支冲突
- 为 `stranger_first_greet` 与 `long_session_warmup` 首轮补充 `expect_warmth`，锁定 avatar 微笑表现
- 补充 analyzer/avatar 单元测试

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `emotion-relationship`：新增「初次见面问候」温和正向情感标注需求
- `voice-avatar`：新增对应 avatar 微笑/nod 映射需求

## Impact

- `backend/app/sentiment_lexicon.py`
- `backend/app/emotion/analyzer.py`
- `backend/app/dialogue_quality/scenarios.py`
- `backend/tests/test_analyzer_insight.py`
- `backend/tests/test_avatar.py`
- 不影响 safety、危机干预、记忆主路径；persona 侧 `_user_turn_tone_hint` 将随 sentiment>0.3 自动追加同频侧重

## 成功标准

- `stranger_first_greet` 与 `long_session_warmup` 首轮 avatar 为微笑/nod
- `python3 -m pytest` 全绿
- `run_dialogue_quality.py --strict` 26/26 通过
