## 1. 实现 compose 育儿焦虑分支

- [x] 1.1 在 `dialogue_compose.py` 的 `compose_contextual_reply` 中，于通用负面 open 兜底之前插入育儿焦虑分支，关键词与 `mock.py` 对齐
- [x] 1.2 返回理解自责与担心的陪伴接话，禁止问卷套话与句首「嗯」；续聊子分支覆盖怕耽误孩子

## 2. 测试与验证

- [x] 2.1 在 `test_dialogue_compose.py` 增加 `parent_anxiety` 两轮单测
- [ ] 2.2 运行 `python3 -m pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [ ] 2.3 运行 `python3 scripts/run_dialogue_quality.py --strict` 与 `python3 -m pytest tests/test_dialogue_quality.py -q`
- [ ] 2.4 运行 `npx openspec validate --specs`
