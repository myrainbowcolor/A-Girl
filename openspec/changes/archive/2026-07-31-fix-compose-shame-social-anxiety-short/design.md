## Context

既有「短句无语/尴尬/社死」分支覆盖社交尴尬感，但不含「丢脸 / 丢人 / 羞耻 / 社恐」。见 proposal.md - Why。上一轮 `fix-compose-rumination-short` 明确未扩此缺口，本轮单点补齐。

## Goals / Non-Goals

**Goals**
- ≤12 字丢脸/丢人/羞耻/社恐短句走社交尴尬共情接话，不问卷兜底
- mock 场景路径对齐，避免空回复
- 按关键词分流话术，避免「好丢脸」抽到「社恐」或「无语」话术

**Non-Goals**
- 不扩展「被裁 / 被鸽 / 自卑 / 愧疚 / 摆烂」等其他缺口
- 不改调度频率、安全策略、记忆召回、avatar 映射
- 不新建独立长叙事分支

## Decisions

1. **扩展既有无语/尴尬/社死分支**：在 `compose_contextual_reply` / mock `_scene_reply` 的 ≤12 字分支关键词追加「丢脸」「丢人」「羞耻」「社恐」；按关键词优先级分流（社恐 → 羞耻 → 丢脸/丢人 → 既有社死/尴尬/无语）。
2. **mock `_VENT` / `_user_tone` 对齐**：将同四词加入 `_VENT` 与 negative tone，使 mock 走共情而非空串。
3. **话术语气**：先接住丢脸/羞耻/社恐感受，陪伴倾听，至多一个问句；陌生关系不过度亲昵。

## Risks / Trade-offs

- [「社恐」与「社死」子串] → 分流时先判「社死」再判「社恐」，或「社死」仍用既有分支优先
- [「羞耻」误伤无关语境] → ≤12 字短句约束；口语「好羞耻/羞耻」几乎专指尴尬羞耻感

## Migration Plan

纯后端逻辑扩展，无 DB/API 变更。回滚即 revert compose/mock 改动。

## Open Questions

（无）
