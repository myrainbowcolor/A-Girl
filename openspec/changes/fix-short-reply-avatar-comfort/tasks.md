## 1. 情感词典

- [ ] 1.1 在 `analyzer.py` 增加整句极简口语前置匹配（还好/还行/一般 → -0.35；不知道/说不清/说不上 → -0.45）
- [ ] 1.2 在 `test_analyzer_insight.py` 补充极简口语与长句不误判单测

## 2. 场景期望

- [ ] 2.1 `short_reply_user` 第 2～4 轮 TurnSpec 增加 `expect_comfort_avatar=True`

## 3. 验证

- [ ] 3.1 `cd backend && python3 -m pytest --ignore=tests/test_dialogue_quality.py -q`
- [ ] 3.2 `python3 scripts/run_dialogue_quality.py --strict --scenario short_reply_user`
- [ ] 3.3 `python3 -m pytest tests/test_dialogue_quality.py -q`
- [ ] 3.4 `cd .. && npx openspec validate --specs`
