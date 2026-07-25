## Context

`compose_contextual_reply` 在 scene_first 编排第二层覆盖大量场景分支，未命中时返回 `None` 并落入 `compose_open_reply` 问卷兜底。`mock.py` 在 `_scene_reply` 通用负面情绪分支已处理「崩溃」「烦」等关键词，但 compose 的短句低落分支（`fix-compose-loneliness-pressure-short`）仅覆盖难过/孤独/压力等，短句如「好崩溃」「难受」「好郁闷」仍会漏接；`is_minimal_fatigue_utterance` 亦未覆盖「好累好累」「累坏了」。

基线 dialogue quality 26/26 全绿，属 compose 路径探测缺口，与近期 `fix-compose-sad-short-utterance` 同类型小步补齐。

## Goals / Non-Goals

**Goals:**

- 扩展现有 ≤12 字短句低落倾诉分支，增加崩溃/难受/郁闷/烦躁/痛苦等关键词
- `is_minimal_fatigue_utterance` 追加「好累好累」「累坏了」
- 模板与 mock 通用负面分支语气一致：先接住、陪着，至多一个轻问句
- 补充单测覆盖探针句

**Non-Goals:**

- 不改动 `safety.py`、危机干预、记忆检索
- 不处理长句复杂场景（已有独立分支）
- 不调整 compose_open_reply 问卷池
- 不修改 mock（mock 已有通用处理）

## Decisions

1. **触发条件**：在现有 `len(text) <= 12` 低落分支关键词列表中追加 `崩溃/难受/郁闷/烦躁/痛苦`；疲惫变体走 `is_minimal_fatigue_utterance` 扩展。
2. **插入位置**：直接扩展现有短句低落分支关键词元组；疲惫变体追加到 `_MINIMAL_FATIGUE_UTTERANCES` 集合。
3. **模板风格**：复用现有短句低落模板「能感觉到你现在不太好受」「我就在这儿陪着你」，禁止句首「嗯」。
4. **与考试焦虑分支**：短句「焦虑」仍走考试分支（已有行为，本轮不改）。

## Risks / Trade-offs

- [「烦躁」与「好烦」短句分支重叠] 「好烦躁」已由 `好烦` 短句分支命中；纯「烦躁」走扩展后的低落分支 → 可接受
- [关键词过宽] 仅 ≤12 字触发，长句仍走既有专用分支 → 风险可控
