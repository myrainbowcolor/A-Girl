## Why

`scene_first` 编排优先调用 `compose_contextual_reply`，但 mock 已覆盖的「快撑不住了」类倦怠口语（含「撑不住」「扛不住」「受不了」）在 compose 路径返回 `None`。生产路径会落入 open 兜底（如「嗯，我在呢。你先随便丢几个词给我也行~」），对 `close_mixed_day` 场景第 3 轮「有时候觉得自己快撑不住了」共情不足，且句首「嗯」有机械腔风险。

## What Changes

- 在 `dialogue_compose.py` 的 `compose_contextual_reply` 新增与 `mock.py` 对齐的倦怠/极限口语分支
- 分支置于通用负面 open 兜底之前，先接住「快到极限」感受、表达陪伴，至多一个轻问句
- 补充 `test_dialogue_compose.py` 单测覆盖 `close_mixed_day` 第 3 轮 compose 路径
- 更新 `openspec/specs/persona/spec.md` delta：明确 compose 与 mock 行为一致

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：口语化回复约束中补充倦怠/极限口语 compose 场景

## Impact

- `backend/app/dialogue_compose.py` — 新增 1 组场景分支
- `backend/tests/test_dialogue_compose.py` — 新增 compose 单测
- 不影响安全、危机干预、记忆主路径；不改 API 契约

## 成功标准

- `compose_contextual_reply("有时候觉得自己快撑不住了", …)` 返回含「极限」「陪」类共情表述，非 open 兜底
- `python3 -m pytest` 全绿；`run_dialogue_quality.py --strict` 26/26 通过
