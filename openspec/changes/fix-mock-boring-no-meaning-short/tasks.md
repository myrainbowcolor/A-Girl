## 1. 扩展 mock 短句低落分支

- [x] 1.1 在 `mock.py` emo/低落分支对齐 compose：≤12 字命中「没劲」「没意思」「低落」时返回低落共情话术；补「心好累」与既有 emo/丧/心累兼容
- [x] 1.2 `_LOW` / `_user_tone` 补「没意思」，避免中性空串

## 2. 测试

- [x] 2.1 扩展 `test_mock_llm.py`：参数化覆盖「没意思」「没意思了」「好没意思」「真没意思」「感觉没意思」；保留「没劲」「心累」回归
- [x] 2.2 扩展 `test_dialogue_compose.py`：参数化覆盖「没意思了」「好没意思」变体回归

## 3. 验证

- [ ] 3.1 `cd backend && python3 -m pytest --ignore=tests/test_dialogue_quality.py -q`
- [ ] 3.2 `python3 scripts/run_dialogue_quality.py --strict` 与 `python3 -m pytest tests/test_dialogue_quality.py -q`
- [ ] 3.3 `npx openspec validate --specs`
