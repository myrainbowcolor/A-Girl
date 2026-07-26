## 1. 实现 compose / lexicon 扩展

- [x] 1.1 `sentiment_lexicon.py` `_MINIMAL_FATIGUE_UTTERANCES` 补充「今天好累啊」
- [x] 1.2 `dialogue_compose.py` masking 分支补充「一般般」
- [x] 1.3 `dialogue_compose.py` 新增短句困倦口语分支（困/好困/有点困，len≤6）
- [x] 1.4 `persona.py`、`emotion/analyzer.py` `_MINIMAL_MASKING` 补充「一般般」

## 2. 测试与验证

- [x] 2.1 `test_dialogue_compose.py` 补充「今天好累啊」「一般般」「好困」「有点困」「困」探针单测
- [x] 2.2 运行 `pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 2.3 运行 `scripts/run_dialogue_quality.py --strict` 26/26 全绿
- [x] 2.4 运行 `npx openspec validate --specs` 通过
