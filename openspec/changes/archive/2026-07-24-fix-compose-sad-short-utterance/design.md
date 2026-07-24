## Context

`compose_contextual_reply` 在 scene_first 编排第二层覆盖大量场景分支，未命中时返回 `None` 并落入 `compose_open_reply` 问卷兜底。`mock.py` 在 `_scene_reply` 中有通用负面情绪处理（难过/伤心/孤独/压力等），但 compose 仅对「我不开心」等个别句式有分支，短句如「有点难过」「心情不好」会漏接。

基线 dialogue quality 26/26 全绿，属 compose 路径探测缺口，与近期 `fix-compose-minimal-ack-enen` 等同类型小步补齐。

## Goals / Non-Goals

**Goals:**

- 在 `compose_contextual_reply` return None 之前，为 ≤12 字短句低落倾诉增加共情分支
- 模板与 mock 通用负面分支语气一致：先接住、陪着，至多一个轻问句
- 补充单测覆盖「有点难过」「心情不好」「好委屈」

**Non-Goals:**

- 不改动 `safety.py`、危机干预、记忆检索
- 不新增 sentiment_lexicon 函数（关键词内联即可）
- 不处理长句低落倾诉（已有其他分支或 LLM 路径）
- 不调整 compose_open_reply 问卷池

## Decisions

1. **触发条件**：`len(text) <= 12` 且含 `难过/伤心/委屈/想哭/心情不好/不好受` 任一关键词；排除已处理的「我不开心」等精确匹配分支。
2. **插入位置**：在 `好烦` 短句分支之后、封闭极简附和分支之前（通用负面兜底区），避免与失眠/分手等具体场景冲突。
3. **模板风格**：复用 mock 语气「能感觉到你现在不太好受」「我就在这儿陪着你」，禁止句首「嗯」；亲密关系可略暖但不越界。
4. **不修改 mock**：mock 已有通用处理，仅补齐 compose 缺口。

## Risks / Trade-offs

- [误触发] 长句含「难过」但 >12 字 → 由长度限制规避，长句走 LLM 或其他分支
- [与「不开心」分支重复] 「我不开心」已有独立分支，新分支用关键词匹配不会冲突
