## Context

`scene_first` 编排优先调用 `compose_contextual_reply`；未命中时退回 `compose_open_reply` 或 mock 场景分支。单字「累」与「早呀/早安」已有专属分支，但「好累」「早」仍落入 open 问卷兜底或 mock 通用负面「嗯……不太好受」套话。

## Goals / Non-Goals

**Goals:**

- 为「好累」「早」补齐 compose 与 mock 专属分支，与现有单字「累」、早安寒暄行为对齐
- 补充单测，确保不回归问卷式 open 兜底

**Non-Goals:**

- 不改调度频率、API 契约、安全策略
- 不扩展其他极简口语（如「困」「烦」已有短句分支）

## Decisions

1. **疲惫分支扩展**：将 `text == "累"` 改为 `text in ("累", "好累")`，复用同一回复池；放在通用负面关键词之前（已有位置不变）。
2. **早安分支扩展**：在 `_is_morning_greeting` 中增加对整句 `text == "早"` 的识别，或于 `_MORNING_GREETING_MARKERS` 旁增加单字判断；回复复用现有早安池。
3. **mock 对齐**：在单字「累」分支旁增加 `text == "好累"`；在早安分支增加 `text == "早"`，避免落入 line 558 通用负面分支。

## Risks / Trade-offs

- [误判] 「好累」出现在长句中（如「今天好累」）— 仅匹配整句 `text == "好累"`，长句仍走加班/心累等既有分支。
- [误判] 「早」出现在其他词中 — 仅整句等于「早」时命中。

## Migration Plan

无数据迁移；合并后跑全量 pytest + dialogue quality strict。

## Open Questions

无。
