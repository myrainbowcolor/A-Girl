## 1. Mock 分支

- [x] 1.1 在 `llm/mock.py`「什么都不想干 / 整个人空了」分支之后、泛化低落之前新增 ≤10 字「堵得慌 / 心里堵 / 堵心 / 心堵 / 好堵」短句共情分支，话术与 compose 对齐；补充 `_VENT` / `_user_tone` 关键词

## 2. 测试

- [x] 2.1 在 `test_mock_llm.py` 增加心好堵/堵得慌等参数化用例，断言非空串、含共情、无热线、不以「嗯」开头
- [x] 2.2 在 `test_dialogue_compose.py` 扩展既有心里堵参数化用例，覆盖「心好堵」「好心堵」「好堵」

## 3. 验证

- [x] 3.1 `cd backend && python -m pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 3.2 `python scripts/run_dialogue_quality.py --strict` 与 `pytest tests/test_dialogue_quality.py -q` 通过
- [x] 3.3 `npx openspec validate --specs` 通过
