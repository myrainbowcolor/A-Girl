## 1. Spec 与实现

- [x] 1.1 在 `dialogue_compose.py` 的 `compose_contextual_reply` 增加异地恋想念分支（挂电话空落落、异地恋好难），与 mock.py 对齐
- [x] 1.2 在 `test_dialogue_compose.py` 补充 `long_distance_miss` 两轮 compose 单测

## 2. 验证

- [x] 2.1 `python3 -m pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 2.2 `python3 scripts/run_dialogue_quality.py --strict` 26/26 通过
- [x] 2.3 `python3 -m pytest tests/test_dialogue_quality.py -q` 通过
- [x] 2.4 `npx openspec validate --specs` 通过
