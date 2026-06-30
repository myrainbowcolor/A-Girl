## 1. Mock 场景分支

- [x] 1.1 修改 `backend/app/llm/mock.py` 陌生关系「还想继续聊」模板：去掉「嗯嗯」「欢迎随时」，改为口语化续聊句并保留温暖标记

## 2. 测试

- [x] 2.1 在 `backend/tests/test_mock.py` 补充陌生关系续聊文案断言（无嗯嗯/欢迎随时、含温暖标记）
- [x] 2.2 跑 `long_session_warmup` 场景 `run_dialogue_quality.py --scenario long_session_warmup`

## 3. 验证

- [x] 3.1 `cd backend && python3 -m pytest --ignore=tests/test_dialogue_quality.py -q`
- [x] 3.2 `python3 scripts/run_dialogue_quality.py --strict`
- [x] 3.3 `python3 -m pytest tests/test_dialogue_quality.py -q`
- [x] 3.4 `cd .. && npx openspec validate --specs`
