## 1. 实现 compose / mock 分支扩展

- [x] 1.1 `dialogue_compose.py`：比较/自我怀疑分支追加「自卑」，≤12 字短句走自卑专用话术（先于差劲/比较分流）
- [x] 1.2 `llm/mock.py`：同分支对齐「自卑」关键词与话术，避免空回复

## 2. 测试与验证

- [x] 2.1 `test_dialogue_compose.py` 补充「好自卑」「自卑」「我好自卑」「好自卑啊」探针；`test_mock_llm.py` 补充「好自卑」对齐单测
- [x] 2.2 运行 `pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 2.3 运行 `scripts/run_dialogue_quality.py --strict` 与 `pytest tests/test_dialogue_quality.py -q` 全绿
- [x] 2.4 运行 `npx openspec validate --specs` 通过
