## 1. 实现 compose / mock 分流修正

- [x] 1.1 `dialogue_compose.py`：收紧冲动消费语境判定；无消费语境的 ≤12 字「没用」短句走自我否定共情话术（勿套用管不住手/后悔话术）
- [x] 1.2 `llm/mock.py`：同条件与短句分流对齐，避免误套消费后悔话术

## 2. 测试与验证

- [x] 2.1 `test_dialogue_compose.py` 补充「好没用」「我好没用」「没用」探针与消费语境回归；`test_mock_llm.py` 补充「好没用」对齐单测
- [x] 2.2 运行 `pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 2.3 运行 `scripts/run_dialogue_quality.py --strict` 与 `pytest tests/test_dialogue_quality.py -q` 全绿
- [x] 2.4 运行 `npx openspec validate --specs` 通过
