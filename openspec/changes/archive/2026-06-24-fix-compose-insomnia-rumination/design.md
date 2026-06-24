## Context

`orchestrator._generate_chat_reply` 在 `scene_first` 策略下优先使用 `compose_contextual_reply` 返回值。`mock.py` 已对失眠反刍（「越躺越清醒」「项目会不会黄」等）有专用分支，但 compose 仅覆盖通用短句「好烦」（`len <= 10`），导致「越躺越清醒，好烦」被误路由。本轮对齐两条路径，参照 `2026-06-23-fix-compose-pet-antics-priority` 模式。

## Goals / Non-Goals

**Goals:**

- compose 在「越躺越清醒」及失眠上下文续聊时返回反刍共情话术
- 分支顺序：失眠/反刍 > 通用短烦，与 mock.py 一致
- 单测断言 compose 输出含「清醒」或「失眠」类共情，不含「突然还是一阵子」

**Non-Goals:**

- 不改 `mock.py`（已正确）
- 不改 persona system prompt（已有 insomnia 侧重）
- 不改 evaluator 规则或新增场景

## Decisions

1. **分支位置**：在现有 `有点烦/好烦` 短句分支（约 L277）之前插入失眠反刍检测。
2. **匹配规则**：
   - `越躺越清醒` in text → 专用回复（对齐 mock）
   - `失眠`/`睡不着`/`脑子停` in text → 失眠接住
   - 项目悬停：`项目`/`会不会黄`/`创业` in text 且非报喜 → 项目焦虑接住
3. **文案池**：2 条变体，用现有 `_pick(seed)` 去重，保持口语 1～2 句、至多一问句。

## Risks / Trade-offs

- [与 mock 文案重复] → 可接受，compose 与 mock 本应对齐
- [误命中非失眠的「好烦」] → 「越躺越清醒」检测优先，其余仍走原分支
