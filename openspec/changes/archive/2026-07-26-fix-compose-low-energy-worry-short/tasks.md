## 1. 实现 compose 分支扩展

- [x] 1.1 `dialogue_compose.py` emo/低落分支扩展「没劲」「好没劲」「没意思」「低落」关键词
- [x] 1.2 `dialogue_compose.py` 新增心里堵/堵心/堵得慌短句分支（len≤10）
- [x] 1.3 `dialogue_compose.py` 新增短句慌张/担心分支（慌/害怕/担心，len≤10，排除育儿语境）

## 2. 测试与验证

- [x] 2.1 `test_dialogue_compose.py` 补充「没劲」「心里堵」「堵得慌」「慌」「好担心」探针单测
- [x] 2.2 运行 `pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 2.3 运行 `scripts/run_dialogue_quality.py --strict` 26/26 全绿
- [x] 2.4 运行 `npx openspec validate --specs` 通过
