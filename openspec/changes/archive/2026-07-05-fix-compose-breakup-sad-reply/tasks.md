## 1. 实现 compose 失恋分支

- [x] 1.1 在 `dialogue_compose.py` 的 `compose_contextual_reply` 中，于通用负面 open 兜底之前插入失恋/分手分支，关键词与 `mock.py` 对齐
- [x] 1.2 分手首轮、分手语境忍不住哭、怀疑自己能否好起来分别返回共情句，禁止问卷套话

## 2. 测试与验证

- [x] 2.1 在 `test_dialogue_compose.py` 增加 `friend_breakup_sad` 三轮单测
- [x] 2.2 运行 `python3 -m pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 2.3 运行 `python3 scripts/run_dialogue_quality.py --strict` 与 `python3 -m pytest tests/test_dialogue_quality.py -q`
- [x] 2.4 运行 `npx openspec validate --specs`
