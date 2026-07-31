## 1. 实现 compose / mock 分支扩展

- [ ] 1.1 `dialogue_compose.py`：短句无语/尴尬/社死分支追加「丢脸」「丢人」「羞耻」「社恐」，按关键词分流话术（社死优先于社恐）
- [ ] 1.2 `llm/mock.py`：同分支 + `_VENT` / `_user_tone` 对齐同关键词，避免空回复

## 2. 测试与验证

- [ ] 2.1 `test_dialogue_compose.py` 补充「好丢脸」「丢脸」「好丢人」「好羞耻」「社恐了」「好社恐」探针；`test_mock_llm.py` 补充「好丢脸」对齐单测
- [ ] 2.2 运行 `pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [ ] 2.3 运行 `scripts/run_dialogue_quality.py --strict` 与 `pytest tests/test_dialogue_quality.py -q` 全绿
- [ ] 2.4 运行 `npx openspec validate --specs` 通过
