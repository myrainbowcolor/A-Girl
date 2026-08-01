## ADDED Requirements

### Requirement: 短句自卑 compose 回应

用户发送整句 ≤12 字且含「自卑」的低落口语（如「好自卑」「自卑」「好自卑啊」「我好自卑」）时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句先接住自卑感的共情陪伴接话，至多一个问句，禁止落入问卷式 open 兜底；回复 MUST NOT 以「嗯」开头；回复 MUST NOT 套用「升职比较 / 原地踏步」专用话术敷衍；`mock.py` 场景路径 MUST 行为一致（不得返回空串或「好，我收到了」类问卷兜底）。本需求通过扩展既有比较/自我怀疑分支实现，并按关键词分流（含「自卑」时走自卑专用话术）。

#### Scenario: 生产路径 compose 短句「好自卑」

- **WHEN** `compose_contextual_reply("好自卑", [])` 被调用
- **THEN** 返回含自卑/不够好/陪着/否定自己类共情表述，不返回「好，我收到了」类 open 兜底；回复 MUST NOT 以「嗯」开头；不得仅用「升职 / 原地踏步」比较话术敷衍

#### Scenario: 生产路径 compose 短句「自卑」

- **WHEN** `compose_contextual_reply("自卑", [])` 被调用
- **THEN** 返回含自卑/陪着/自我怀疑类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「我好自卑」

- **WHEN** `compose_contextual_reply("我好自卑", [])` 被调用
- **THEN** 返回含自卑/陪着类共情表述，不返回「好，我收到了」类 open 兜底

#### Scenario: 生产路径 compose 短句「好自卑啊」

- **WHEN** `compose_contextual_reply("好自卑啊", [])` 被调用
- **THEN** 返回含自卑/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: mock 短句「好自卑」对齐

- **WHEN** mock 场景引擎处理整句「好自卑」
- **THEN** 返回含共情/陪伴表述，不返回空串或问卷式 open 兜底语气
