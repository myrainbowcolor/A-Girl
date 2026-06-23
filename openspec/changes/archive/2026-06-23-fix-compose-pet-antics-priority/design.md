## Context

`docs/ARCHITECTURE.md` 规定生产对话走 `scene_first`：`orchestrator._generate_chat_reply` 先调 `compose_contextual_reply`，再 fallback 到 `SceneReplyEngine`（`mock.generate_scene_reply`）。2026-06-18 已在 `mock.py` 修复宠物捣蛋续聊，但 compose 层的通用「哈哈」分支仍优先命中，导致 `memory_pet_name` 第 2 轮 transcript 仍为泛化报喜句。

## Goals / Non-Goals

**Goals:**

- `compose_contextual_reply` 在宠物捣蛋续聊时与 `mock.py` 行为对齐
- 单测 + 对话质量 26/26 保持全绿

**Non-Goals:**

- 不改 orchestrator 调用顺序（避免影响其他 compose 分支优先级）
- 不新增 API、不改安全/记忆主路径

## Decisions

1. **在 `dialogue_compose.py` 增宠物捣蛋分支，置于「哈哈/嘿嘿」之前**
   - 理由：最小 diff，与 mock 修复策略一致；不改 orchestrator 全局优先级
   - 备选：调整 orchestrator 先 scene 后 compose — 影响面大，放弃

2. **复用 `mock._pet_name_from_context` 提取宠物名**
   - 理由：避免重复正则逻辑；mock 与 compose 保持同一提取规则
   - 备选：内联复制 — 易漂移，放弃

3. **话术与 mock 宠物捣蛋分支保持一致风格**
   - 示例：「哈哈，橘子又把杯子打翻啦？这种捣蛋精真是又气又好笑～」

## Risks / Trade-offs

- [Risk] 仅含「哈哈」无宠物语境的句子仍走原报喜分支 → 无影响，预期行为
- [Risk] compose 与 mock 话术长期漂移 → 单测各覆盖一条路径；spec 要求行为一致

## Migration Plan

直接部署；无数据迁移。回滚：删除 compose 宠物分支即可。

## Open Questions

（无）
