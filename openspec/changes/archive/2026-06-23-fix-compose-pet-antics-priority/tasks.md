## 1. 实现 compose 宠物捣蛋分支

- [x] 1.1 在 `dialogue_compose.py` 的 `compose_contextual_reply` 中，于「哈哈/嘿嘿」分支之前增加宠物捣蛋续聊分支（复用 `mock._pet_name_from_context`）
- [x] 1.2 在 `test_dialogue_compose.py` 新增 `test_compose_pet_antics_followup` 单测

## 2. 验证

- [x] 2.1 `cd backend && python3 -m pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 2.2 `python3 scripts/run_dialogue_quality.py --strict` 26/26 通过
- [x] 2.3 `python3 -m pytest tests/test_dialogue_quality.py -q` 通过
- [x] 2.4 `cd .. && npx openspec validate --specs` 通过
