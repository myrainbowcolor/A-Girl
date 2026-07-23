## 1. 识别与 compose 分支

- [x] 1.1 在 `sentiment_lexicon.py` 新增 `user_complains_filler_reply`
- [x] 1.2 在 `dialogue_compose.py` 封闭极简附和分支补充「嗯嗯」
- [x] 1.3 在 `mock.py`、`reply_guard.py`、`persona.py` 复用新函数

## 2. 测试与验证

- [x] 2.1 在 `test_dialogue_compose.py` 与 `test_sentiment_lexicon.py` 补充单测
- [x] 2.2 运行 `pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 2.3 运行 `run_dialogue_quality.py --strict` 与 `pytest tests/test_dialogue_quality.py -q` 全绿
- [x] 2.4 运行 `npx openspec validate --specs` 通过
