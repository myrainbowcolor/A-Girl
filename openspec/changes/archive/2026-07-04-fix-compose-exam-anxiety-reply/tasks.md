## 1. 实现 compose 考试焦虑分支

- [x] 1.1 在 `dialogue_compose.py` 的 `compose_contextual_reply` 中，于通用负面 open 兜底之前插入考试/学业焦虑分支，关键词与 `mock.py` 对齐
- [x] 1.2 排除家长育儿语境；「记不住」续聊与首轮考前紧张分别返回共情句，禁止问卷套话

## 2. 测试与验证

- [x] 2.1 在 `test_dialogue_compose.py` 增加 `acquainted_exam_anxiety` 两轮单测
- [x] 2.2 运行 `python3 -m pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 2.3 运行 `python3 scripts/run_dialogue_quality.py --strict` 与 `python3 -m pytest tests/test_dialogue_quality.py -q`
- [x] 2.4 运行 `npx openspec validate --specs`
