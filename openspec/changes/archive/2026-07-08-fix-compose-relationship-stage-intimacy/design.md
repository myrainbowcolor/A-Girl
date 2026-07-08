## Context

`scene_first` 策略优先调用 `compose_contextual_reply`，未命中再走 `SceneReplyEngine`/mock。compose 中多处用 `prior_assistant` 是否含「亲爱的」等推断亲密，但新会话首轮无 assistant 历史时即失效。orchestrator 在生成回复前已加载 `Relationship` 并写入 system prompt，却未传给 compose。

## Goals / Non-Goals

**Goals:**

- compose 路径根据 `relationship_stage` 与 prior_assistant 双通道判断亲密/朋友语气
- 亲密首轮「想念」与 mock `_scene_reply` 对齐
- 最小 diff，仅改 compose 签名与 orchestrator 传参

**Non-Goals:**

- 不改 mock.py、persona prompt、亲密度计算逻辑
- 不改 dialogue_quality 场景定义（行为修正后 transcript 自然改善）

## Decisions

1. **参数设计**：`compose_contextual_reply(..., relationship_stage: str | None = None)`，接受 `close`/`friend`/`stranger`/`acquainted` 或中文「亲密」「朋友」等，内部归一化。
2. **判断逻辑**：`_is_intimate_stage(stage) or prior_assistant 含亲昵标记`；朋友同理 `_is_friend_stage(stage) or is_warm_friend`。
3. **传参位置**：仅 `orchestrator._generate_chat_reply` 传入 `relationship.stage.value`；`reply_guard._compose_or_fallback` 保持默认 None（后处理兜底场景无 stage 时行为不变）。

## Risks / Trade-offs

- [Risk] stage 与 prior_assistant 不一致时以 stage 为准 → 符合关系模型，可接受
- [Risk] 仅改想念分支不够 → 同步更新倚靠、续聊、加班等共用 `is_intimate` 的分支
