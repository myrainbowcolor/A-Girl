## Context

`compose_contextual_reply` 在 `scene_first` 编排中优先于 LLM 调用。当前问候分支仅精确匹配 `("你好", "嗨", "哈喽", "在吗")`，漏掉「你好呀」「嗨，第一次来」等常见变体。`sentiment_lexicon.is_friendly_greeting_utterance` 与 `voice-avatar` spec 已覆盖此类句子的情感/表情映射，但 compose 未返回口语接话。

## Goals / Non-Goals

**Goals**

- compose 对友好问候变体返回 1～2 句口语化接话，与 mock 初识问候风格一致
- 陌生关系语气克制、禁止过度亲昵；至多一个问句
- 回复不以「嗯」开头

**Non-Goals**

- 不改 mock 已有分支逻辑
- 不改主动消息、安全策略、记忆召回
- 不扩展问候识别到长句或含负面词的复合句（沿用 lexicon 负面排除）

## Decisions

1. **复用 `is_friendly_greeting_utterance`**：与 avatar 情感分析共用同一识别函数，避免 compose 与 analyzer 分歧。
2. **保留现有精确匹配分支**：将 `text in (...)` 条件扩展为 `is_friendly_greeting_utterance(text) or ...`，最小 diff。
3. **初识 vs 续聊**：有 prior_assistant 且含自我介绍标记时走「又见面」续聊；否则走初识自我介绍模板（与现有逻辑一致）。

## Risks / Trade-offs

- 误判风险低：`is_friendly_greeting_utterance` 有句长 ≤12 与负面词排除
- 与英文 hello/hi 分支并存，需保持互斥顺序不变

## Migration Plan

无数据迁移；部署后即生效。回滚：还原 `dialogue_compose.py` 问候条件即可。

## Open Questions

无
