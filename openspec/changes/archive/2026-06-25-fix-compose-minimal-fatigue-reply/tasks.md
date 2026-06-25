## 1. 实现 compose 单字「累」分支

- [x] 1.1 在 `dialogue_compose.py` 的 `compose_contextual_reply` 中，于「还行/还好」分支附近增加 `text == "累"` 疲惫共情分支
- [x] 1.2 补充 `test_dialogue_compose.py` 断言 compose 对「累」返回含疲惫语义、不含「不太好受」

## 2. 对齐 mock 场景分支

- [x] 2.1 在 `mock.py` 的 `_scene_reply` 通用负面关键词分支之前增加 `text == "累"` 极简疲惫分支

## 3. 验证

- [x] 3.1 运行 `pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 3.2 运行 `scripts/run_dialogue_quality.py --strict` 与 `pytest tests/test_dialogue_quality.py -q` 全绿
- [x] 3.3 运行 `npx openspec validate --specs` 通过
