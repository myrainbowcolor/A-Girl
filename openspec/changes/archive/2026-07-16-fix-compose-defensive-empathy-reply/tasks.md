## 1. 实现

- [x] 1.1 在 `dialogue_compose.py` 增加防御心态（你不懂/没人懂）共情分支
- [x] 1.2 扩展封闭撤回分支覆盖「不想说/不说了/算了」，与 mock 对齐
- [x] 1.3 在 `test_dialogue_compose.py` 增加 friend_defensive 语境单测

## 2. 验证

- [x] 2.1 `cd backend && python3 -m pytest --ignore=tests/test_dialogue_quality.py -q`
- [x] 2.2 `python3 scripts/run_dialogue_quality.py --strict`
- [x] 2.3 `python3 -m pytest tests/test_dialogue_quality.py -q`
- [x] 2.4 `cd .. && npx openspec validate --specs`
