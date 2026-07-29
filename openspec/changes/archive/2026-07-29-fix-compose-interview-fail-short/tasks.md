## 1. 实现词典否定 + compose / mock 分支

- [x] 1.1 `sentiment_lexicon.py`：为「通过」「录取」补充 `_NEGATION_BLOCK` 否定前缀
- [x] 1.2 `dialogue_compose.py`：在考试失利分支之后、通用 open 兜底之前，新增 ≤12 字选拔/面试失利短句共情分支（面试砸/面试挂/没通过/落选/搞砸）
- [x] 1.3 `llm/mock.py`：场景分支对齐同关键词短句，先共情再至多一个轻问；确保不走报喜路径

## 2. 测试与验证

- [x] 2.1 `test_sentiment_lexicon.py` 补充「没通过」「面试通过了」等探针
- [x] 2.2 `test_dialogue_compose.py` 补充「面试砸了」「没通过」「落选了」「搞砸了」探针单测
- [x] 2.3 运行 `pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 2.4 运行 `scripts/run_dialogue_quality.py --strict` 与 `pytest tests/test_dialogue_quality.py -q` 全绿
- [x] 2.5 运行 `npx openspec validate --specs` 通过
