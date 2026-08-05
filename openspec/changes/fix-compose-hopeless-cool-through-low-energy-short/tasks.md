## 1. Compose / Mock 分支

- [x] 1.1 在 `dialogue_compose.py` 心灰/心死/麻了分支之后、短句烦躁/通用 open 兜底之前新增 ≤12 字没救了/凉透了/彻底凉了/提不起劲/提不起精神短句分支，按关键词轻分流共情话术
- [x] 1.2 在 `llm/mock.py` 同步同条件分支与话术，并补充 `_VENT` / `_user_tone` 关键词，保证与 compose 对齐

## 2. 测试

- [x] 2.1 在 `test_dialogue_compose.py` 增加没救了/凉透了/提不起劲参数化用例，并保留「心凉了」「没劲」回归
- [x] 2.2 在 `test_mock_llm.py` 增加对应 mock 对齐用例

## 3. 验证

- [ ] 3.1 `cd backend && python -m pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [ ] 3.2 `python scripts/run_dialogue_quality.py --strict` 与 `pytest tests/test_dialogue_quality.py -q` 通过
- [ ] 3.3 `npx openspec validate --specs` 通过
