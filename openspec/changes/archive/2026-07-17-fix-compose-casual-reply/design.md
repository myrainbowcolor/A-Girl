## Context

`orchestrator` 默认 `dialogue_strategy=scene_first`，优先 `compose_contextual_reply` 再 fallback mock/scene_engine。mock.py 已有天气/电影、感谢、晚安、emo/心累分支，但 compose 缺失，导致生产路径拟真度低于评测基线。

## Goals / Non-Goals

**Goals:**
- compose 路径覆盖上述 4 类日常口语，与 mock 话术风格一致
- 感谢句在开心分享分支之前命中，修复误判
- 单测锁定 compose 行为

**Non-Goals:**
- 不改 mock 现有分支
- 不改调度频率、安全策略、记忆检索
- 不新增 dialogue_quality 场景（现有 `long_session_warmup` 已覆盖）

## Decisions

1. **分支插入位置**：天气/电影放在早安分支附近、开心分享之前；感谢放在 `is_positive_utterance` 之前；emo/心累放在比较心态之前；晚安放在 emo 之后。与 mock 优先级保持一致。
2. **话术来源**：复用 mock 口语风格（1～2 句、至多一个问句），用 `_pick` 变体避免复读。
3. **关系阶段**：感谢/晚安根据 `relationship_stage` 区分朋友亲密与普通语气，与 mock `_dear` 逻辑对齐。

## Risks / Trade-offs

- [误判开心分享] → 感谢分支显式前置，且 `is_positive_utterance` 仅用于真正报喜
- [与 open 兜底冲突] → 新分支在 `compose_open_reply` 调用链之前命中，无影响

## Migration Plan

纯逻辑增量，无 DB/API 变更；回滚即 revert `dialogue_compose.py` 新增分支。
