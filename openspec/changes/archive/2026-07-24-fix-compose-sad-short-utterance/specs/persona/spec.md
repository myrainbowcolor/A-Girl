## ADDED Requirements

### Requirement: 短句低落倾诉 compose 回应

用户发送整句 ≤12 字的低落倾诉（含「难过」「伤心」「委屈」「想哭」「心情不好」「不好受」等关键词，且非已由其他 compose 分支覆盖的长句场景）时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句先接住情绪的共情陪伴接话，至多一个问句，禁止落入问卷式 open 兜底；回复 MUST NOT 以「嗯」开头；与 `mock.py` 通用负面情绪分支行为一致。

#### Scenario: 生产路径 compose 短句「有点难过」

- **WHEN** `compose_contextual_reply("有点难过", [])` 被调用
- **THEN** 返回含共情/陪伴表述（如「不太好受」「陪着」），不返回「哪一块你现在最想提」类问卷兜底

#### Scenario: 生产路径 compose 短句「心情不好」

- **WHEN** `compose_contextual_reply("心情不好", [])` 被调用
- **THEN** 返回含共情/陪伴表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「好委屈」

- **WHEN** `compose_contextual_reply("好委屈", [])` 被调用
- **THEN** 返回含共情/陪伴表述，不返回问卷式 open 兜底
