## Why

对话质量评测 26 场景全绿，无 open `dialogue-quality` Issue。但 `latest.json` transcript 显示 `long_session_warmup` 末轮用户说「明天还想来找你聊聊」时，陌生关系 mock 回复为「嗯嗯，欢迎随时来找我聊，能陪着你我也挺高兴的。」——以「嗯嗯」开头违反 persona 禁止语气词敷衍规则，「欢迎随时来找我聊」偏客服腔，拟真度不足。

修复前 transcript 片段：
- 用户：明天还想来找你聊聊
- NPC：（语气轻快起来）嗯嗯，欢迎随时来找我聊，能陪着你我也挺高兴的。

## What Changes

- 优化 `backend/app/llm/mock.py` 陌生关系「还想继续聊」场景分支：去掉「嗯嗯」开头与「欢迎随时」客服套话，改为口语化微信续聊接话，保留同频温暖标记
- 补充 `backend/tests/test_mock.py`（或现有 mock 场景测试）断言陌生关系续聊回复不含「嗯嗯」/「欢迎随时」
- 不改 orchestrator、安全策略、API 契约、调度频率

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: 陌生关系用户表达「还想/明天/下次」继续聊时，mock 场景分支 MUST 返回口语化续聊接话，禁止以「嗯嗯」开头，禁止「欢迎随时来找我聊」类客服套话，须含同频温暖表达

## Impact

- `backend/app/llm/mock.py` — `_scene_reply` 陌生关系续聊分支
- `backend/tests/test_mock.py` — 文案约束测试
- 不影响 `dialogue_compose.py`、安全策略、avatar、记忆检索
