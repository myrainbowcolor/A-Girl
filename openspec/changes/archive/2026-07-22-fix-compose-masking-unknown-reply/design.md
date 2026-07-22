## Context

`scene_first` 编排优先调用 `compose_contextual_reply`，未命中才走 `SceneReplyEngine`（mock 场景分支）。persona spec 已要求整句极简 masking 口语（「还好」「还行」「一般」「不知道」「说不清」「说不上」）使用「极简 masking 低落」侧重；`compose_contextual_reply` 在 line 717 已有分支覆盖「说不清」「说不上来」，但遗漏整句「不知道」「说不上」。mock `_scene_reply` 在 line 745 已覆盖三者。

`short_reply_user` 场景第 3 轮用户说「不知道」，mock 路径正常，compose 路径返回 `None` 落入 open 兜底。

## Goals / Non-Goals

**Goals:**

- 扩展 `dialogue_compose.py` masking 分支，覆盖「不知道」「说不上」
- 与 mock 模板语义对齐：轻轻接住、不逼想清楚、可轻问一句
- 补充 compose 探针测试

**Non-Goals:**

- 不改 `analyzer.py`（已对「不知道」「说不上」判偏负向）
- 不改 persona prompt 侧重逻辑
- 不扩展其他未覆盖的 None 缺口（如「好困」「起不来」）

## Decisions

1. **合并到现有 masking 分支（line 717）**
   - 将 `text in (...)` 元组扩展加入「不知道」「说不上」
   - 理由：与「说不清」「说不上来」同级，避免新增分支顺序问题

2. **模板去句首「嗯」**
   - 现有「说不清」模板含「嗯，说不清也没关系」——新增变体使用无「嗯」前缀模板，与 spec 句首禁止「嗯」一致
   - 理由：masking 场景用户情绪低落，机械「嗯」易触发 `robotic_tone`

3. **保留「说不上来」与「说不上」并存**
   - 「说不上来」为口语变体，「说不上」为 mock 对齐的整句
   - 理由：最小 diff，不破坏已有「说不上来」行为

## Risks / Trade-offs

- [Risk] 长句「我不知道该怎么办」误命中 → Mitigation：仅整句精确匹配 `text in (...)`，与 analyzer 一致
- [Risk] 与「说不清」模板重复 → Mitigation：复用同一 `_pick` 池，语义一致

## Migration Plan

无数据迁移。部署后即生效。回滚：还原 `dialogue_compose.py` 一行改动即可。

## Open Questions

无。
