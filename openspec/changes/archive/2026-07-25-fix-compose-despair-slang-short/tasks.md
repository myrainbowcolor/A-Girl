## 1. 实现 compose 分支扩展

- [x] 1.1 `dialogue_compose.py` 短句低落分支追加绝望/无助/迷茫/空虚/破防/憋屈/心痛/心碎/泪目/要哭关键词
- [x] 1.2 `dialogue_compose.py` 扩展单字「烦」「烦啊」短句烦躁分支；「绷不住」并入撑不住分支

## 2. 测试与验证

- [x] 2.1 `test_dialogue_compose.py` 补充「好绝望」「迷茫」「破防」「憋屈」「烦」探针单测
- [x] 2.2 运行 `pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 2.3 运行 `scripts/run_dialogue_quality.py --strict` 26/26 全绿
- [x] 2.4 运行 `npx openspec validate --specs` 通过
