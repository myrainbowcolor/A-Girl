## 1. compose 分支实现

- [x] 1.1 在 `dialogue_compose.py` 新增天气/电影闲聊分支（须在开心分享之前）
- [x] 1.2 新增感谢分支（须在 `is_positive_utterance` 之前），按关系阶段区分语气
- [x] 1.3 新增 emo/心累低落分支
- [x] 1.4 新增晚安/道别分支

## 2. 测试与验证

- [x] 2.1 在 `test_dialogue_compose.py` 补充天气、电影、感谢、晚安、心累 compose 单测
- [x] 2.2 运行 `python3 -m pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 2.3 运行 `python3 scripts/run_dialogue_quality.py --strict` 与 `pytest tests/test_dialogue_quality.py -q`
- [x] 2.4 运行 `npx openspec validate --specs`
