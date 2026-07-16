## Why

`friend_defensive` 场景（用户说「你不懂的，没人懂」「算了，不想说了」）在 mock 路径有共情接话，但生产路径 `compose_contextual_reply` 返回 `None` 后走 scene_engine 或 open 兜底，口语共情弱于 compose 直出。本轮在无 open Issue、26/26 全绿基线上，补齐 compose 与 mock 的防御心态共情行为缺口。

## What Changes

- 在 `backend/app/dialogue_compose.py` 增加「你不懂/没人懂」防御心态共情分支
- 扩展封闭边界分支，覆盖「不想说/不说了/算了」与 mock 对齐
- 补充 `backend/tests/test_dialogue_compose.py` 单测（`friend_defensive` 语境）
- 更新 `openspec/specs/persona` delta：明确 compose 须接住防御心态与封闭撤回

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：口语化回复约束中增加 compose 对防御心态（你不懂/没人懂）与封闭撤回（不想说/不说了）的接话要求

## Impact

- `backend/app/dialogue_compose.py`（新增/扩展分支，约 20 行）
- `backend/tests/test_dialogue_compose.py`（新增 2～3 条测试）
- 不影响安全、危机干预、记忆主路径；不改 API 契约
