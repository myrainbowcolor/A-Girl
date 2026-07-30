## Context

既有「短句低落倾诉」分支覆盖难过/委屈/崩溃/绝望等关键词，但不含「失望 / 失落 / 灰心 / 心酸」。见 proposal.md - Why。

## Goals / Non-Goals

**Goals**
- 短句失望/失落/灰心/心酸走既有短句低落共情接话，不问卷兜底
- mock `_VENT` / 情绪低落路径对齐，避免空回复
- 最小 diff：扩展关键词，不新建独立话术池（与绝望/破防扩展同一模式）

**Non-Goals**
- 不单独新建「失望」专用长叙事分支
- 不扩展「纠结 / 被忽视 / 被鸽」等其他缺口
- 不改调度频率、安全策略、记忆召回、avatar 映射

## Decisions

1. **并入短句低落关键词表**：在 `compose_contextual_reply` 的 ≤12 字低落分支追加「失望」「失落」「灰心」「心酸」；复用既有共情话术池。
2. **mock 对齐**：将同四词加入 `_VENT`，并纳入 `_scene_reply` 情绪低落关键词（及 `_user_tone` negative 若需要），使 mock 走共情而非空串。
3. **不拆独立分支**：与「绝望/破防」扩展一致，降低话术漂移与抢占风险。

## Risks / Trade-offs

- [「失望」误伤含「不失望」的否定句] → ≤12 字短句极少出现「不失望」；若出现可后续加否定前缀
- [陌生关系过度亲昵] → 复用既有克制陪伴话术，不强制 intimate 前缀

## Migration Plan

纯后端逻辑扩展，无 DB/API 变更。回滚即 revert compose/mock 改动。

## Open Questions

（无）
