## Why

对话质量评测 26 场景全绿，无 open `dialogue-quality` Issue。但 `latest.json` transcript 显示 `bored_smalltalk` 第 2 轮用户说「嗯」时，NPC 话术为陪伴式「我在这儿呢…」，avatar 却为「微笑 nod」——因前轮正向闲聊抬高了 NPC 内在 PAD，误走笑脸分支，与 voice-avatar spec「封闭极简句不因闲聊正向规则误判为微笑」不符。同句在 `short_reply_user` 场景正确显示「平静 idle」，表现不一致、拟真度受损。

修复前 transcript 片段：
- 用户：嗯（接在「好无聊啊」之后）
- NPC：我在这儿呢。不急着说，你想开口了再说~
- avatar：微笑 / nod（应为平静或轻柔陪伴）

## What Changes

- `emotion_to_avatar` 在用户整句为封闭极简口语（「嗯」「哦」等，复用 `reply_guard.user_is_closed` 判定）时，优先返回平静/idle，不因 NPC 内在正向 PAD 展示微笑
- `orchestrator.py` 调用 `emotion_to_avatar` 时传入 `user_text`
- 补充 `test_avatar.py` 与 `bored_smalltalk` 场景第 2 轮 avatar 约束（或等价集成断言）
- 不改 sentiment 词典、mock 话术、安全策略

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `voice-avatar`: 封闭极简句（「嗯」等）在 NPC 内在情绪偏正向时仍须平静/idle，禁止微笑

## Impact

- `backend/app/avatar.py` — `emotion_to_avatar` 封闭极简优先分支
- `backend/app/orchestrator.py` — 传入 `user_text`
- `backend/tests/test_avatar.py` — 单元测试
- `backend/app/dialogue_quality/scenarios.py`（可选）— bored_smalltalk 第 2 轮期望
- 不影响 safety、危机干预、masking 口语（「还好」「不知道」）的 comfort 路径

## 成功标准

- `bored_smalltalk` 场景「嗯」轮次 avatar 为平静（非微笑）
- `python3 -m pytest` 全绿
- `run_dialogue_quality.py --strict` 26/26 通过
