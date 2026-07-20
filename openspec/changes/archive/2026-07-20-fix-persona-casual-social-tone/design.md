## Context

`persona.build_system_prompt` 通过 `_user_turn_tone_hint(user_text)` 注入「本轮侧重」，与 avatar/TTS 多模态共情对齐。已有想念、怀旧、愤怒、失眠、自我怀疑等独立侧重；但 `analyze_lexicon` 对早安寒暄（`is_morning_greeting_utterance`）、友好问候（`is_friendly_greeting_utterance`）、无聊/社交探问（`is_casual_social_smalltalk`）、轻松正向闲聊（`is_casual_positive_smalltalk`）返回温和正向 sentiment≈0.38，最终落入通用 `positive` 侧重。

compose/mock 规则路径已有自然话术，本变更仅修正 **LLM prompt 指引**，与 `emotion-relationship` / `voice-avatar` 已建立的寒暄正向标注一致。

## Goals / Non-Goals

**Goals:**
- 早安/友好问候/无聊闲聊/夸赞天气等句子的 prompt 侧重与场景语义一致
- 真·开心分享（如「今天特别开心哈哈」）仍走现有 `positive` 侧重

**Non-Goals:**
- 不改 `analyze_lexicon` 返回值
- 不改 compose、mock、proactivity、avatar 映射逻辑

## Decisions

1. **在 `_USER_TURN_TONE` 新增三类侧重**：
   - `morning_greeting`：朋友互道早安，自然温暖，禁止报喜/客服腔
   - `friendly_greeting`：初识问候，礼貌克制，禁止过度亲昵
   - `casual_chat`：无聊摸鱼/天气电影/探问，轻松唠嗑，禁止当成报喜

2. **判定顺序**（在 `analyze_lexicon` 正向分支之前）：
   - `is_morning_greeting_utterance` → morning_greeting
   - `is_friendly_greeting_utterance` → friendly_greeting
   - `is_casual_social_smalltalk` 或 `is_casual_positive_smalltalk` → casual_chat

3. **复用 `sentiment_lexicon` 现有函数**，与 avatar 标注同源，避免重复 marker 列表。

## Risks / Trade-offs

- [误判真开心为闲聊] → `is_casual_positive_smalltalk` 已排除强正向词；「今天特别开心哈哈」仍走词典正向匹配
- [范围过小] → 仅覆盖已标注的 4 类社交句，不扩大启发式

## Migration Plan

单文件逻辑增量，无数据迁移；失败可回滚 `persona.py` 一处改动。
