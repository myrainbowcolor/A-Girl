## Context

`scene_first` 编排优先调用 `compose_contextual_reply`（见 `docs/ARCHITECTURE.md`），未命中才走 `scene_engine` / `compose_open_reply` / LLM。`mock.py` 在 `_scene_reply` 第 264 行已处理「你在干嘛」类社交探问，但 `dialogue_compose.py` 缺失对应分支，导致 compose 返回 `None` 后可能落入 `compose_open_reply` 的「好，我收到了」类封闭兜底，违反 `ignores_user_question` 规则意图。

## Goals / Non-Goals

**Goals:**

- `compose_contextual_reply` 对「你在干嘛 / 在干嘛 / 干什么」返回与 mock 一致的口语接话
- 根据 `prior_users` 是否含「无聊」切换「也在摸鱼吗」/「这会儿忙不忙」续问
- 回复不以「嗯」开头，至多一个问句

**Non-Goals:**

- 不改 mock 已有分支
- 不改调度频率、avatar 映射或安全策略
- 不新增 dialogue_quality 场景（现有 `bored_smalltalk` 已覆盖）

## Decisions

1. **插入位置**：放在 `随便聊聊` 分支之后、情感重分支之前，与 mock 社交闲聊优先级一致。
2. **文案来源**：复用 mock 核心句式（泡茶发呆 + 反问），用 `_pick` 做确定性变体。
3. **无聊语境检测**：用已有 `_user_history(history)` 拼接串检查「无聊」，与 mock 的 `prior` 逻辑等价。

## Risks / Trade-offs

- [Risk] 真实 LLM 路径若 scene_engine 先命中可能与 compose 重复 → Mitigation：compose 在 orchestrator 中优先返回，行为更一致
- [Risk] 「干什么」可能误匹配非探问语境 → Mitigation：与 mock 共用同一关键词集，已有线上验证
