## 1. Avatar 映射修复

- [x] 1.1 将 `emotion_to_avatar` 低激活负面情绪分支 animation 由 `idle` 改为 `comfort`
- [x] 1.2 更新 `test_sad_low_arousal` 断言 animation 为 comfort

## 2. 验证

- [x] 2.1 运行 `cd backend && python3 -m pytest --ignore=tests/test_dialogue_quality.py -q`
- [x] 2.2 运行 `python3 scripts/run_dialogue_quality.py --strict` 与 `python3 -m pytest tests/test_dialogue_quality.py -q`
- [x] 2.3 运行 `npx openspec validate --specs`
