## Context

`scene_first` 编排优先调用 `compose_contextual_reply`。`mock.py` 在 `_scene_reply` 使用 `is_positive_utterance` 处理开心分享（第 587 行），但 `dialogue_compose.py` 缺失对应分支，导致 compose 返回 `None` 后走 scene_engine 或问卷式 open 兜底。

## Goals / Non-Goals

**Goals:**

- `compose_contextual_reply` 对开心分享返回与 mock 一致的同频共振接话
- 回复含「开心」「替你」或「城市」类温暖标记，至多一个问句
- `friend_happy_share` 与 `close_mixed_day` 首轮在 compose 路径下行为稳定

**Non-Goals:**

- 不改 mock 已有分支
- 不混淆「不开心」否定词与开心分享（复用 `is_positive_utterance` 安全判断）
- 不改 avatar 映射或安全策略

## Decisions

1. **插入位置**：放在想念/好久未见分支之后、「哈哈」报喜分支之前，与 mock 开心分享优先级一致。
2. **判断函数**：复用 `sentiment_lexicon.is_positive_utterance`，避免「不开心」误入。
3. **关系阶段**：朋友/亲密返回更亲昵同频句式；陌生/熟悉返回温和报喜句式；城市续聊单独变体。
4. **文案来源**：复用 mock 核心句式，用 `_pick` 做确定性变体，去除动作描写括号。

## Risks / Trade-offs

- [Risk] 「想你」与开心分享冲突 → Mitigation：`is_positive_utterance` 已排除 `is_longing_utterance`
- [Risk] 宠物捣蛋「哈哈」抢先命中 → Mitigation：宠物分支已在「哈哈」分支之前；开心分享在想念之后、纯「哈哈」之前，与 mock 一致
