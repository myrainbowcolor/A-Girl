## 1. 情感词典

- [x] 1.1 在 `sentiment_lexicon.py` 新增 `is_casual_positive_smalltalk` 及标记常量
- [x] 1.2 在 `analyzer.py` 早安分支后接入闲聊正向分支（sentiment≈0.38、label「闲聊」）

## 2. 场景回归

- [x] 2.1 `scenarios.py` 为 `long_session_warmup` 第 2～3 轮加 `expect_warmth=True`

## 3. 测试与验证

- [x] 3.1 `test_analyzer_insight.py` 补充天气/电影/负面排除单测
- [ ] 3.2 `pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [ ] 3.3 `run_dialogue_quality.py --strict` 26/26 通过
- [ ] 3.4 `pytest tests/test_dialogue_quality.py -q` 通过
- [ ] 3.5 `npx openspec validate --specs` 通过
