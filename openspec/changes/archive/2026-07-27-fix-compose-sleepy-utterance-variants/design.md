## Context

`compose_contextual_reply` 是 scene_first 编排的第二层无 LLM 接话路径。上一轮 `fix-compose-fatigue-mask-sleepy-short` 已补齐「困/好困/有点困」短句分支，但探测仍发现常见口语变体「困了」「好困啊」未命中，落入问卷式 open 兜底。

## Goals / Non-Goals

**Goals**
- 新增 `is_minimal_sleepy_utterance` 统一困倦口语识别，覆盖「困了」「好困啊」等变体
- compose 与 mock 困倦分支对齐，scene_first 编排下返回体贴接话

**Non-Goals**
- 不改「困死了」通勤语境（仍走 `_is_morning_greeting`）
- 不改调度频率、安全策略、记忆召回

## Decisions

1. **困倦识别**：在 `sentiment_lexicon.py` 新增 `is_minimal_sleepy_utterance`，frozenset 包含既有短句 + 「困了」「好困啊」；排除含「困死」「不想起床」等通勤长句。
2. **compose 分支**：将 `text in ("困", ...)` 替换为 `is_minimal_sleepy_utterance(text)`，复用既有体贴接话模板。
3. **mock 对齐**：在 `is_minimal_fatigue_utterance` 分支附近增加 `is_minimal_sleepy_utterance` 分支，返回困倦共情短句。

## Risks / Trade-offs

- [「困了」与「累了」歧义] → 困倦集合与疲惫集合互斥，「累了」走 fatigue 分支
- [过度扩展集合] → 只加已探测变体「困了」「好困啊」
