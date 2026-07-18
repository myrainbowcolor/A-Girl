## 1. compose 分支实现

- [x] 1.1 在 `dialogue_compose.py` 新增「撑不住/扛不住/受不了」倦怠极限分支（须在 open 兜底之前）
- [x] 1.2 话术与 mock.py 对齐，用 `_pick` 变体，不含句首「嗯」

## 2. 测试与验证

- [x] 2.1 在 `test_dialogue_compose.py` 补充 `close_mixed_day` 第 3 轮 compose 单测
- [x] 2.2 运行 `python3 -m pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 2.3 运行 `python3 scripts/run_dialogue_quality.py --strict` 与 `pytest tests/test_dialogue_quality.py -q`
- [x] 2.4 运行 `npx openspec validate --specs`
