## Why

对话质量评测 26 场景全绿，但主动消息（welcome / idle / emotion / insight 规则模板）仍存在「连环追问」痕迹，例如 idle 文案「最近过得怎么样？随便说点小事也行」在同一句里叠加两个引导，像问卷而非真人微信开场。persona spec 要求每轮最多一个问句，主动触达也应保持同样口语节奏，提升陪伴拟真度。

## What Changes

- 优化 `backend/app/proactivity.py` 中 welcome、emotion、idle 三类固定开场白：更口语、每句最多一个问句，去掉「随便说点小事也行」类叠问
- 优化 `backend/app/user_insight.py` 中 `rule_proactive_message` 的 follow_up / comfort / reconnect 模板，减少客服腔与问卷感
- 补充 `test_proactivity.py` / `test_user_insight.py` 断言：主动文案含问句时不超过 1 个问号
- 不改调度频率、冷却、API 契约、安全策略

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `proactivity`: 主动消息文案须口语化、每轮最多一个问句，禁止问卷式连环引导

## Impact

- `backend/app/proactivity.py` — 固定触发开场白
- `backend/app/user_insight.py` — 洞察驱动规则模板
- `backend/tests/test_proactivity.py`、`backend/tests/test_user_insight.py` — 文案约束测试
- 不影响 orchestrator、safety、记忆、avatar、调度逻辑
