## 1. 情感词典

- [x] 1.1 在 `sentiment_lexicon.py` 新增 `is_morning_greeting_utterance`（含困倦排除）
- [x] 1.2 在 `analyzer.py` 的 `analyze_lexicon` 中接入早安寒暄温和正向分支

## 2. 场景回归

- [x] 2.1 `scenarios.py` 的 `morning_checkin` 首轮增加 `expect_warmth=True`

## 3. 测试与验证

- [x] 3.1 `test_analyzer_insight.py` 补充早安正向与困倦排除用例
- [x] 3.2 运行 `pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 3.3 运行 `scripts/run_dialogue_quality.py --strict` 与 `pytest tests/test_dialogue_quality.py -q`
- [x] 3.4 运行 `npx openspec validate --specs`
