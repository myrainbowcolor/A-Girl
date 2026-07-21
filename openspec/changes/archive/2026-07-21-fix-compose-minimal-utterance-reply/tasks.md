## 1. 实现 compose 分支

- [x] 1.1 `dialogue_compose.py`：将 `text == "累"` 扩展为 `text in ("累", "好累")`
- [x] 1.2 `dialogue_compose.py`：为整句 `text == "早"` 命中早安寒暄分支（复用现有回复池）

## 2. 对齐 mock

- [x] 2.1 `mock.py`：单字疲惫分支增加 `text == "好累"`
- [x] 2.2 `mock.py`：早安分支增加 `text == "早"`

## 3. 测试与验证

- [x] 3.1 `test_dialogue_compose.py`：新增 `test_compose_minimal_fatigue_hao_lei`、`test_compose_minimal_morning_zao`
- [x] 3.2 `cd backend && python -m pytest --ignore=tests/test_dialogue_quality.py -q`
- [x] 3.3 `cd backend && python scripts/run_dialogue_quality.py --strict`
- [x] 3.4 `cd backend && python -m pytest tests/test_dialogue_quality.py -q`
- [x] 3.5 `cd .. && npx openspec validate --specs`
