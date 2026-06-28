## Context

情感词典 `analyze_lexicon` 已有早安寒暄（`is_morning_greeting_utterance`）与轻松正向闲聊（`is_casual_positive_smalltalk`）分支，返回 sentiment≈0.38 驱动 avatar 微笑。`avatar.py` 在 `user_sentiment > 0.35` 时映射微笑/nod。

「好无聊啊」历史上刻意保持中性（`test_analyze_lexicon_bored_is_neutral`），是为避免将「无聊」放入 `_NEGATIVE` 导致担心脸。但中性 sentiment 使 avatar 停留平静 idle，与 mock 自然接话不匹配。

## Goals / Non-Goals

**Goals:**
- 无聊摸鱼、社交探问（你在干嘛）触发温和正向 sentiment，avatar 微笑/nod
- 含明显负面标记的句子（如「好无聊，不想活了」）不走此分支
- 保持封闭极简句（「嗯」）仍为平静/comfort，不误触温暖分支

**Non-Goals:**
- 不改 mock 话术、compose 编排、proactivity 调度
- 不调整 avatar 阈值或 PAD 映射主逻辑
- 不将「无聊」单字加入 `_NEGATIVE`

## Decisions

1. **新增 `is_casual_social_smalltalk` 而非扩展 `is_casual_positive_smalltalk`**
   - 理由：无聊/探问与夸赞天气语义不同，独立函数便于维护与负面排除列表
   - 备选：合并到 `CASUAL_POSITIVE_MARKERS` — 拒绝，marker 语义混杂

2. **sentiment 复用 0.38 / label「闲聊」**
   - 与早安寒暄、夸赞天气一致，`emotion_to_avatar` 无需改动
   - persona `_user_turn_tone_hint` 自动获得 positive 侧重

3. **负面排除列表**
   - 复用 `_CASUAL_POSITIVE_NEGATIVE_BLOCK` 同类词：难过、烦、累、差、不想、郁闷、低落、孤独、落寞
   - 另排除「不想活」「没意思」等低落口语

## Risks / Trade-offs

- [「好无聊，好烦」误判为温暖] → 句中含「烦」等负面标记时不走社交闲聊分支
- [封闭「嗯」误触温暖] → 社交 marker 不含单字「嗯」；整句精确匹配或完整短语匹配
- [改变 bored 测试语义] → 更新测试为「温和正向闲聊」而非「中性」，与产品目标一致

## Migration Plan

纯规则增量，无 DB/API 变更；回滚即删除新分支与场景期望。
