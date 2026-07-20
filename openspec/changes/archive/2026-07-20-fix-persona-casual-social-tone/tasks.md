## 1. 实现

- [x] 1.1 在 `persona.py` 的 `_USER_TURN_TONE` 新增 `morning_greeting`、`friendly_greeting`、`casual_chat` 侧重文案
- [x] 1.2 在 `_user_turn_tone_hint` 接入 `is_morning_greeting_utterance`、`is_friendly_greeting_utterance`、`is_casual_social_smalltalk`、`is_casual_positive_smalltalk`，优先于通用正向分支

## 2. 测试

- [x] 2.1 `test_persona.py`：早安寒暄、友好问候、无聊闲聊、天气夸赞不误走「替 ta 高兴」侧重
- [x] 2.2 `test_persona.py`：真开心分享仍走 `positive` 侧重
- [x] 2.3 `cd backend && python -m pytest --ignore=tests/test_dialogue_quality.py -q`
- [x] 2.4 `cd backend && python scripts/run_dialogue_quality.py --strict`
- [x] 2.5 `cd .. && npx openspec validate --specs`
