## Context

`compose_contextual_reply` 是 scene_first 编排的第二层无 LLM 接话路径。近期已补齐没劲/堵心/慌张等短句分支，但探测仍发现 4 类漏网：疲惫变体「今天好累啊」、masking 变体「一般般」、困倦短句「困/好困/有点困」。这些输入落入 `compose_open_reply` 问卷兜底，拟真度下降。

## Goals / Non-Goals

**Goals**
- 扩展 `is_minimal_fatigue_utterance` 与 compose masking/困倦分支，与 mock 疲惫共情、masking 陪伴行为对齐
- persona/emotion analyzer masking 集合补充「一般般」，保证 prompt 侧重与 avatar comfort 一致

**Non-Goals**
- 不改 mock.py 通用负面分支（mock 对「困」等短句亦走 empathy 兜底，非本轮范围）
- 不改调度频率、安全策略、记忆召回

## Decisions

1. **疲惫变体**：在 `_MINIMAL_FATIGUE_UTTERANCES` 增加「今天好累啊」，复用既有疲惫 compose 分支，最小 diff。
2. **masking 变体**：在 compose `还行/一般` 分支与 `_MINIMAL_MASKING` 同步增加「一般般」。
3. **困倦短句**：新增独立分支，匹配整句 `困`/`好困`/`有点困`（len≤6），排除含「困死」「不想起床」等通勤长句（已由 `_is_morning_greeting` 覆盖）。放在 masking 分支之后、通用 open 兜底之前。

## Risks / Trade-offs

- [「困」与早安通勤歧义] → 仅精确匹配短句，长句仍走 morning greeting 分支
- [过度扩展 fatigue 集合] → 只加已探测到的「今天好累啊」，不泛化其他未验证变体

## Migration Plan

纯后端逻辑扩展，无 DB/API 变更。回滚即 revert compose/sentiment_lexicon 改动。

## Open Questions

（无）
