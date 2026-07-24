## 1. 扩展 compose 短句低落分支

- [x] 1.1 在 `dialogue_compose.py` 现有 ≤12 字低落倾诉分支关键词中追加孤独/孤单/寂寞/压力
- [x] 1.2 确认模板禁止句首「嗯」，至多一个问句

## 2. 测试与验证

- [ ] 2.1 在 `test_dialogue_compose.py` 补充「好孤独」「压力大」「压力好大」探针单测
- [ ] 2.2 运行 `pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [ ] 2.3 运行 `python3 scripts/run_dialogue_quality.py --strict` 26/26 通过
- [ ] 2.4 运行 `npx openspec validate --specs` 通过
