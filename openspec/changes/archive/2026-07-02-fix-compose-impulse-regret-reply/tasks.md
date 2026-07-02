## 1. 实现 compose 冲动消费后悔分支

- [x] 1.1 在 `dialogue_compose.py` 的 `compose_contextual_reply` 中，于通用负面 open 兜底之前插入冲动消费/自责分支，关键词与 `mock.py` 对齐
- [x] 1.2 冲动消费后悔返回理解后悔的共情句；自责追问返回不急着贴「没用」标签的接话；禁止「突然还是一阵子」与说教式理财

## 2. 测试与验证

- [x] 2.1 在 `test_dialogue_compose.py` 增加 `impulse_regret` 两轮单测（乱花钱后悔 + 自责管不住手）
- [x] 2.2 运行 `python3 -m pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 2.3 运行 `python3 scripts/run_dialogue_quality.py --strict` 与 `python3 -m pytest tests/test_dialogue_quality.py -q`
- [x] 2.4 运行 `npx openspec validate --specs`
