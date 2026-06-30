## Context

`emotion_to_avatar` 在 `user_sentiment` 未触发正负阈值时，回退到 NPC 内在 PAD 映射表情。正向闲聊（如「好无聊啊」）会抬高 pleasure，导致下一轮用户仅回「嗯」时仍显示微笑，与陪伴式话术和 spec 不一致。`reply_guard.user_is_closed` 已能区分封闭极简句与 masking 口语（「还好」）。

## Goals / Non-Goals

**Goals:**
- 封闭极简句（「嗯」「哦」等）avatar 固定为平静/idle，不受前轮 NPC 正向 PAD 影响
- 保持 masking/回避/疲惫口语的 comfort 路径不变
- 最小 diff：仅 avatar + orchestrator 传参

**Non-Goals:**
- 不改 mock 话术、persona 提示词
- 不改「好无聊啊」「你在干嘛」的微笑规则
- 不改主动消息、安全拦截

## Decisions

1. **在 `emotion_to_avatar` 增加 `user_text` 可选参数**，用 `is_neutral_minimal_avatar_utterance`（仅「嗯」「哦」等中性极简整句，**不含**「不想说」类情绪封闭句）判定；命中时在检查 NPC PAD 之前返回 `平静/idle`。
   - 备选：在 analyzer 给「嗯」负向 sentiment → 会误触发担心脸，且仍无法阻止 PAD 微笑路径。
   - 备选：降低前轮闲聊对 PAD 的影响 → 波及面过大。

2. **orchestrator 三处 chat 路径传入 `user_text`**，proactive 路径不传（无用户轮次文本）。

3. **场景约束**：为 `bored_smalltalk` 第 2 轮增加 evaluator 可检查的期望字段（若已有 `expect_neutral_avatar` 则复用；否则在 turn spec 加轻量标记或在 test_avatar 覆盖即可）。

## Risks / Trade-offs

- [误判封闭] `user_is_closed` 对极短句较宽 → 与现有 reply_guard 行为一致，已长期运行
- [过度平静] 用户开心回「好」时变平静 → 可接受，极简肯定语陪伴场景偏安静

## Migration Plan

纯逻辑补丁，无数据迁移；回滚删除 avatar 优先分支即可。

## Open Questions

（无）
