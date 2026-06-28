## Context

`emotion_to_avatar` 在 `user_sentiment > 0.35` 时展示微笑/nod。初次问候「你好呀」「嗨，第一次来」经 `analyze_lexicon` 判为中性（0.0），故 avatar 回落为平静。`mock.py` 已有 `_user_is_greeting` 用于话术路由，但情感分析未复用同类逻辑。

## Goals / Non-Goals

**Goals:**
- 短句初次问候返回温和正向 sentiment（约 0.38），驱动微笑 avatar
- 含明显负面情绪或倾诉内容的问候句保持现有负向/comfort 行为
- 与 `mock._user_is_greeting` 语义对齐，避免长句或带负面词的误判

**Non-Goals:**
- 不改 mock/compose 问候话术模板
- 不改 proactivity 调度或亲密度计算
- 不调整 avatar 阈值曲线本身
- 不将「嗯」等极简句误判为微笑（已有 spec 约束）

## Decisions

1. **在 `sentiment_lexicon.py` 新增 `is_friendly_greeting_utterance`**：集中定义问候标记（你好/嗨/哈喽/在吗/早上好/晚上好）与首次来访标记（第一次来），并排除负面词块；句长上限约 12 字，与 mock `_user_is_greeting`（≤8）略宽以覆盖「嗨，第一次来」。
2. **sentiment 取 0.38、label「寒暄」**：与早安/闲聊分支同级，刚好超过 avatar 微笑阈值 0.35。
3. **分支顺序**：置于 `is_morning_greeting_utterance` 之后，避免重复；早安句仍走专用分支。
4. **场景回归**：`stranger_first_greet` 与 `long_session_warmup` 首轮加 `expect_warmth=True`。

## Risks / Trade-offs

- [误判带负面倾诉为问候] → 负面词块排除（难过/烦/累/孤独等）；「你好，我好难过」不走正向分支
- [过度笑脸] → sentiment 0.38 仅触发微笑/nod，不触发大笑 cheer
- [长句误命中] → 句长上限 + 须含明确问候标记
