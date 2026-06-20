## Why

`short_reply_user` 场景（情绪低落、用户极简回复）在 transcript 中可见：用户说「还好」「不知道」时，NPC 话术已共情（如「说不清也没关系，我陪你慢慢理」），但 avatar 仍为「平静/idle」，与 `voice-avatar` 规范「用户低落时安慰表情」不一致。根因是 `analyze_lexicon` 将整句「还好」「不知道」判为中性，`user_sentiment` 未触发 `emotion_to_avatar` 的 comfort 分支。

## What Changes

- 在 `analyzer.py` 为**整句极简口语**（「还好」「还行」「一般」「不知道」「说不清」「说不上」）增加专属情感判定，使 avatar/TTS 与用户侧共情表现一致
- 在 `scenarios.py` 的 `short_reply_user` 为第 2～4 轮补充 `expect_comfort_avatar=True`，固化回归期望
- 补充 `test_analyzer_insight.py` 单测，确保「好无聊」等闲聊句仍保持中性

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `voice-avatar`：明确整句极简低落口语也应触发安慰类 avatar
- `emotion-relationship`：词典对极简回复的情感标注规则

## Impact

- `backend/app/emotion/analyzer.py` — 极简口语情感判定
- `backend/app/dialogue_quality/scenarios.py` — 场景期望
- `backend/tests/test_analyzer_insight.py` — 单测
- 不影响 safety、危机干预、编排主路径
