## Context

早安寒暄修复（`fix-morning-greeting-warm-avatar`）已在 `sentiment_lexicon.py` + `analyzer.py` 建立「整句标记 → 温和正向 sentiment → avatar 微笑」模式。`long_session_warmup` transcript 显示同类缺口：用户夸赞天气、分享电影时话术自然但 avatar 仍平静。

## Goals / Non-Goals

**Goals:**

- 复用早安寒暄模式，为轻松正向闲聊补充词典分支
- `long_session_warmup` 第 2～3 轮 avatar 微笑 + 对话质量 `expect_warmth` 约束
- 全量 pytest + dialogue quality strict 保持通过

**Non-Goals:**

- 不改 mock/compose 话术（已自然）
- 不扩展至「无聊闲聊」等中性场景（spec 要求无聊保持中性）
- 不改调度频率或 API 契约

## Decisions

1. **新增 `is_casual_positive_smalltalk(text)`**（`sentiment_lexicon.py`）
   - 标记：`天气不错`、`天气真好`、`天气好`、`挺好的电影`、`好看的电影`、`部挺好的`
   - 排除：句中含 `_NEGATIVE_BLOCK` 明显负面词时不触发
   - 返回 sentiment 0.38、label「闲聊」（与早安/想念一致）

2. **analyzer 分支顺序**：极简 masking → longing → morning greeting → **casual positive** → 常规模块匹配

3. **场景回归**：`long_session_warmup` turn 1-2 加 `expect_warmth=True`

## Risks / Trade-offs

- [误判长句含「天气不错」但情绪复杂] → 负面词排除列表覆盖「难过/烦/累/差/不想」等
- [与真开心报喜混淆] → sentiment 0.38 仅触发微笑/nod，不触发大笑 cheer（阈值 0.6）
