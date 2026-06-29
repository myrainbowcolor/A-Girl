## Why

`stranger_first_greet` 与 `long_session_warmup` 场景评测虽 100 分通过，但 transcript 显示用户说「你好呀」「嗨，第一次来」时 NPC 话术温暖、avatar 却仍为「平静 idle」，与友好问候的口语温度不符。此前已为早安寒暄、夸赞天气、无聊摸鱼等补了温和正向标注；初识/重逢友好问候属于同类社交场景，应复用同一模式驱动微笑/nod。

当前 transcript 片段：
- 用户：「你好呀」→ 回复自然，avatar：平静
- 用户：「嗨，第一次来」→ 回复自然，avatar：平静

## What Changes

- 在 `sentiment_lexicon.py` 新增 `is_friendly_greeting_utterance`：识别友好问候（「你好」「你好呀」「嗨」「第一次来」），句长 ≤12，负面词排除
- 在 `analyzer.py` 对该类句返回温和正向 sentiment（≈0.38、label「寒暄」）
- **勿**将「嗯」入问候正向；带「难过」等负面倾诉的问候仍走 comfort
- 补充 analyzer/avatar 单元测试

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `emotion-relationship`：新增「友好问候」温和正向标注需求
- `voice-avatar`：新增对应 avatar 微笑/nod 映射需求

## Impact

- `backend/app/sentiment_lexicon.py`
- `backend/app/emotion/analyzer.py`
- `backend/tests/test_analyzer_insight.py`
- `backend/tests/test_avatar.py`
- 不影响 safety、危机干预、记忆主路径；persona 侧 `_user_turn_tone_hint` 将随 sentiment>0.3 自动追加同频侧重

## 成功标准

- `stranger_first_greet`「你好呀」与 `long_session_warmup`「嗨，第一次来」轮次 avatar 为微笑/nod
- `python3 -m pytest` 全绿
- `run_dialogue_quality.py --strict` 26/26 通过
