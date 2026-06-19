## Why

Avatar 与 TTS 已根据用户本轮情感（`user_sentiment`）切换安慰/共情表现，但 `build_system_prompt` 仅依据 NPC 内在 PAD 标签注入「语气微调」。情绪衰减后，用户突然倾诉疲惫/焦虑时 NPC 内在状态可能仍为「平和」，导致真实 LLM 路径下 prompt 仍指引「自然闲聊」，与口播/表情不一致。Mock CI 全绿掩盖了这一 prompt 层缺口。

## What Changes

- 在 `backend/app/persona.py` 新增「本轮侧重」语气提示：复用 `analyze_lexicon()` 分析 `user_text`，当用户明显偏负/偏正/怀旧时，在 system prompt 中追加与 avatar/TTS 一致的共情或同频指引
- 中性或无用户文本时不追加，保持现有 prompt 不变
- 补充 `test_persona.py` 单元测试：负面用户句 + 平和 NPC 情绪时 prompt 含共情侧重

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: system prompt 须根据用户本轮情感倾向注入「本轮侧重」语气微调，与 avatar/TTS 多模态表现一致

## Impact

- `backend/app/persona.py` — 新增 `_user_turn_tone_hint()` 并注入 prompt
- `backend/tests/test_persona.py` — 新增测试
- 不影响 API 契约、安全策略（safety.py）、记忆检索、mock 模板逻辑
