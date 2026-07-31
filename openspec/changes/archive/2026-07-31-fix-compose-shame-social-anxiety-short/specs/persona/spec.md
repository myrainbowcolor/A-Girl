## ADDED Requirements

### Requirement: 短句丢脸/羞耻/社恐 compose 回应

用户发送整句 ≤12 字且含「丢脸」「丢人」「羞耻」或「社恐」的社交尴尬口语（如「好丢脸」「丢脸」「好丢人」「丢人」「好羞耻」「羞耻」「社恐了」「好社恐」）时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句先接住丢脸/羞耻/社恐感受的共情陪伴接话，至多一个问句，禁止落入问卷式 open 兜底；回复 MUST NOT 以「嗯」开头；`mock.py` 场景路径 MUST 行为一致（不得返回空串或「好，我收到了」类问卷兜底）。本需求通过扩展既有短句无语/尴尬/社死分支实现，并按关键词分流话术（社死优先于社恐；羞耻、丢脸/丢人各自话术，禁止混用无语话术敷衍）。

#### Scenario: 生产路径 compose 短句「好丢脸」

- **WHEN** `compose_contextual_reply("好丢脸", [])` 被调用
- **THEN** 返回含丢脸/尴尬/找地缝/陪着类共情表述，不返回「好，我收到了」类 open 兜底；回复 MUST NOT 以「嗯」开头

#### Scenario: 生产路径 compose 短句「丢人」

- **WHEN** `compose_contextual_reply("丢人", [])` 被调用
- **THEN** 返回含丢脸/丢人/尴尬/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「好羞耻」

- **WHEN** `compose_contextual_reply("好羞耻", [])` 被调用
- **THEN** 返回含羞耻/尴尬/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「社恐了」

- **WHEN** `compose_contextual_reply("社恐了", [])` 被调用
- **THEN** 返回含社恐/社交压力/陪着类共情表述，不返回「好，我收到了」类 open 兜底；不得误用「社死」专用话术作为唯一命中

#### Scenario: 生产路径 compose 短句「好社恐」

- **WHEN** `compose_contextual_reply("好社恐", [])` 被调用
- **THEN** 返回含社恐/社交/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: mock 短句「好丢脸」对齐

- **WHEN** mock 场景引擎处理整句「好丢脸」
- **THEN** 返回含共情/陪伴表述，不返回空串或问卷式 open 兜底语气
