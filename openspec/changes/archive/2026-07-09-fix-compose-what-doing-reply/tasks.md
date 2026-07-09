## 1. 实现

- [x] 1.1 在 `dialogue_compose.py` 增加「你在干嘛 / 在干嘛 / 干什么」分支（与 mock 对齐，检测无聊上文）
- [x] 1.2 在 `test_dialogue_compose.py` 增加 bored_smalltalk 语境与普通探问两条单测

## 2. 验证

- [x] 2.1 `cd backend && python3 -m pytest --ignore=tests/test_dialogue_quality.py -q`
- [x] 2.2 `python3 scripts/run_dialogue_quality.py --strict`
- [x] 2.3 `python3 -m pytest tests/test_dialogue_quality.py -q`
- [x] 2.4 `cd .. && npx openspec validate --specs`
