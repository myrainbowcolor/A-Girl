## 1. mock 疲惫倾诉分支

- [x] 1.1 在 `mock.py` `_scene_reply` 通用疲惫兜底前新增「疲惫 + 倾诉意愿」分支，亲密/朋友差异化话术
- [x] 1.2 补充 `test_mock.py`：断言「想靠着你说说」回复含陪伴倾听、不含「不想说也没关系」

## 2. persona LLM 路径

- [x] 2.1 在 `persona.py` 新增 `fatigue_talk` 侧重与关键词检测（疲惫词 AND 倾诉意愿词）
- [x] 2.2 补充 `test_persona.py`：断言 `user_text="今天过得好累，想靠着你说说"` 含疲惫想聊侧重

## 3. 验证

- [x] 3.1 `cd backend && python3 -m pytest --ignore=tests/test_dialogue_quality.py -q`
- [x] 3.2 `python3 scripts/run_dialogue_quality.py --strict` 与 `python3 -m pytest tests/test_dialogue_quality.py -q`
- [x] 3.3 `cd .. && npx openspec validate --specs`
