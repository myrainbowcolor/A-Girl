## 1. 识别与 compose 分支

- [x] 1.1 在 `sentiment_lexicon.py` 新增 `is_presence_ping_utterance`
- [x] 1.2 在 `dialogue_compose.py` 友好问候分支复用该函数，覆盖「你在吗」「有人吗」等变体

## 2. 测试与验证

- [x] 2.1 在 `test_dialogue_compose.py` 补充在线探问 compose 单测
- [x] 2.2 运行 `pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 2.3 运行 `run_dialogue_quality.py --strict` 与 `pytest tests/test_dialogue_quality.py -q` 全绿
- [x] 2.4 运行 `npx openspec validate --specs` 通过
