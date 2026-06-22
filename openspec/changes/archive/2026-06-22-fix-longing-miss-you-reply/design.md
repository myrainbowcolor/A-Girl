## Context

「想你」「想念」在 `POSITIVE_WORDS` 与 `analyze_lexicon._POSITIVE` 中，导致 `is_positive_utterance("好久没聊了，有点想你")` 为 true。`mock._scene_reply` 中开心分享分支（L537）排在想念分支（L556）之前，亲密想念被当作报喜处理。

## Goals / Non-Goals

**Goals:**
- 想念/好久未见类口语走专属分支与情感标注
- avatar 展现温暖微笑（nod），非大笑 cheer
- 回复柔软黏人，每轮至多一个问句

**Non-Goals:**
- 不改调度、记忆、安全、LLM provider 契约
- 不调整「开心报喜」类真正正向分享的行为

## Decisions

1. **`is_longing_utterance(text)`** 放在 `sentiment_lexicon.py`，匹配「想你」「想念」「好久不见」「好久没聊」「有点想你」等。
2. **`is_positive_utterance`** 对想念句返回 false，避免 mock 开心分支误命中。
3. **`analyze_lexicon`** 对想念句返回 sentiment≈0.38、label「想念」，使 `emotion_to_avatar` 走微笑/nod（>0.35 且 <0.6）。
4. **`mock._scene_reply`** 将想念分支移至 `is_positive_utterance` 之前；亲密话术示例：「我也想你呀～好久没聊了，过来跟我说说今天呗」。
5. **`persona._USER_TURN_TONE["longing"]`** 指引柔软黏人、表达也在乎，禁止「开心起来了」式报喜。

## Risks / Trade-offs

- 「想你」与「谢谢你一直陪着我」等真正向句需靠上下文区分 → 想念检测限定为典型依恋表述，真报喜仍走 positive 分支。
- sentiment 0.38 边界接近 0.35 阈值 → 测试锁定 avatar 为微笑/nod。

## Migration Plan

无数据迁移；部署后即生效。

## Open Questions

（无）
