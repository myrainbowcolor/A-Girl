## 1. Compose / Mock 分支

- [x] 1.1 在 `dialogue_compose.py` 短句慌张/担心关键词中追加「怕了」
- [x] 1.2 在 `llm/mock.py`：收紧 `_empathy_reply` 育儿分支（「害怕」须有育儿语境）；新增 ≤10 字慌张短句场景分支；`_VENT` 补充「怕了」「好怕」

## 2. 测试

- [x] 2.1 在 `test_dialogue_compose.py` 增加「怕了」「我怕了」用例，保留「慌」回归
- [x] 2.2 在 `test_mock_llm.py` 增加「好害怕」不误路由育儿、「怕了」对齐，及育儿语境回归

## 3. 验证

- [x] 3.1 `cd backend && python -m pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 3.2 `python scripts/run_dialogue_quality.py --strict` 与 `pytest tests/test_dialogue_quality.py -q` 通过
- [x] 3.3 `npx openspec validate --specs` 通过
