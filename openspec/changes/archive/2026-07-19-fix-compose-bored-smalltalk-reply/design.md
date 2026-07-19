## Context

`scene_first` 编排优先调用 `compose_contextual_reply`。`mock.py` 对「好无聊啊」等无聊口语有专属分支，但 compose 仅覆盖「无聊上文 + 极简嗯」与「你在干嘛」探问，首轮无聊口语返回 `None` 后落入 `compose_open_reply` 问卷兜底。`bored_smalltalk` 场景 mock 路径评测全绿，生产 compose 路径拟真度不足。

## Goals / Non-Goals

**Goals:**

- compose 与 mock 在无聊闲聊首轮行为一致
- 1～2 句轻松接话，至多一个问句，不以「嗯」开头
- 朋友/亲密与陌生/熟悉语气差异化

**Non-Goals:**

- 不改无聊 sentiment/avatar 映射（已有）
- 不改调度频率或主动消息
- 不新增 dialogue_quality 场景（现有 bored_smalltalk 已覆盖 mock 路径）

## Decisions

1. **分支关键词**：复用 mock 的 `("无聊", "没事干", "好闲")`，与 `_scene_reply` 对齐。
2. **插入位置**：置于「你在干嘛」探问分支之后、通用 open 兜底之前；须在 `is_positive_utterance` / 「哈哈」报喜之前，避免误判。
3. **关系阶段**：使用已有 `_is_friend_stage` / `_is_intimate_stage` 区分亲昵与克制语气，与 mock stage 分支一致。
4. **句首嗯**：模板禁止句首「嗯」，与 persona spec 的 `robotic_tone` 规则一致。

## Risks / Trade-offs

- [误判] 「好无聊，心情还是很差」含无聊但也含负面 → 已有 `_CASUAL_SOCIAL_NEGATIVE_BLOCK` 在 sentiment 侧排除；compose 分支仅匹配无聊关键词，该句会命中更靠前的负面/低落分支，风险低
- [重复] 与「你在干嘛」摸鱼续聊语义接近 → 首轮与探问分属不同用户意图，保持独立分支
