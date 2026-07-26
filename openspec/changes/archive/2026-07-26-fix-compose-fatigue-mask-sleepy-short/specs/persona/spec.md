## ADDED Requirements

### Requirement: 疲惫变体「今天好累啊」compose 回应

用户整句仅为「今天好累啊」时，生产路径 `compose_contextual_reply` MUST 经 `is_minimal_fatigue_utterance` 命中疲惫共情分支，返回含「累」「辛苦」或「歇」类疲惫共情表述，禁止落入问卷式 open 兜底；回复 MUST NOT 以「嗯」开头。

#### Scenario: 生产路径 compose 疲惫变体「今天好累啊」

- **WHEN** `compose_contextual_reply("今天好累啊", [])` 被调用
- **THEN** 返回含「累」「辛苦」或「歇」类疲惫共情表述，不返回 `None` 或问卷式 open 兜底；回复 MUST NOT 以「嗯」开头

### Requirement: masking 变体「一般般」compose 回应

用户整句仅为「一般般」时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句轻轻接住 masking 情绪的陪伴接话，可轻问一句，禁止落入问卷式 open 兜底；与 `mock.py` masking 分支及 `_MINIMAL_MASKING` 行为一致。

#### Scenario: 生产路径 compose 整句「一般般」

- **WHEN** `compose_contextual_reply("一般般", [])` 被调用
- **THEN** 返回含「平平」「陪着」或轻问类 masking 共情表述，不返回 `None` 或问卷式 open 兜底

### Requirement: 短句困倦口语 compose 回应

用户发送整句 ≤6 字的困倦口语（「困」「好困」「有点困」），且非含「困死」「不想起床」等通勤长句时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句接住困倦/想睡的体贴接话，至多一个问句，禁止落入问卷式 open 兜底；回复 MUST NOT 以「嗯」开头。

#### Scenario: 生产路径 compose 短句「好困」

- **WHEN** `compose_contextual_reply("好困", [])` 被调用
- **THEN** 返回含「困」或「歇」类体贴表述，不返回 `None` 或问卷式 open 兜底；回复 MUST NOT 以「嗯」开头

#### Scenario: 生产路径 compose 短句「有点困」

- **WHEN** `compose_contextual_reply("有点困", [])` 被调用
- **THEN** 返回含「困」或「歇」类体贴表述，不返回 `None` 或问卷式 open 兜底

#### Scenario: 生产路径 compose 单字「困」

- **WHEN** `compose_contextual_reply("困", [])` 被调用
- **THEN** 返回含「困」或「歇」类体贴表述，不返回 `None` 或「好，我收到了」类 open 兜底
