## Context

`scene_first` 编排中 `compose_contextual_reply` 优先于场景引擎。当前对极简附和（「嗯」「哦」「好」）统一走封闭边界套话，未区分上文是无聊摸鱼闲聊还是情绪低落封闭。`bored_smalltalk` 第 2 轮因此答非所问，虽启发式评测通过，但 transcript 拟真度不足。

已有 `is_casual_social_smalltalk` 用于 avatar sentiment，可复用标记检测近期无聊语境。

## Goals / Non-Goals

**Goals:**

- 近期用户话含无聊/社交闲聊标记时，极简附和返回轻松续聊
- `dialogue_compose.py` 与 `mock.py` 行为一致
- 真正封闭/低落场景（`short_reply_user` 等）不受影响

**Non-Goals:**

- 不改 avatar 对极简「嗯」的平静表情策略（避免误微笑）
- 不改调度频率、安全策略或记忆主路径
- 不新增 dialogue_quality 场景（现有 `bored_smalltalk` 已覆盖）

## Decisions

1. **新增 `has_casual_social_context(prior_text)`**（`sentiment_lexicon.py）：检测近期用户话是否含 `CASUAL_SOCIAL_MARKERS` 且未被负面块排除。复用现有词典，避免「无聊」入负面词典的回归。

2. **分支插入位置**：在 `compose_contextual_reply` / `_scene_reply` 的通用极简分支（`嗯/哦/好`）之前插入无聊上文判断；命中则返回 1～2 句轻松续聊（如「摸鱼状态我懂～随便唠唠也行」），至多一个问句。

3. **封闭场景保护**：仅当 `has_casual_social_context(prior_users)` 为真时走新分支；无标记时保持原封闭套话。

## Risks / Trade-offs

- [误判] 用户说「好无聊，心情还是很差」后回「嗯」→ 已有 `_CASUAL_SOCIAL_NEGATIVE_BLOCK` 排除，不会走轻松分支
- [avatar 不变] 第 2 轮仍显示平静 → 有意保留，避免封闭「嗯」误微笑；本 change 只修话术

## Migration Plan

纯逻辑增量，无数据迁移。回滚即还原三处分支顺序。

## Open Questions

无。
