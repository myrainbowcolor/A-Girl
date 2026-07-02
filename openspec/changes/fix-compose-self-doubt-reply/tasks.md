## 1. 实现 compose 比较/自我怀疑分支

- [x] 1.1 在 `dialogue_compose.py` 的 `compose_contextual_reply` 中，于通用负面 open 兜底之前插入比较/自我怀疑分支，关键词与 `mock.py` 对齐
- [x] 1.2 比较心态返回承认落差的共情句；自我怀疑返回不急着贴标签的接话；禁止「别比了」「突然还是一阵子」

## 2. 测试与验证

- [x] 2.1 在 `test_dialogue_compose.py` 增加 `jealous_comparison` 两轮单测（比较心态 + 自我怀疑）
- [ ] 2.2 运行 `python3 -m pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [ ] 2.3 运行 `python3 scripts/run_dialogue_quality.py --strict` 与 `python3 -m pytest tests/test_dialogue_quality.py -q`
- [ ] 2.4 运行 `npx openspec validate --specs`
