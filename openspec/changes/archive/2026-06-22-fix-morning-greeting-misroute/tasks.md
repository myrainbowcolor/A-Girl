## 1. 实现

- [x] 1.1 在 `dialogue_compose.py` 增加早安/通勤寒暄分支，收紧工作压力短句触发条件
- [x] 1.2 补充 `test_dialogue_compose.py` 回归：「早呀，今天又要上班了」不走工作压力 vent

## 2. 验证

- [x] 2.1 `cd backend && python3 -m pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 2.2 `python3 scripts/run_dialogue_quality.py --strict` 与 `--scenario morning_checkin` 全绿
- [x] 2.3 `python3 -m pytest tests/test_dialogue_quality.py -q` 全绿
- [x] 2.4 `cd .. && npx openspec validate --specs` 通过
