## 1. 实现

- [x] 1.1 在 `dialogue_compose.py` 增加 `is_positive_utterance` 开心分享分支（与 mock 对齐）
- [x] 1.2 在 `test_dialogue_compose.py` 增加 friend_happy_share 与 close_mixed_day 语境单测

## 2. 验证

- [x] 2.1 `cd backend && python3 -m pytest --ignore=tests/test_dialogue_quality.py -q`
- [x] 2.2 `python3 scripts/run_dialogue_quality.py --strict`
- [x] 2.3 `python3 -m pytest tests/test_dialogue_quality.py -q`
- [x] 2.4 `cd .. && npx openspec validate --specs`
