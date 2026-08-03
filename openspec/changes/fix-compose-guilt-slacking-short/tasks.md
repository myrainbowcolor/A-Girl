## 1. Compose / Mock 分支

- [ ] 1.1 在 `dialogue_compose.py` 冲动消费分支之后、通用 open 兜底之前新增 ≤12 字愧疚/内疚/摆烂/无消费后悔短句分支，按关键词轻分流共情话术；后悔须排除消费线索
- [ ] 1.2 在 `llm/mock.py` 同步同条件分支与话术，保证与 compose 对齐

## 2. 测试

- [ ] 2.1 在 `test_dialogue_compose.py` 增加愧疚/内疚/摆烂/好后悔参数化用例，并断言不套用冲动消费话术；保留「好后悔买了」等消费后悔回归
- [ ] 2.2 在 `test_mock_llm.py` 增加对应 mock 对齐用例

## 3. 验证

- [ ] 3.1 `cd backend && python -m pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [ ] 3.2 `python scripts/run_dialogue_quality.py --strict` 与 `pytest tests/test_dialogue_quality.py -q` 通过
- [ ] 3.3 `npx openspec validate --specs` 通过
