## MODIFIED Requirements

### Requirement: 短句低落倾诉 compose 回应

用户发送整句 ≤12 字的低落倾诉（含「难过」「伤心」「委屈」「想哭」「心情不好」「不好受」「孤独」「孤单」「寂寞」「压力」「崩溃」「难受」「郁闷」「烦躁」「痛苦」等关键词，且非已由其他 compose 分支覆盖的长句场景）时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句先接住情绪的共情陪伴接话，至多一个问句，禁止落入问卷式 open 兜底；回复 MUST NOT 以「嗯」开头；与 `mock.py` 通用负面情绪分支行为一致。

#### Scenario: 生产路径 compose 短句「好崩溃」

- **WHEN** `compose_contextual_reply("好崩溃", [])` 被调用
- **THEN** 返回含「崩溃」或「陪」类共情表述，不返回「好，我收到了」类 open 兜底

#### Scenario: 生产路径 compose 短句「难受」

- **WHEN** `compose_contextual_reply("难受", [])` 被调用
- **THEN** 返回含共情/陪伴表述（如「不太好受」「陪着」），不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「好郁闷」

- **WHEN** `compose_contextual_reply("好郁闷", [])` 被调用
- **THEN** 返回含共情/陪伴表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「好累好累」

- **WHEN** `compose_contextual_reply("好累好累", [])` 被调用
- **THEN** 返回含「累」「辛苦」或「歇」类疲惫共情表述，不返回 open 兜底；回复 MUST NOT 以「嗯」开头

#### Scenario: 生产路径 compose 疲惫变体「累坏了」

- **WHEN** `compose_contextual_reply("累坏了", [])` 被调用
- **THEN** 返回含「累」「辛苦」或「歇」类疲惫共情表述，不返回 open 兜底
