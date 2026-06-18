## Context

`emotion_to_avatar`（`backend/app/avatar.py`）将 PAD 情绪映射为 Live2D/数字人驱动线索。高激活负面情绪已映射为「担心 + comfort」，用户情感负向时亦强制 comfort；但低激活负面情绪（难过）仍映射为 `animation="idle"`，与口播安慰不同步。

架构文档中 Avatar 与 TTS/情绪引擎并列，属表现层，不改编排主路径。

## Goals / Non-Goals

**Goals:**

- 低激活负面情绪使用 comfort 动画，提升陪伴场景音画一致
- 保持现有 expression/intensity 逻辑与 API 字段不变

**Non-Goals:**

- 不改 Live2D 参数预设、TTS 逻辑
- 不调整 proactive 调度或对话文案
- 不新增 API 字段

## Decisions

1. **仅改 animation 字段**：`p <= -0.3 and a < 0.45` 分支由 `idle` → `comfort`，expression 仍为「难过」。
   - 备选：改为「担心」表情 — 否决，担心更适合高激活焦虑，难过更贴低能量陪伴。
2. **不新增 user_sentiment 参数**：现有 orchestrator 已传 user_sentiment；本改动覆盖未传 sentiment 或 NPC 内在情绪驱动的边缘路径。

## Risks / Trade-offs

- [Risk] 非倾诉场景 NPC 独自低落时 comfort 动作略「主动」→ 可接受：陪伴产品语境下静止 idle 更不自然。
- [Risk] 前端动画资源未实现 comfort → 已有 worry/comfort 路径在用，无新资源依赖。

## Migration Plan

单文件一行改动，回滚即恢复 `idle`。无需数据迁移。

## Open Questions

无。
