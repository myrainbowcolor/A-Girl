## ADDED Requirements

### Requirement: 短句无语尴尬社死 compose 回应

用户发送整句 ≤12 字且含「无语」「尴尬」或「社死」的社交尴尬/无语口语（如「无语」「好无语」「有点无语」「尴尬」「好尴尬」「社死了」「好社死」）时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句先接住无语/尴尬感的共情陪伴接话，至多一个问句，禁止落入问卷式 open 兜底（如「你想从哪儿开始说」「随便丢几个词」）；回复 MUST NOT 以「嗯」开头；`mock.py` 场景分支 MUST 行为一致。

#### Scenario: 生产路径 compose 短句「好无语」

- **WHEN** `compose_contextual_reply("好无语", [])` 被调用
- **THEN** 返回含「无语」「尴尬」「憋屈」或「陪」类共情表述，不返回「你想从哪儿开始说」类问卷兜底；回复 MUST NOT 以「嗯」开头

#### Scenario: 生产路径 compose 短句「无语」

- **WHEN** `compose_contextual_reply("无语", [])` 被调用
- **THEN** 返回含共情/陪伴表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「好尴尬」

- **WHEN** `compose_contextual_reply("好尴尬", [])` 被调用
- **THEN** 返回含「尴尬」或「陪」类共情表述，不返回「随便丢几个词」类 open 兜底

#### Scenario: 生产路径 compose 短句「社死了」

- **WHEN** `compose_contextual_reply("社死了", [])` 被调用
- **THEN** 返回含「尴尬」「社死」或「陪」类共情表述，不返回问卷式 open 兜底

#### Scenario: mock 短句「有点无语」对齐

- **WHEN** mock 场景引擎处理整句「有点无语」
- **THEN** 返回含共情/陪伴表述，不返回问卷式 open 兜底语气
