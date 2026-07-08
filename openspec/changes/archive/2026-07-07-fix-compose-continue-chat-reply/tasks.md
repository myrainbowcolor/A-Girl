## 1. Compose 续聊分支

- [x] 1.1 在 `dialogue_compose.py` 的 `compose_contextual_reply` 增加「还想/明天/下次继续聊」分支（想念分支之后、哈哈报喜之前），陌生/朋友文案与 mock 对齐
- [x] 1.2 在 `test_dialogue_compose.py` 补充陌生续聊与朋友续聊 compose 路径测试

## 2. 验证

- [x] 2.1 `cd backend && python3 -m pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 2.2 `python3 scripts/run_dialogue_quality.py --strict` 26/26 通过
- [x] 2.3 `python3 -m pytest tests/test_dialogue_compose.py -q` 通过
- [x] 2.4 `cd .. && npx openspec validate --specs` 通过
