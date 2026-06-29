## 1. 情感词典

- [x] 1.1 `sentiment_lexicon.py` 新增 `is_friendly_greeting_utterance` 与 marker/句长/负面排除
- [x] 1.2 `analyzer.py` 在 `is_morning_greeting_utterance` 之后调用新分支，返回 sentiment≈0.38、label「寒暄」

## 2. 测试

- [x] 2.1 `test_analyzer_insight.py` 新增友好问候用例（含负面排除与「嗯」不误判）
- [x] 2.2 `test_avatar.py` 补充友好问候 sentiment 驱动微笑用例

## 3. 验证

- [x] 3.1 `cd backend && python3 -m pytest --ignore=tests/test_dialogue_quality.py -q`
- [x] 3.2 `python3 scripts/run_dialogue_quality.py --strict`
- [x] 3.3 `python3 -m pytest tests/test_dialogue_quality.py -q`
- [x] 3.4 `cd .. && npx openspec validate --specs`
