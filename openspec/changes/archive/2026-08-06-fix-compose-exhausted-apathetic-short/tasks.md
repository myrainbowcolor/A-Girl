## 1. Compose / Mock 分支

- [x] 1.1 在 `dialogue_compose.py` 废了/完了/提不起兴趣分支之后、短句烦躁/通用 open 兜底之前新增 ≤12 字累透/累趴/不想动/懒得动/没盼头/无所谓了短句分支，按关键词轻分流共情话术；「心累透了」不得误入本分支
- [x] 1.2 在 `llm/mock.py` 同步同条件分支与话术（置于泛化「累」低落分支之前），并补充 `_VENT` / `_user_tone` 关键词，保证与 compose 对齐

## 2. 测试

- [x] 2.1 在 `test_dialogue_compose.py` 增加累透了/不想动/懒得动/没盼头/无所谓了参数化用例，并保留「心累透了」「好累啊」「提不起劲」回归
- [x] 2.2 在 `test_mock_llm.py` 增加对应 mock 对齐用例

## 3. 验证

- [x] 3.1 `cd backend && python -m pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 3.2 `python scripts/run_dialogue_quality.py --strict` 与 `pytest tests/test_dialogue_quality.py -q` 通过
- [x] 3.3 `npx openspec validate --specs` 通过
