## 1. persona 实现

- [x] 1.1 在 `backend/app/persona.py` 新增 `_user_turn_tone_hint(user_text)`，复用 `analyze_lexicon` 与怀旧关键词
- [x] 1.2 在 `build_system_prompt` 中于「语气微调」后条件注入 `【本轮侧重】` 段

## 2. 测试与验证

- [x] 2.1 在 `backend/tests/test_persona.py` 新增：负面用户句 + 平和 NPC 情绪时 prompt 含共情侧重
- [x] 2.2 在 `backend/tests/test_persona.py` 新增：正向/中性场景断言
- [x] 2.3 运行 `cd backend && python3 -m pytest --ignore=tests/test_dialogue_quality.py -q`
- [x] 2.4 运行 `python3 scripts/run_dialogue_quality.py --strict` 与 `python3 -m pytest tests/test_dialogue_quality.py -q`
- [x] 2.5 运行 `cd .. && npx openspec validate --specs`
