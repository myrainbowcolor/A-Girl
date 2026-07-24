## 1. 实现 compose 短句低落分支

- [x] 1.1 在 `dialogue_compose.py` 好烦短句分支之后新增 ≤12 字低落倾诉分支（难过/伤心/委屈/想哭/心情不好/不好受）
- [x] 1.2 模板对齐 mock 通用负面语气，禁止句首「嗯」，至多一个问句

## 2. 测试与验证

- [x] 2.1 在 `test_dialogue_compose.py` 补充「有点难过」「心情不好」「好委屈」探针单测
- [x] 2.2 运行 `pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 2.3 运行 `python3 scripts/run_dialogue_quality.py --strict` 26/26 通过
- [x] 2.4 运行 `npx openspec validate --specs` 通过
