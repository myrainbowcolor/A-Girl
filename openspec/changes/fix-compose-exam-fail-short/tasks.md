## 1. 实现 compose / mock 分支

- [x] 1.1 `dialogue_compose.py`：在考试焦虑与育儿焦虑分支之后、通用 open 兜底之前，新增 ≤12 字考试失利短句共情分支（考砸/没考好/挂科；排除家长关键词）
- [x] 1.2 `llm/mock.py`：场景分支对齐同关键词短句，先共情再至多一个轻问

## 2. 测试与验证

- [x] 2.1 `test_dialogue_compose.py` 补充「考砸了」「没考好」「挂科了」探针单测
- [ ] 2.2 运行 `pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [ ] 2.3 运行 `scripts/run_dialogue_quality.py --strict` 与 `pytest tests/test_dialogue_quality.py -q` 全绿
- [ ] 2.4 运行 `npx openspec validate --specs` 通过
