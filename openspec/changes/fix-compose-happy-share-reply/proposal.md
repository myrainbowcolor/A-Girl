## Why

`friend_happy_share` 与 `close_mixed_day` 场景首轮用户分享开心事（如「今天项目过了，超开心！」「终于可以去喜欢的城市了」）时，`mock.py` 会返回同频共振接话；但生产路径 `compose_contextual_reply` 未覆盖该分支，返回 `None` 后走 scene_engine 或 open 兜底，口语温暖感弱于 compose 直出。本轮在无 open Issue、26/26 全绿基线上，补齐 compose 与 mock 的开心分享行为缺口。

## What Changes

- 在 `backend/app/dialogue_compose.py` 增加 `is_positive_utterance` 开心分享分支（含城市/offer 续聊变体），与 `mock.py` 对齐
- 补充 `backend/tests/test_dialogue_compose.py` 单测（含 `friend_happy_share` 与 `close_mixed_day` 语境）
- 更新 `openspec/specs/persona` delta：明确 compose 须接住开心分享并同频共振

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：口语化回复约束中增加 compose 对开心分享/报喜的接话要求

## Impact

- `backend/app/dialogue_compose.py`（新增分支，约 15 行）
- `backend/tests/test_dialogue_compose.py`（新增 2～3 条测试）
- 不影响安全、危机干预、记忆主路径；不改 API 契约
