## 1. 情感词典

- [x] 1.1 在 `sentiment_lexicon.py` 新增 `is_friendly_greeting_utterance`（含负面排除与句长上限）
- [x] 1.2 在 `analyzer.py` 的 `analyze_lexicon` 中接入初次问候温和正向分支

## 2. 场景回归

- [x] 2.1 `scenarios.py` 的 `stranger_first_greet` 增加 `expect_warmth=True`
- [x] 2.2 `scenarios.py` 的 `long_session_warmup` 首轮增加 `expect_warmth=True`

## 3. 测试与验证

- [x] 3.1 `test_analyzer_insight.py` 补充初次问候正向与负面排除用例
- [x] 3.2 `test_avatar.py` 补充初次问候 sentiment 微笑用例
- [x] 3.3 运行 `pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 3.4 运行 `scripts/run_dialogue_quality.py --strict` 与 `pytest tests/test_dialogue_quality.py -q`
- [x] 3.5 运行 `npx openspec validate --specs`
