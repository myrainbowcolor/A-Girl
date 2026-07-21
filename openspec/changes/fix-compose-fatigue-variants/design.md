## Context

`scene_first` 编排优先调用 `compose_contextual_reply`；未命中时退回 `compose_open_reply` 问卷兜底。单字「累」与整句「好累」已有专属分支，但「累了」「好累啊」「今天好累」「有点累」「累死了」等高频疲惫口语仍返回 `None`，落入「是突然这样，还是已经有一阵子了？」类问卷接话。

## Goals / Non-Goals

**Goals:**

- 抽取 `is_minimal_fatigue_utterance` 辅助函数，覆盖常见疲惫口语变体
- compose 与 mock 对齐，复用同一疲惫共情回复池
- 补充单测，确保不回归问卷式 open 兜底

**Non-Goals:**

- 不改调度频率、API 契约、安全策略
- 不扩展长句疲惫（如「最近好累啊」走既有负面/加班分支）
- 不处理「好孤独」等其它极简口语（留待后续 change）

## Decisions

1. **辅助函数位置**：在 `sentiment_lexicon.py` 新增 `is_minimal_fatigue_utterance`，与 `is_morning_greeting_utterance` 等并列，供 compose 与 mock 共用。
2. **匹配策略**：仅整句精确匹配固定集合 `{"累","好累","累了","好累啊","今天好累","有点累","累死了"}`，避免长句误触。
3. **回复池**：复用现有疲惫共情 `_pick` 池，不新增话术。
4. **分支顺序**：保持疲惫分支在通用负面 open 兜底之前（现有位置不变）。

## Risks / Trade-offs

- [误判] 「今天好累好烦」含「累」— 仅整句精确匹配，长句仍走加班/心累分支。
- [覆盖不足] 「最近好累啊」等带前缀长句 — 有意留待既有负面关键词分支处理。

## Migration Plan

无数据迁移；合并后跑全量 pytest + dialogue quality strict。

## Open Questions

无。
