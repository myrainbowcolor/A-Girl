## Why

`close_mixed_day` 场景第 2 轮用户说「但回家还要哄娃，心好累」时，`mock.py` 会返回「一边上班一边顾娃，真的太耗你了」类育儿疲惫共情接话；但生产路径 `compose_contextual_reply` 未覆盖该分支，返回 `None` 后走 scene_engine 并带上「亲爱的，（轻轻叹了口气）」等动作描写前缀，口语感不如 compose 直出。本轮在无 open Issue、26/26 全绿基线上，补齐 compose 与 mock 的行为缺口。

## What Changes

- 在 `backend/app/dialogue_compose.py` 增加「哄娃/带娃/神兽/孩子闹」+ 疲惫关键词分支，返回 1～2 句育儿疲惫共情接话，与 `mock.py` 对齐
- 补充 `backend/tests/test_dialogue_compose.py` 单测（含 `close_mixed_day` 上文语境）
- 更新 `openspec/specs/persona` delta：明确 compose 须接住育儿疲惫倾诉

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：口语化回复约束中增加 compose 对育儿/哄娃疲惫倾诉的接话要求

## Impact

- `backend/app/dialogue_compose.py`（新增分支，约 12 行）
- `backend/tests/test_dialogue_compose.py`（新增 2 条测试）
- 不影响安全、危机干预、记忆主路径；不改 API 契约
