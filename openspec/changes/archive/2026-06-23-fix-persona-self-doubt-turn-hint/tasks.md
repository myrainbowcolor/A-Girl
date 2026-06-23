## 1. Persona 自我怀疑侧重

- [x] 1.1 在 `persona.py` 新增 `_SELF_DOUBT_KEYWORDS` 与 `_USER_TURN_TONE["self_doubt"]` 文案
- [x] 1.2 在 `_user_turn_tone_hint()` 中想念判断之后、sentiment 负向判断之前检查自我怀疑关键词

## 2. 测试与验证

- [x] 2.1 `test_persona.py` 新增自我怀疑句 prompt 含专用侧重、纯低落句仍为共情侧重
- [x] 2.2 运行 `pytest` 全量 + `run_dialogue_quality.py --strict` + `npx openspec validate --specs`
