## 1. 实现 compose 孤独失眠分支

- [x] 1.1 在 `dialogue_compose.py` 的 `compose_contextual_reply` 中，于通用失眠关键词分支之前增加「孤独 + 失眠/睡不着」复合分支
- [x] 1.2 话术 1～2 句口语化，含孤独/难熬共情，陌生关系禁用亲昵称呼，至多一个问句

## 2. 测试与验证

- [x] 2.1 在 `test_dialogue_compose.py` 新增 `test_compose_lonely_insomnia`：断言含孤独相关词，不含「脑子特别吵」「是什么事在转」
- [x] 2.2 运行 `python3 -m pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 2.3 运行 `python3 scripts/run_dialogue_quality.py --strict` 与 `python3 -m pytest tests/test_dialogue_quality.py -q`
- [x] 2.4 运行 `npx openspec validate --specs` 通过
