## 1. Compose / Mock 分支

- [x] 1.1 在 `dialogue_compose.py`「撑不住/受不了」分支之后、通用 open 兜底之前新增 ≤12 字心凉/寒心/受够了短句分支，按关键词轻分流共情话术
- [x] 1.2 在 `llm/mock.py` 同步同条件分支与话术，保证与 compose 对齐

## 2. 测试

- [x] 2.1 在 `test_dialogue_compose.py` 增加心凉/寒心/受够了参数化用例，并保留「撑不住」回归
- [x] 2.2 在 `test_mock_llm.py` 增加对应 mock 对齐用例

## 3. 验证

- [x] 3.1 `cd backend && python -m pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 3.2 `python scripts/run_dialogue_quality.py --strict` 与 `pytest tests/test_dialogue_quality.py -q` 通过
- [x] 3.3 `npx openspec validate --specs` 通过
