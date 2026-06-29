## Context

情感词典 `analyze_lexicon` 已有早安寒暄（`is_morning_greeting_utterance`）、轻松正向闲聊（`is_casual_positive_smalltalk`）与无聊社交探问（`is_casual_social_smalltalk`）分支，均返回 sentiment≈0.38 驱动 avatar 微笑。`avatar.py` 在 `user_sentiment > 0.35` 时映射微笑/nod。

「你好呀」「嗨，第一次来」等初识问候话术自然，但 sentiment 为中性 0.0，avatar 停留平静 idle，与温暖接话不匹配。

## Goals / Non-Goals

**Goals:**
- 友好问候（你好/嗨/第一次来）触发温和正向 sentiment，avatar 微笑/nod
- 含明显负面标记的问候（如「你好，我今天很难过」）不走此分支
- 封闭极简句（「嗯」）仍为平静/comfort，不误触温暖分支

**Non-Goals:**
- 不改 mock 话术、compose 编排、proactivity 调度
- 不调整 avatar 阈值或 PAD 映射主逻辑
- 不扩展 evaluator 新增 expect_warm_avatar 标记（本轮靠单元测试锁定）

## Decisions

1. **新增 `is_friendly_greeting_utterance` 而非扩展 `is_morning_greeting_utterance`**
   - 理由：早安与初识问候 marker 不同，独立函数便于维护
   - 备选：合并 marker 列表 — 拒绝，早安含困倦排除逻辑不同

2. **句长 ≤12 + 负面排除**
   - 短句问候才走温暖分支，长句倾诉（含负面词）仍走 comfort
   - 负面排除复用同类词：难过、烦、累、差、不想、郁闷、低落、孤独、落寞、孤单、难受、伤心

3. **sentiment 复用 0.38 / label「寒暄」**
   - 与早安寒暄一致，`emotion_to_avatar` 无需改动

## Risks / Trade-offs

- [「你好，我今天很难过」误判为温暖] → 句中含「难过」或超句长不走问候分支
- [封闭「嗯」误触温暖] → marker 不含单字「嗯」
- [「你好吗」误判] → 句长 >12 或需 marker 精确匹配；「你好吗」含「你好」但长度 3，需确认是否应温暖 — 3 ≤12 且无负面，会触发温暖，可接受

## Migration Plan

纯规则增量，无 DB/API 变更；回滚即删除新分支与测试。
