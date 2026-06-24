## Context

`scene_first` 编排策略在 `orchestrator._generate_reply` 中优先调用 `compose_contextual_reply`，命中则直接返回，不再走 `SceneReplyEngine`。近期已对齐宠物捣蛋、失眠反刍等续聊分支；`stranger_late_night_lonely` 场景用户同时说「睡不着」与「孤独」时，compose 的通用失眠关键词分支（`睡不着`）优先级过高，覆盖了孤独感受。

参考 `docs/ARCHITECTURE.md` 中 scene_first 分层：compose 负责确定性上下文拼装，应与 mock 场景分支在情感优先级上保持一致。

## Goals / Non-Goals

**Goals:**

- 在 `compose_contextual_reply` 失眠通用分支之前增加「孤独 + 失眠/睡不着」复合检测
- 回复 1～2 句口语化，先接住孤独与深夜难熬，至多一个问句
- 单测锁定 `stranger_late_night_lonely` 首轮话术

**Non-Goals:**

- 不改 `mock.py` 分支顺序（compose 优先命中即可覆盖生产路径）
- 不改 orchestrator、安全策略、avatar、亲密度逻辑
- 不调整 proactive 调度或 LLM 提示词

## Decisions

1. **复合条件**：`any(孤独/孤单/寂寞/孤独感)` AND `any(失眠/睡不着/凌晨)` — 比单独失眠更具体，优先于现有 `("失眠", "睡不着", "脑子停")` 分支。
2. **话术风格**：强调「孤独」「难熬」「陪着」，避免「脑子特别吵」「是什么事在转」等纯反刍引导；陌生关系禁用亲昵称呼（宝贝、亲爱的、靠着我）。
3. **放置位置**：紧挨失眠反刍专用分支（`越躺越清醒`）之后、通用失眠关键词分支之前，与 `fix-compose-insomnia-rumination` 模式一致。

## Risks / Trade-offs

- [仅含失眠不含孤独仍走原分支] → 预期行为，不扩大范围
- [误匹配长句中的子串] → 使用明确孤独关键词集合，与 evaluator 一致

## Migration Plan

纯逻辑增量，无数据迁移；回滚即删除新分支。

## Open Questions

无。
