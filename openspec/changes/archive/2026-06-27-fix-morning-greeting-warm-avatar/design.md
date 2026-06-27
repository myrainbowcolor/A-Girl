## Context

`emotion_to_avatar` 在 `user_sentiment > 0.35` 时展示微笑/nod。早安寒暄「早呀，今天又要上班了」经 `analyze_lexicon` 判为中性（0.0），故 avatar 回落为平静。`dialogue_compose.py` 已有 `_is_morning_greeting` 用于话术路由，但情感分析未复用同类逻辑。

## Goals / Non-Goals

**Goals:**
- 无困倦标记的早安句返回温和正向 sentiment（约 0.38），驱动微笑 avatar
- 困倦早安句（「困死了，不想起床」）保持现有负向 comfort 行为
- 与 `dialogue_compose._is_morning_greeting` 语义对齐，避免「上班好累」类工作压力句误判

**Non-Goals:**
- 不改 mock/compose 早安话术模板
- 不改 proactivity 调度或亲密度计算
- 不调整 avatar 阈值曲线本身

## Decisions

1. **在 `sentiment_lexicon.py` 新增 `is_morning_greeting_utterance`**：集中定义早安标记与困倦排除词，供 analyzer 与 compose 未来复用；本轮仅 analyzer 调用。
2. **sentiment 取 0.38**：与 `is_longing_utterance`（0.38）同级，刚好超过 avatar 微笑阈值 0.35，且低于大笑阈值 0.6。
3. **困倦标记优先**：含「困」「困死」「不想起床」「起不来」时跳过早安正向分支，沿用 `_NEGATIVE` 中的「困死」等匹配。
4. **场景回归**：`morning_checkin` 首轮加 `expect_warmth=True`，锁定微笑表现。

## Risks / Trade-offs

- [误判工作压力为早安] → 困倦排除 + compose 已有 `_is_morning_greeting` 要求句首/含明确早安词，「上班好累」不含早安标记不受影响
- [过度笑脸] → sentiment 0.38 仅触发微笑/nod，不触发大笑 cheer
