## 1. 文案优化

- [x] 1.1 更新 `proactivity.py` welcome / emotion / idle 开场白，去掉叠问
- [x] 1.2 更新 `user_insight.py` `rule_proactive_message` 各 need 模板

## 2. 测试

- [x] 2.1 在 `test_proactivity.py` 断言 welcome/idle/emotion 消息问句数 ≤ 1
- [x] 2.2 在 `test_user_insight.py` 断言 rule 模板问句数 ≤ 1
- [x] 2.3 运行 `pytest --ignore=tests/test_dialogue_quality.py -q` 全绿
- [x] 2.4 运行 `scripts/run_dialogue_quality.py --strict` 与 `pytest tests/test_dialogue_quality.py -q`
