## 1. 扩展 compose / mock 短句分支

- [x] 1.1 在 `dialogue_compose.py`「不想干/整个人空了」分支增加 ≤12 字「感觉空了」「掏空了」命中，复用发空共情话术（不用裸「空了」）
- [x] 1.2 在 `mock.py` 同步同条件分支；`_VENT` / `_user_tone` 补「感觉空了」「掏空了」

## 2. 测试

- [x] 2.1 扩展 `test_dialogue_compose.py`：参数化覆盖「感觉空了」「掏空了」「感觉掏空了」；保留「空了」「空落落的」「整个人空了」回归
- [x] 2.2 扩展 `test_mock_llm.py`：同上 mock 对齐断言

## 3. 验证

- [ ] 3.1 `cd backend && python3 -m pytest --ignore=tests/test_dialogue_quality.py -q`
- [ ] 3.2 `python3 scripts/run_dialogue_quality.py --strict` 与 `python3 -m pytest tests/test_dialogue_quality.py -q`
- [ ] 3.3 `npx openspec validate --specs`
