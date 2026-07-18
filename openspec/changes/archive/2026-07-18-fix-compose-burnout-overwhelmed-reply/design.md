## Context

`orchestrator` 默认 `dialogue_strategy=scene_first`，优先 `compose_contextual_reply` 再 fallback mock/scene_engine。`mock.py` 第 700–705 行已有「撑不住/扛不住/受不了」分支，但 `dialogue_compose.py` 缺失，导致生产路径在 `close_mixed_day` 情绪转折后半段拟真度低于评测基线。

## Goals / Non-Goals

**Goals:**
- compose 路径覆盖倦怠/极限口语，与 mock 话术风格一致
- 单测锁定 compose 行为，防止回归

**Non-Goals:**
- 不改 mock 现有分支
- 不改调度频率、安全策略、记忆检索
- 不新增 dialogue_quality 场景（现有 `close_mixed_day` 已覆盖）

## Decisions

1. **分支插入位置**：放在育儿疲惫分支之后、通用负面 open 兜底之前，与 mock 优先级一致。
2. **话术来源**：复用 mock 口语风格（1～2 句、至多一个问句），用 `_pick` 变体避免复读；不含句首「嗯」。
3. **关键词**：`撑不住`、`扛不住`、`受不了`，与 mock 和 `emotion/analyzer.py` 词表对齐。

## Risks / Trade-offs

- [误判其他语境] → 关键词较具体（极限/承受类），误触概率低
- [与 open 兜底冲突] → 新分支在 `compose_open_reply` 调用链之前命中，无影响

## Migration Plan

纯逻辑增量，无 DB/API 变更；回滚即 revert `dialogue_compose.py` 新增分支。
