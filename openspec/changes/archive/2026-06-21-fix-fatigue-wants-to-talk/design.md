## Context

`mock.py` 的 `_scene_reply` 在命中「累/压力/烦」等负向词时走通用疲惫兜底：「不想说太多也没关系，我就在这儿陪着你。」该话术适用于用户封闭或不愿多说，但当用户明确表达倾诉意愿（如 `close_miss_you` 场景「今天过得好累，想靠着你说说」）时语义相反，破坏亲密陪伴拟真度。persona 的 `_user_turn_tone_hint` 尚无「疲惫 + 想聊」区分，真实 LLM 路径可能复用同样问题。

## Goals / Non-Goals

**Goals:**

- mock 在疲惫 + 倾诉意愿组合时返回接住疲惫、邀请慢慢说的口语回复
- persona prompt 为 LLM 路径注入「疲惫想聊」侧重
- 单测覆盖关键词组合；对话质量 26/26 保持全绿

**Non-Goals:**

- 不改通用封闭边界逻辑（「嗯」「不想说」仍短句陪伴）
- 不改 avatar 映射、亲密度算法、安全策略
- 不新增 dialogue quality 场景（现有 `close_miss_you` 已覆盖）

## Decisions

1. **分支位置**：在 `_scene_reply` 通用疲惫块（约 L458）之前插入「疲惫 + 想倾诉」检测，避免被宽泛 `累` 匹配吞掉。
2. **关键词集**：倾诉意愿 `靠着/跟你说/想聊聊/想说说`；疲惫 `累/好累/心累/辛苦/撑不住`。两者 AND 触发，降低误伤纯封闭句概率。
3. **关系差异化**：亲密/朋友可用「靠着我说」类亲昵表达；陌生/熟悉保持体贴但不越界。
4. **persona 侧重**：新增 `_USER_TURN_TONE["fatigue_talk"]`，在 `_ANGER_KEYWORDS` / `_INSOMNIA_KEYWORDS` 之后、通用 negative 之前检测，优先级高于纯 negative。

## Risks / Trade-offs

- [「好累但不想说」误触发倾诉分支] → 要求同时含倾诉意愿词，封闭句「不想说」仍走 closed 路径
- [关键词过宽] → 仅用常见口语组合，单测锁定 `想靠着你说说` 与反例 `好累不想说`
