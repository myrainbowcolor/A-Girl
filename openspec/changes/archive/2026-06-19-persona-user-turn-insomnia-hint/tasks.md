## 1. Persona 实现

- [x] 1.1 在 `persona.py` 增加 `_INSOMNIA_KEYWORDS` 与 `_USER_TURN_TONE["insomnia"]` 文案
- [x] 1.2 在 `_user_turn_tone_hint()` 愤怒分支之后、通用负向之前匹配失眠关键词

## 2. 测试与验证

- [x] 2.1 在 `test_persona.py` 增加失眠句与纯低落句对照断言
- [x] 2.2 运行 `pytest --ignore=tests/test_dialogue_quality.py` 全绿
- [x] 2.3 运行 `run_dialogue_quality.py --strict` 与 `test_dialogue_quality.py` 全绿
- [x] 2.4 运行 `npx openspec validate --specs` 通过
