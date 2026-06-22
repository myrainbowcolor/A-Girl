## 1. 情感标注

- [x] 1.1 `sentiment_lexicon.py` 增加 `is_longing_utterance`；`is_positive_utterance` 对想念句返回 false
- [x] 1.2 `analyzer.py` 对想念句返回温和正向 sentiment（label「想念」）
- [x] 1.3 补充 `test_sentiment_lexicon.py` 想念/开心区分测试

## 2. 回复与语气

- [x] 2.1 `mock.py` 想念分支提前于开心分享，优化亲密/朋友想念话术
- [x] 2.2 `persona.py` 增加 longing 用户轮次侧重
- [x] 2.3 补充 `test_mock_llm.py`、`test_persona.py` 回归

## 3. 验证

- [x] 3.1 `pytest --ignore=tests/test_dialogue_quality.py` 全绿
- [x] 3.2 `run_dialogue_quality.py --strict` 26/26 通过
- [x] 3.3 `npx openspec validate --specs` 通过
