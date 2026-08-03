## ADDED Requirements

### Requirement: 短句愧疚/内疚/摆烂/无消费后悔 compose 回应

用户发送整句 ≤12 字且含「愧疚」「内疚」「摆烂」，或含「后悔」且无消费线索（不含「钱」「买」「手」「花」「乱花钱」「管不住」）的短句口语（如「好愧疚」「内疚」「我好内疚」「摆烂了」「想摆烂」「好后悔」「后悔了」）时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句先接住内疚自责或摆烂无力感的共情陪伴接话，至多一个问句，禁止落入问卷式 open 兜底；回复 MUST NOT 以「嗯」开头；回复 MUST NOT 套用冲动消费后悔专用话术（如「乱花钱」「管不住手」「没忍住」）敷衍；`mock.py` 场景路径 MUST 行为一致。既有冲动消费后悔路径（如「乱花钱好后悔」「好后悔买了」「觉得自己好没用，管不住手」）MUST 不受破坏。

#### Scenario: 生产路径 compose 短句「好愧疚」

- **WHEN** `compose_contextual_reply("好愧疚", [])` 被调用
- **THEN** 返回含愧疚/内疚/陪着/自责类共情表述，不返回「好，我收到了」类 open 兜底；回复 MUST NOT 以「嗯」开头；不得套用「乱花钱」「管不住手」类话术敷衍

#### Scenario: 生产路径 compose 短句「内疚」

- **WHEN** `compose_contextual_reply("内疚", [])` 被调用
- **THEN** 返回含内疚/愧疚/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「摆烂了」

- **WHEN** `compose_contextual_reply("摆烂了", [])` 被调用
- **THEN** 返回含摆烂/陪着/无力类共情表述，不返回问卷式 open 兜底；不得套用「乱花钱」「管不住手」类话术

#### Scenario: 生产路径 compose 短句「好后悔」（无消费语境）

- **WHEN** `compose_contextual_reply("好后悔", [])` 被调用
- **THEN** 返回含后悔/陪着类共情表述，不返回问卷式 open 兜底；不得含「乱花钱」「管不住手」「没忍住」

#### Scenario: 既有冲动消费后悔仍命中

- **WHEN** `compose_contextual_reply("好后悔买了", [])` 被调用
- **THEN** 仍返回冲动消费后悔共情表述（可含后悔/没忍住/乱花钱类），不走无消费后悔/愧疚/摆烂专用话术中的「摆烂」表述

#### Scenario: mock 短句「好愧疚」对齐

- **WHEN** mock 场景引擎处理整句「好愧疚」
- **THEN** 返回含共情/陪伴表述，不返回空串或问卷式 open 兜底语气；不得套用「乱花钱」「管不住手」类话术
