## Why

对话质量评测 26 场景全绿，无 open `dialogue-quality` Issue。但 `2026-06-30-fix-stranger-continue-chat-reply` 仅修复了 `mock.py` 陌生关系「还想继续聊」分支；生产路径 `compose_contextual_reply`（`scene_first` 编排优先调用）对「明天还想来找你聊聊」返回 `None`，会降级为问卷式 open 兜底（如「我听着。哪一块你现在最想提？」），与 mock 口语化续聊不一致。

修复前 compose 路径 transcript 片段（`long_session_warmup` 末轮）：
- 用户：明天还想来找你聊聊
- NPC（compose 未命中 → open 兜底）：我听着。哪一块你现在最想提？

## What Changes

- 在 `backend/app/dialogue_compose.py` 增加「还想/明天/下次继续聊」场景分支，与 `mock.py` 行为对齐：陌生关系口语化续聊、朋友/亲密亲昵续聊
- 补充 `backend/tests/test_dialogue_compose.py` 断言 compose 路径陌生/朋友续聊回复自然、不含客服套话
- 不改 orchestrator 调度、安全策略、API 契约、mock 已有分支

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: 生产路径 `compose_contextual_reply` 对用户表达还想/明天/下次继续聊时 MUST 返回口语化续聊接话，与 mock 场景分支行为一致

## Impact

- `backend/app/dialogue_compose.py` — 新增继续聊分支
- `backend/tests/test_dialogue_compose.py` — compose 续聊测试
- 不影响 safety、记忆、avatar、proactivity 调度
