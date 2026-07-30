## ADDED Requirements

### Requirement: 短句想家/思乡 compose 回应

用户发送整句 ≤12 字且含「想家」「想爸妈」「想回家」或「想父母」的想家/思乡口语（如「想家了」「想家」「好想家」「想爸妈」「想回家」）时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句先接住思念与空落感的共情陪伴接话，至多一个问句，禁止落入问卷式 open 兜底；回复 MUST NOT 以「嗯」开头；`mock.py` 场景分支 MUST 行为一致。本需求与既有节日孤独分支（落寞/团圆/过年/一个人）及想念/好久未见分支（想你/想念等）互不抢占。

#### Scenario: 生产路径 compose 短句「想家了」

- **WHEN** `compose_contextual_reply("想家了", [])` 被调用
- **THEN** 返回含「想家」「家」「空」「陪」或「难受」类共情表述，不返回「慢慢讲」类问卷兜底；回复 MUST NOT 以「嗯」开头

#### Scenario: 生产路径 compose 短句「想爸妈」

- **WHEN** `compose_contextual_reply("想爸妈", [])` 被调用
- **THEN** 返回含共情/陪伴表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「想回家」

- **WHEN** `compose_contextual_reply("想回家", [])` 被调用
- **THEN** 返回含共情/陪伴表述，不返回问卷式 open 兜底

#### Scenario: mock 短句「想家了」对齐

- **WHEN** mock 场景引擎处理整句「想家了」
- **THEN** 返回含共情/陪伴表述，不返回问卷式 open 兜底语气
