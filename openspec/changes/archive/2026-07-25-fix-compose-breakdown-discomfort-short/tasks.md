## 1. 扩展 compose 短句低落与疲惫分支

- [x] 1.1 在 `dialogue_compose.py` 现有 ≤12 字低落倾诉分支关键词中追加崩溃/难受/郁闷/烦躁/痛苦
- [x] 1.2 在 `sentiment_lexicon.py` `_MINIMAL_FATIGUE_UTTERANCES` 追加「好累好累」「累坏了」

## 2. 测试与验证

- [x] 2.1 在 `test_dialogue_compose.py` 补充「好崩溃」「难受」「好郁闷」「好累好累」探针单测
- [ ] 2.2 运行 `pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [ ] 2.3 运行 `python3 scripts/run_dialogue_quality.py --strict` 26/26 通过
- [ ] 2.4 运行 `npx openspec validate --specs` 通过
