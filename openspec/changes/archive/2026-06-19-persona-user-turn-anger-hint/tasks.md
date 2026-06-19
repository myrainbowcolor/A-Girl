## 1. Persona 愤怒侧重

- [x] 1.1 在 `persona.py` 新增 `_ANGER_KEYWORDS` 与 `_USER_TURN_TONE["angry"]` 文案
- [x] 1.2 在 `_user_turn_tone_hint()` 中怀旧判断之后、sentiment 判断之前检查愤怒关键词

## 2. 测试与验证

- [x] 2.1 `test_persona.py` 新增愤怒句 prompt 含发泄侧重、纯低落句仍为共情侧重
- [x] 2.2 运行 `pytest` 全量 + `run_dialogue_quality.py --strict` + `npx openspec validate --specs`
