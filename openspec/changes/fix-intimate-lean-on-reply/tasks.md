## 1. mock 场景倚靠分支

- [x] 1.1 在 `mock.py` 的 `_scene_reply` 通用负面关键词分支之前增加「靠着/想靠着/倚靠」分支，按关系阶段分层话术
- [x] 1.2 补充 `test_mock_llm.py` 覆盖亲密「想靠着你说说」回复

## 2. compose 对齐

- [x] 2.1 在 `dialogue_compose.py` 的 `compose_contextual_reply` 增加倚靠倾诉分支（根据 prior 亲密标记推断）
- [x] 2.2 补充 `test_dialogue_compose.py` 多轮 close_miss_you 风格断言

## 3. 场景期望

- [x] 3.1 加强 `scenarios.py` 中 `close_miss_you` 第二轮 `TurnSpec`（`expect_empathy=True` 或等价约束）

## 4. 验证

- [ ] 4.1 运行 `pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [ ] 4.2 运行 `scripts/run_dialogue_quality.py --strict` 与 `pytest tests/test_dialogue_quality.py -q` 全绿
- [ ] 4.3 运行 `npx openspec validate --specs` 通过
