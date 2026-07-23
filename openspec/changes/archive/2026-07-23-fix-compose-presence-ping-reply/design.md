## Context

`compose_contextual_reply` 已有「在吗」字面匹配，但用户常用「你在吗」「有人吗」「在不在」「还在吗」等变体探问 NPC 是否在线。这些变体未命中任何 compose 分支，落入 `compose_open_reply` 问卷兜底，与 mock `_user_is_greeting`（`len≤8` 且含 `_GREET` 含「在吗」）行为不一致。

## Goals / Non-Goals

**Goals:**
- 短句在线探问在 compose 路径返回自然「在呢」接话
- 与现有「在吗」回复风格一致，至多一个问句，不以「嗯」开头
- 补充单测，保持 26 场景 strict 全绿

**Non-Goals:**
- 不改 mock `_scene_reply` 场景分支（mock 主路径经 `_user_is_greeting` 已覆盖）
- 不改主动消息调度、安全策略、记忆召回

## Decisions

1. **识别函数放 `sentiment_lexicon.py`**：与 `is_friendly_greeting_utterance` 同级，供 compose 与后续 persona 复用。
2. **判定规则**：整句在预定义 frozenset（`你在吗`、`有人吗`、`在不在`、`还在吗` 等），或 `len≤8` 且含「在吗」/「在不在」且非负面词；排除含「难过」「烦」等负面词的句子。
3. **回复模板**：复用现有友好问候分支的「在呢」模板池，按 `relationship_stage` 区分陌生/朋友语气；陌生关系克制，朋友可稍亲昵。

## Risks / Trade-offs

- **误判风险**：「在吗」子串可能误命中长句 → 用 `len≤8` 与 frozenset 双重约束缓解
- **与友好问候重叠**：「在吗」已在分支中 → `is_presence_ping_utterance` 包含「在吗」变体，compose 分支统一用新函数

## Migration Plan

无数据迁移。部署后即生效。

## Open Questions

（无）
