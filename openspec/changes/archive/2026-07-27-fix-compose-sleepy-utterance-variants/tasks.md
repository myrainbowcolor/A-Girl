## 1. 困倦口语识别

- [x] 1.1 `sentiment_lexicon.py` 新增 `is_minimal_sleepy_utterance`，覆盖「困」「好困」「有点困」「困了」「好困啊」，排除通勤长句

## 2. compose / mock 分支

- [x] 2.1 `dialogue_compose.py` 困倦分支改用 `is_minimal_sleepy_utterance`
- [x] 2.2 `llm/mock.py` 增加困倦变体专属共情分支

## 3. 测试与验证

- [x] 3.1 `test_dialogue_compose.py` 补充「困了」「好困啊」parametrize 探针
- [x] 3.2 跑 pytest（忽略 dialogue_quality）+ dialogue quality strict + openspec validate
