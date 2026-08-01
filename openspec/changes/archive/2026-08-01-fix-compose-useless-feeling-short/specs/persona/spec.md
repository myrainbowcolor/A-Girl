## ADDED Requirements

### Requirement: 短句「好没用」自我否定 compose 回应

用户发送整句 ≤12 字且含「没用」、且**不含**冲动消费语境词（「乱花钱」「钱」「买」「花」「管不住」「手」）的自我否定口语（如「好没用」「没用」「我好没用」）时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句先接住「觉得自己没用」感受的共情陪伴接话，至多一个问句，禁止落入问卷式 open 兜底；回复 MUST NOT 以「嗯」开头；回复 MUST NOT 套用冲动消费后悔话术（如「管不住手」「这次最让你后悔」「乱花钱」）；`mock.py` 场景路径 MUST 行为一致。含消费语境的「觉得自己好没用，管不住手」等既有冲动消费自责路径 MUST 仍走消费后悔共情，不受本需求改动破坏。

#### Scenario: 生产路径 compose 短句「好没用」

- **WHEN** `compose_contextual_reply("好没用", [])` 被调用
- **THEN** 返回含没用/否定自己/陪着类共情表述，不返回「好，我收到了」类 open 兜底；回复 MUST NOT 以「嗯」开头；不得出现「管不住手」「后悔」「乱花钱」类消费话术

#### Scenario: 生产路径 compose 短句「我好没用」

- **WHEN** `compose_contextual_reply("我好没用", [])` 被调用
- **THEN** 返回含没用/陪着/自我否定类共情表述，不返回问卷式 open 兜底；不得套用冲动消费后悔话术

#### Scenario: 生产路径 compose 短句「没用」

- **WHEN** `compose_contextual_reply("没用", [])` 被调用
- **THEN** 返回含陪着/自我否定类共情表述，不返回问卷式 open 兜底；不得套用冲动消费后悔话术

#### Scenario: 生产路径 compose 冲动消费自责仍命中

- **WHEN** `compose_contextual_reply` 在已有乱花钱上文后处理「觉得自己好没用，管不住手」
- **THEN** 仍返回含「没用」或「管不住」类消费自责共情表述，不急着贴标签，不返回问卷式 open 兜底

#### Scenario: mock 短句「好没用」对齐

- **WHEN** mock 场景引擎处理整句「好没用」
- **THEN** 返回含共情/陪伴表述，不返回空串或问卷式 open 兜底语气；不得套用「管不住手 / 这次最让你后悔」类消费话术
