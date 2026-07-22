## 1. Compose 短句烦躁模板

- [x] 1.1 在 `dialogue_compose.py` 短句烦躁分支替换含「突然/一阵子」的模板为口语化共情接话
- [x] 1.2 在 `mock.py` `_empathy_reply` 陌生「烦」分支去掉问卷套话，与 compose 对齐

## 2. 测试与验证

- [x] 2.1 加强 `test_dialogue_compose.py` 短句烦躁探针：断言不含「突然」「一阵子」
- [x] 2.2 运行 `pytest`（忽略 dialogue_quality）+ `run_dialogue_quality.py --strict` + `test_dialogue_quality.py` 全绿
- [x] 2.3 运行 `npx openspec validate --specs` 通过
