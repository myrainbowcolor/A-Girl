## Why

对话质量评测 26 场景全绿，但 `emotion_to_avatar` 在 NPC 内在情绪偏负（愉悦度 ≤ -0.3）且激活度较低时，会映射为「难过 + idle」肢体动作。用户倾诉时 NPC 口播已在安慰，表情却是静止 idle，音画情感不一致，削弱陪伴感。voice-avatar spec 要求用户低落时倾向 comfort 类动作。

## What Changes

- 调整 `backend/app/avatar.py`：低激活负面情绪（难过）时 animation 由 `idle` 改为 `comfort`，与「担心」分支一致展现安抚姿态
- 补充 `test_avatar.py` 断言难过场景使用 comfort 动画
- 不改 API 契约、调度频率、安全策略

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `voice-avatar`: 明确低激活负面情绪（难过）也应使用 comfort 安抚动作，而非静止 idle

## Impact

- `backend/app/avatar.py` — PAD→AvatarCue 映射
- `backend/tests/test_avatar.py` — 单元测试
- 不影响 orchestrator 主路径、safety、记忆检索
