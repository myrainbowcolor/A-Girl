## 1. 文案优化

- [x] 1.1 更新 `proactivity.py` `_event_message` birthday 模板，全句至多一个问号
- [x] 1.2 复核 interview / exam / other 模板，确认已符合单问句约束

## 2. 测试

- [x] 2.1 在 `test_proactivity.py` 为各 event kind 断言问句数 ≤ 1
- [x] 2.2 运行 `pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 2.3 运行 `scripts/run_dialogue_quality.py --strict` 与 `pytest tests/test_dialogue_quality.py -q`
