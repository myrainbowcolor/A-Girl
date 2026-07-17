## Why

`scene_first` 编排优先调用 `compose_contextual_reply`，但 mock 已覆盖的天气/电影闲聊、感谢、晚安道别与 emo/心累低落口语在 compose 路径返回 `None` 或误命中「开心分享」分支（如「感觉你挺温柔的，谢谢」）。生产路径会落入 open 兜底或错误报喜，与 `long_session_warmup` 等场景拟真度不符。

## What Changes

- 在 `dialogue_compose.py` 的 `compose_contextual_reply` 新增与 `mock.py` 对齐的分支：天气/电影闲聊、感谢、晚安道别、emo/心累低落
- 感谢分支须在 `is_positive_utterance` 开心分享之前命中，避免「谢谢」被误判为报喜
- 补充 `test_dialogue_compose.py` 单测覆盖上述 compose 路径
- 更新 `openspec/specs/persona/spec.md` delta：明确 compose 与 mock 行为一致

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：口语化回复约束中补充天气/电影闲聊、感谢、晚安、emo/心累 compose 场景

## Impact

- `backend/app/dialogue_compose.py` — 新增 4 组场景分支
- `backend/tests/test_dialogue_compose.py` — 新增 compose 单测
- 不影响安全、危机干预、记忆主路径；不改 API 契约

## 成功标准

- `long_session_warmup` 相关 compose 路径返回自然口语接话（非 open 兜底或错误报喜）
- `python3 -m pytest` 全绿；`run_dialogue_quality.py --strict` 26/26 通过
