## 1. Avatar 逻辑

- [x] 1.1 `emotion_to_avatar` 增加 `user_text` 参数，封闭极简句（`user_is_closed`）优先返回平静/idle
- [x] 1.2 `orchestrator.py` chat 路径传入 `user_text` 至 `emotion_to_avatar`

## 2. 测试与场景

- [x] 2.1 `test_avatar.py`：高 pleasure PAD + 用户「嗯」→ 平静 idle
- [x] 2.2 确认 `bored_smalltalk` transcript 第 2 轮 avatar 为平静（跑 strict 评测）

## 3. 验证

- [x] 3.1 `cd backend && python3 -m pytest --ignore=tests/test_dialogue_quality.py -q`
- [x] 3.2 `python3 scripts/run_dialogue_quality.py --strict`
- [x] 3.3 `python3 -m pytest tests/test_dialogue_quality.py -q`
- [x] 3.4 `cd .. && npx openspec validate --specs`
