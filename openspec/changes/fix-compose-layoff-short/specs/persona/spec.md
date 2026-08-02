## ADDED Requirements

### Requirement: 短句失业/裁员 compose 回应

用户发送整句 ≤12 字且含「被裁」「裁员」「被开除」「失业」或「丢工作」的失业/裁员口语（如「被裁了」「裁员了」「被裁员了」「被开除了」「失业了」「丢工作了」）时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句先接住失业/被裁失落感的共情陪伴接话，至多一个问句，禁止落入问卷式 open 兜底；回复 MUST NOT 以「嗯」开头；回复 MUST NOT 套用通用工作话题话术（如「忙不过来」「不公平」「特别耗你」）敷衍；`mock.py` 场景路径 MUST 行为一致。本需求须优先于通用工作话题短句分支，使「丢工作了」不被误路由。既有加班疲惫、冲动辞职念头、工作话题（非失业）路径 MUST 不受破坏。

#### Scenario: 生产路径 compose 短句「被裁了」

- **WHEN** `compose_contextual_reply("被裁了", [])` 被调用
- **THEN** 返回含被裁/失业/陪着/失落类共情表述，不返回「好，我收到了」类 open 兜底；回复 MUST NOT 以「嗯」开头；不得仅用「忙不过来 / 不公平」类工作话题话术敷衍

#### Scenario: 生产路径 compose 短句「失业了」

- **WHEN** `compose_contextual_reply("失业了", [])` 被调用
- **THEN** 返回含失业/陪着/失落类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「丢工作了」不误路由

- **WHEN** `compose_contextual_reply("丢工作了", [])` 被调用
- **THEN** 返回含丢工作/失业/陪着类共情表述，不得套用「忙不过来」「不公平」类通用工作话题话术；不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「被开除了」

- **WHEN** `compose_contextual_reply("被开除了", [])` 被调用
- **THEN** 返回含开除/陪着/失落类共情表述，不返回问卷式 open 兜底

#### Scenario: 既有工作话题短句仍命中

- **WHEN** `compose_contextual_reply("工作上的事", [])` 被调用
- **THEN** 仍返回工作话题共情/探问表述，不走失业/裁员专用话术

#### Scenario: mock 短句「被裁了」对齐

- **WHEN** mock 场景引擎处理整句「被裁了」
- **THEN** 返回含共情/陪伴表述，不返回空串或问卷式 open 兜底语气；不得套用「忙不过来 / 不公平」类工作话题话术
