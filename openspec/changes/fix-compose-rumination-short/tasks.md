## 1. 实现 compose / mock 关键词扩展

- [ ] 1.1 `dialogue_compose.py`：短句低落倾诉关键词追加「内耗」「心态崩」「心态炸」「心态爆炸」「被掏空」
- [ ] 1.2 `llm/mock.py`：`_VENT` 与情绪低落相关分支对齐同关键词，避免空回复

## 2. 测试与验证

- [ ] 2.1 `test_dialogue_compose.py` 补充「内耗」「好内耗」「心态崩了」「心态炸了」「被掏空了」探针单测；`test_mock_llm.py` 补充「内耗」对齐单测
- [ ] 2.2 运行 `pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [ ] 2.3 运行 `scripts/run_dialogue_quality.py --strict` 与 `pytest tests/test_dialogue_quality.py -q` 全绿
- [ ] 2.4 运行 `npx openspec validate --specs` 通过
