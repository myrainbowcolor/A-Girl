## Why

`close_miss_you` 等亲密场景在 `scene_first` 编排下，首轮用户说「好久没聊了，有点想你」时，`compose_contextual_reply` 仅凭历史 assistant 是否含「亲爱的」判断亲密，无历史则落入陌生/泛化回复（如「听到你这么说心里暖暖的～我们多聊聊吧」），与 mock 路径及 persona 规范「亲密想念应柔软亲昵」不一致，削弱情感陪伴拟真度。

## What Changes

- `compose_contextual_reply` 增加可选 `relationship_stage` 参数，由 orchestrator 传入当前关系阶段
- 想念、倚靠疲惫、续聊、加班疲惫等分支在判断亲密/朋友语气时，除 prior_assistant 标记外亦参考 `relationship_stage`（`close`/`亲密`、`friend`/`朋友`）
- 补充 compose 与集成测试，确保亲密首轮想念返回「我也想你」类亲昵接话

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: 生产路径 compose 在亲密/朋友关系阶段须与 mock 行为一致，不依赖会话历史中的亲昵前缀

## Impact

- `backend/app/dialogue_compose.py` — 关系阶段感知与分支判断
- `backend/app/orchestrator.py` — 向 compose 传递 relationship.stage
- `backend/tests/test_dialogue_compose.py` — 新增/更新 compose 断言
- 不影响 safety、记忆、avatar、proactivity 调度
