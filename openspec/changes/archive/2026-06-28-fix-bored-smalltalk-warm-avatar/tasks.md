## 1. 情感词典

- [x] 1.1 `sentiment_lexicon.py` 新增 `is_casual_social_smalltalk` 与 marker/负面排除
- [x] 1.2 `analyzer.py` 在 `is_casual_positive_smalltalk` 之后调用新分支，返回 sentiment≈0.38、label「闲聊」

## 2. 场景与测试

- [x] 2.1 `scenarios.py` 验证 `bored_smalltalk` avatar 微笑（无需 `expect_warmth`，该标记检查话术非表情）
- [x] 2.2 `test_analyzer_insight.py` 更新 bored 测试并新增社交探问用例
- [x] 2.3 `test_avatar.py` 补充 bored/探问 sentiment 驱动微笑用例（可选，复用现有 0.38 测试模式）

## 3. 验证

- [x] 3.1 `cd backend && python3 -m pytest --ignore=tests/test_dialogue_quality.py -q`
- [x] 3.2 `python3 scripts/run_dialogue_quality.py --strict`
- [x] 3.3 `python3 -m pytest tests/test_dialogue_quality.py -q`
- [x] 3.4 `cd .. && npx openspec validate --specs`
