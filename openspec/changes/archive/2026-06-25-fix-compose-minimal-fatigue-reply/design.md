## Context

`scene_first` 编排优先调用 `compose_contextual_reply`，未命中才走 `SceneReplyEngine`（mock 场景分支）。persona spec 已要求单字「累」使用「极简 masking 低落 / 疲惫共情」侧重；`compose_contextual_reply` 已对「还好」「不知道」等整句极简口语有专属分支，但单字「累」缺失。mock `_scene_reply` 中「累」被通用负面关键词分支（`"累" in text`）抢先命中，返回泛化「不太好受」套话。

## Goals / Non-Goals

**Goals:**
- compose 与 mock 对整句仅为「累」时返回短句疲惫共情，含「累/辛苦/歇」等疲惫语义，至多一个问句
- 分支优先级：单字「累」须在通用负面关键词分支之前，与「还好」「不知道」同级
- 补充单测，确保 compose 路径可测

**Non-Goals:**
- 不改 persona prompt 侧重（已实现）
- 不改 avatar / analyzer（「累」已 comfort）
- 不改长句含「累」的既有分支（如「好累」「心累」）

## Decisions

1. **在 compose 的「还行/还好」分支附近增加 `text == "累"` 分支**
   - 理由：与现有极简 masking 分支位置一致，便于维护
   - 备选：并入封闭句分支 — 拒绝，会误判为边界封闭

2. **在 mock `_scene_reply` 通用负面分支（约 L520）之前增加 `text == "累"` 分支**
   - 理由：避免 `"累" in text` 泛化匹配单字时返回「不太好受」
   - 长句「今天好累」仍走原有 `_empathy_reply` 或场景分支

3. **话术风格**：短句、先接住疲惫，可轻问「身子累还是心里累」，禁止问卷连珠炮

## Risks / Trade-offs

- [Risk] 「好累」等双字句行为变化 → 仅用 `text == "累"` 精确匹配，不影响含「累」长句
- [Risk] compose 与 mock 话术不完全一致 → 语义对齐即可，不要求字面相同
