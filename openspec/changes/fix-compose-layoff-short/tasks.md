## 1. Compose / Mock 分支

- [x] 1.1 在 `dialogue_compose.py` 通用工作话题分支之前新增 ≤12 字失业/裁员短句分支（被裁/裁员/被开除/失业/丢工作），按关键词轻分流共情话术
- [x] 1.2 在 `llm/mock.py` 同步同条件分支与话术，保证与 compose 对齐

## 2. 测试

- [x] 2.1 在 `test_dialogue_compose.py` 增加被裁/失业/丢工作/被开除参数化用例，并断言不套用工作话题误路由话术；保留工作话题回归
- [x] 2.2 在 `test_mock_llm.py` 增加对应 mock 对齐用例

## 3. 验证

- [ ] 3.1 `cd backend && python -m pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [ ] 3.2 `python scripts/run_dialogue_quality.py --strict` 与 `pytest tests/test_dialogue_quality.py -q` 通过
- [ ] 3.3 `npx openspec validate --specs` 通过
