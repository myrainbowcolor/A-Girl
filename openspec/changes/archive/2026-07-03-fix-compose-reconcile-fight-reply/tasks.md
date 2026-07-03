## 1. 实现 compose 吵架和好分支

- [x] 1.1 在 `dialogue_compose.py` 的 `compose_contextual_reply` 中，于通用负面 open 兜底之前插入吵架/冷战/和好分支，关键词与 `mock.py` 对齐
- [x] 1.2 吵架首轮返回接住沉默/别扭的共情句；拉不下脸追问返回理解想和好；求建议返回轻量台阶建议；禁止「突然还是一阵子」与站队评判

## 2. 测试与验证

- [x] 2.1 在 `test_dialogue_compose.py` 增加 `reconcile_after_fight` 三轮单测
- [x] 2.2 运行 `python3 -m pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 2.3 运行 `python3 scripts/run_dialogue_quality.py --strict` 与 `python3 -m pytest tests/test_dialogue_quality.py -q`
- [x] 2.4 运行 `npx openspec validate --specs`
