## Context

`compose_contextual_reply` 在 scene_first 编排第二层覆盖大量场景分支，未命中时返回 `None` 并落入 `compose_open_reply` 问卷兜底。`mock.py` 在 `_scene_reply` 通用负面情绪分支已处理「孤独」「压力」等关键词，但 compose 的短句低落分支（`fix-compose-sad-short-utterance`）仅覆盖难过/伤心/委屈等，短句如「好孤独」「压力大」仍会漏接。

基线 dialogue quality 26/26 全绿，属 compose 路径探测缺口，与近期 `fix-compose-sad-short-utterance` 同类型小步补齐。

## Goals / Non-Goals

**Goals:**

- 扩展现有 ≤12 字短句低落倾诉分支，增加孤独/孤单/寂寞/压力关键词
- 模板与 mock 通用负面分支语气一致：先接住、陪着，至多一个轻问句
- 补充单测覆盖「好孤独」「压力大」「压力好大」

**Non-Goals:**

- 不改动 `safety.py`、危机干预、记忆检索
- 不新增 sentiment_lexicon 函数（关键词内联即可）
- 不处理「孤独+失眠」复合句（已有独立分支）
- 不调整 compose_open_reply 问卷池

## Decisions

1. **触发条件**：在现有 `len(text) <= 12` 低落分支关键词列表中追加 `孤独/孤单/寂寞/压力`；「孤独+失眠」复合句仍由既有分支优先命中。
2. **插入位置**：直接扩展现有短句低落分支关键词元组，不新增独立分支。
3. **模板风格**：复用现有短句低落模板「能感觉到你现在不太好受」「我就在这儿陪着你」，禁止句首「嗯」。
4. **不修改 mock**：mock 已有通用处理，仅补齐 compose 缺口。

## Risks / Trade-offs

- [与考试焦虑分支冲突] 「压力大」可能含考试语境 → 短句 ≤12 字时通用共情仍合理，长句走考试焦虑分支
- [与孤独+失眠复合分支冲突] 复合句含「孤独」且含「失眠/睡不着/凌晨」→ 由既有复合分支优先命中，不受影响
