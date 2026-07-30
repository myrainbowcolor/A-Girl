## 1. 实现 compose / mock 短句想家分支

- [ ] 1.1 `dialogue_compose.py`：在节日孤独分支之后、通用 open 兜底之前，新增 ≤12 字想家/思乡短句共情分支（想家/想爸妈/想回家/想父母）
- [ ] 1.2 `llm/mock.py`：场景分支对齐同关键词短句，先共情再至多一个轻问；不走问卷兜底

## 2. 测试与验证

- [ ] 2.1 `test_dialogue_compose.py` 补充「想家了」「想爸妈」「想回家」「好想家」探针单测
- [ ] 2.2 运行 `pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [ ] 2.3 运行 `scripts/run_dialogue_quality.py --strict` 与 `pytest tests/test_dialogue_quality.py -q` 全绿
- [ ] 2.4 运行 `npx openspec validate --specs` 通过
