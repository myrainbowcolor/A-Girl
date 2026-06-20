## Why

对话质量评测 26 场景全绿，无 open `dialogue-quality` Issue。但 `2026-06-18-improve-proactive-message-naturalness` 仅覆盖 welcome/idle/emotion 与 insight 规则模板，**事件触发**（birthday 等）开场白仍含双问号叠问，例如「今天是特别的日子吧？……有没有给自己留一点放松的时间？」，违反 proactivity spec「每轮最多一个问句」的口语化约束，像问卷而非真人微信。

## What Changes

- 优化 `backend/app/proactivity.py` 中 `_event_message` 各事件模板（重点 birthday），全句至多一个问号，去掉叠问
- 在 `test_proactivity.py` 补充事件触发文案问句数 ≤ 1 的断言
- 不改调度频率、冷却、API 契约、安全策略

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `proactivity`: 事件触发（event）主动消息亦须口语化、全句至多一个问句

## Impact

- `backend/app/proactivity.py` — `_event_message` 模板
- `backend/tests/test_proactivity.py` — 事件文案约束测试
- 不影响 orchestrator、safety、记忆、avatar、调度逻辑
