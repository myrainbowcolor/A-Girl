## Context

`scene_first` 编排优先调用 `compose_contextual_reply`（见 `docs/ARCHITECTURE.md`），未命中才走 `scene_engine`。`mock.py` 在 `_scene_reply` 第 254 行已处理「哄娃/带娃/神兽」+ 疲惫关键词，但 `dialogue_compose.py` 缺失对应分支，导致 compose 返回 `None` 后走 scene_engine 并附带「亲爱的，（轻轻叹了口气）」等动作描写前缀，口语感弱于 compose 直出路径。

## Goals / Non-Goals

**Goals:**

- `compose_contextual_reply` 对育儿/哄娃疲惫倾诉返回与 mock 一致的共情接话
- 回复含「顾娃」「哄娃」或「带娃」类表述，至多一个问句，不以「嗯」开头
- `close_mixed_day` 场景第 2 轮在 compose 路径下行为稳定

**Non-Goals:**

- 不改 mock 已有分支
- 不混淆家长育儿焦虑（孩子考不好）与本人带娃疲惫两条线
- 不改 avatar 映射或安全策略

## Decisions

1. **插入位置**：放在加班疲惫分支之前、怀旧分支之后，与 mock 育儿疲惫优先级一致；须在通用负面 open 兜底之前命中。
2. **关键词集**：复用 mock 的 `("哄娃", "带娃", "神兽", "孩子闹")` + `("累", "辛苦", "撑", "心累", "好累")` 组合判断。
3. **文案来源**：复用 mock 核心句式，用 `_pick` 做确定性变体，去除动作描写括号。

## Risks / Trade-offs

- [Risk] 「孩子」关键词与育儿焦虑分支冲突 → Mitigation：本分支要求同时含哄娃/带娃类词与疲惫词，与「孩子考不好」家长焦虑语境区分
- [Risk] 与加班疲惫分支重叠（「下班还要哄娃」） → Mitigation：哄娃关键词优先于纯加班分支，符合 mock 行为
