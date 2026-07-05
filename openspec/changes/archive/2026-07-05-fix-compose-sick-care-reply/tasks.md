## 1. 实现 compose 生病关心分支

- [x] 1.1 在 `dialogue_compose.py` 的 `compose_contextual_reply` 中，于通用负面 open 兜底之前插入生病/身体不适分支，关键词与 `mock.py` 对齐
- [x] 1.2 返回关心与陪伴接话，禁止问卷套话；亲密语气用 prior_assistant 标记近似

## 2. 测试与验证

- [x] 2.1 在 `test_dialogue_compose.py` 增加 `acquainted_sick_care` 单测
- [x] 2.2 运行 `python3 -m pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 2.3 运行 `python3 scripts/run_dialogue_quality.py --strict` 与 `python3 -m pytest tests/test_dialogue_quality.py -q`
- [x] 2.4 运行 `npx openspec validate --specs`
