## 1. 实现辅助函数与 compose 分支

- [x] 1.1 `sentiment_lexicon.py`：新增 `is_minimal_fatigue_utterance`
- [x] 1.2 `dialogue_compose.py`：用 `is_minimal_fatigue_utterance` 替换 `text in ("累", "好累")`

## 2. 对齐 mock

- [x] 2.1 `mock.py`：单字疲惫分支改用 `is_minimal_fatigue_utterance`

## 3. 测试与验证

- [x] 3.1 `test_dialogue_compose.py`：新增疲惫变体单测（累了、好累啊、今天好累）
- [x] 3.2 `cd backend && python -m pytest --ignore=tests/test_dialogue_quality.py -q`
- [x] 3.3 `cd backend && python scripts/run_dialogue_quality.py --strict`
- [x] 3.4 `cd backend && python -m pytest tests/test_dialogue_quality.py -q`
- [x] 3.5 `cd .. && npx openspec validate --specs`
