## 1. 实现 compose / mock 关键词扩展

- [ ] 1.1 `dialogue_compose.py`：短句低落倾诉关键词追加「失望」「失落」「灰心」「心酸」
- [ ] 1.2 `llm/mock.py`：`_VENT` 与情绪低落相关分支对齐同关键词，避免空回复

## 2. 测试与验证

- [ ] 2.1 `test_dialogue_compose.py` 补充「好失望」「失落」「灰心了」「好心酸」探针单测；`test_mock_llm.py` 补充「好失望」对齐单测
- [ ] 2.2 运行 `pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [ ] 2.3 运行 `scripts/run_dialogue_quality.py --strict` 与 `pytest tests/test_dialogue_quality.py -q` 全绿
- [ ] 2.4 运行 `npx openspec validate --specs` 通过
