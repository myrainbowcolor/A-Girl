## Why

`bored_smalltalk` 场景第 3 轮用户问「你在干嘛」时，`mock.py` 会返回「刚泡了杯热茶，窝在沙发里发呆呢～」类口语接话；但生产路径 `compose_contextual_reply` 未覆盖该分支，返回 `None` 后落入 `compose_open_reply` 问卷式兜底（如「好，我收到了。不用一次说完~」），既不回应提问也破坏无聊闲聊的人味。本轮在无 open Issue、26/26 全绿基线上，补齐 compose 与 mock 的行为缺口。

## What Changes

- 在 `backend/app/dialogue_compose.py` 增加「你在干嘛 / 在干嘛 / 干什么」分支，根据近期用户话是否含「无聊」选择摸鱼/忙不忙续聊，与 `mock.py` 对齐
- 补充 `backend/tests/test_dialogue_compose.py` 单测（含 bored_smalltalk 上文语境）
- 更新 `openspec/specs/persona` delta：明确 compose 须正面回应社交探问

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：口语化回复约束中增加 compose 对「你在干嘛」类社交探问的接话要求

## Impact

- `backend/app/dialogue_compose.py`（新增分支，约 15 行）
- `backend/tests/test_dialogue_compose.py`（新增 2 条测试）
- 不影响安全、危机干预、记忆主路径；不改 API 契约
