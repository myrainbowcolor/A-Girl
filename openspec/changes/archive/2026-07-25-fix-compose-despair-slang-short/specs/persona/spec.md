## MODIFIED Requirements

### Requirement: 短句低落倾诉 compose 回应

用户发送整句 ≤12 字的低落倾诉（含「难过」「伤心」「委屈」「想哭」「心情不好」「不好受」「孤独」「孤单」「寂寞」「压力」「崩溃」「难受」「郁闷」「烦躁」「痛苦」「绝望」「无助」「迷茫」「空虚」「破防」「憋屈」「心痛」「心碎」「泪目」「要哭」等关键词，且非已由其他 compose 分支覆盖的长句场景）时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句先接住情绪的共情陪伴接话，至多一个问句，禁止落入问卷式 open 兜底；回复 MUST NOT 以「嗯」开头；与 `mock.py` 通用负面情绪分支行为一致。用户整句仅为单字「烦」或极简「烦啊」（≤4 字且含「烦」）时 MUST 先接住烦躁/心里堵的感受，至多一个轻问句，禁止落入问卷式 open 兜底。

#### Scenario: 生产路径 compose 短句「有点难过」

- **WHEN** `compose_contextual_reply("有点难过", [])` 被调用
- **THEN** 返回含共情/陪伴表述（如「不太好受」「陪着」），不返回「哪一块你现在最想提」类问卷兜底

#### Scenario: 生产路径 compose 短句「心情不好」

- **WHEN** `compose_contextual_reply("心情不好", [])` 被调用
- **THEN** 返回含共情/陪伴表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「好委屈」

- **WHEN** `compose_contextual_reply("好委屈", [])` 被调用
- **THEN** 返回含共情/陪伴表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「好孤独」

- **WHEN** `compose_contextual_reply("好孤独", [])` 被调用
- **THEN** 返回含「孤独」「孤单」或「陪」类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「压力大」

- **WHEN** `compose_contextual_reply("压力大", [])` 被调用
- **THEN** 返回含「压力」或「陪」类共情表述，不返回「突然还是一阵子」类问卷套话

#### Scenario: 生产路径 compose 短句「压力好大」

- **WHEN** `compose_contextual_reply("压力好大", [])` 被调用
- **THEN** 返回含「压力」或「陪」类共情表述，不返回问卷式 open 兜底

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

#### Scenario: 生产路径 compose 短句「好绝望」

- **WHEN** `compose_contextual_reply("好绝望", [])` 被调用
- **THEN** 返回含共情/陪伴表述，不返回「好，我收到了」类 open 兜底

#### Scenario: 生产路径 compose 短句「迷茫」

- **WHEN** `compose_contextual_reply("迷茫", [])` 被调用
- **THEN** 返回含共情/陪伴表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「破防」

- **WHEN** `compose_contextual_reply("破防", [])` 被调用
- **THEN** 返回含共情/陪伴表述，不返回「好，我收到了」类 open 兜底

#### Scenario: 生产路径 compose 短句「憋屈」

- **WHEN** `compose_contextual_reply("憋屈", [])` 被调用
- **THEN** 返回含共情/陪伴表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 单字「烦」

- **WHEN** `compose_contextual_reply("烦", [])` 被调用
- **THEN** 返回含「烦」或「堵」类共情表述，至多一个问句，不返回「好，我收到了」类 open 兜底
