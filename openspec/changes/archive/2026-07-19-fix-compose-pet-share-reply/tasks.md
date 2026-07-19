## 1. 实现 compose 养宠分享分支

- [x] 1.1 在 `dialogue_compose.py` 新增养宠物首轮分享分支（对齐 mock，排除「记得」）
- [x] 1.2 分支置于宠物捣蛋续聊之前、通用 open 兜底之前

## 2. 测试与验证

- [x] 2.1 在 `test_dialogue_compose.py` 新增首轮养猫分享 compose 单测
- [x] 2.2 运行 `python3 -m pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 2.3 运行 `python3 scripts/run_dialogue_quality.py --strict` 26/26 通过
- [x] 2.4 运行 `npx openspec validate --specs` 通过
