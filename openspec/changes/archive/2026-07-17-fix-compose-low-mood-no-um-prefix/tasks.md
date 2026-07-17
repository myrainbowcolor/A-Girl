## 1. 模板修复

- [x] 1.1 更新 `dialogue_compose.py` emo/心累与「不开心」分支，去掉句首「嗯……」
- [x] 1.2 同步 `mock.py` 对应场景分支文案

## 2. 测试与验证

- [x] 2.1 在 `test_dialogue_compose.py` 断言 compose 与 `polish_reply` 后「心好累」回复不以「嗯」开头
- [x] 2.2 运行 `cd backend && python3 -m pytest --ignore=tests/test_dialogue_quality.py -q`
- [x] 2.3 运行 `cd backend && python3 scripts/run_dialogue_quality.py --strict` 与 `python3 -m pytest tests/test_dialogue_quality.py -q`
- [x] 2.4 运行 `npx openspec validate --specs`
