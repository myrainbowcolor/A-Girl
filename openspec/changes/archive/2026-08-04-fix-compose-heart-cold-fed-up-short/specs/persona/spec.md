## ADDED Requirements

### Requirement: 短句心凉/寒心/受够了 compose 回应

用户发送整句 ≤12 字且含「心凉」「寒心」或「受够了」的短句口语（如「心凉了」「好心凉」「寒心了」「好寒心」「受够了」「我受够了」）时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句先接住心凉/寒心或受够了感受的共情陪伴接话，至多一个问句，禁止落入问卷式 open 兜底；回复 MUST NOT 以「嗯」开头；回复 MUST NOT 套用「撑不住/受不了」极限话术或问卷式「是突然还是一阵子」敷衍；`mock.py` 场景路径 MUST 行为一致。既有「撑不住/扛不住/受不了/绷不住」与短句低落倾诉路径 MUST 不受破坏。

#### Scenario: 生产路径 compose 短句「心凉了」

- **WHEN** `compose_contextual_reply("心凉了", [])` 被调用
- **THEN** 返回含心凉/寒心/陪着/失落类共情表述，不返回「好，我收到了」类 open 兜底；回复 MUST NOT 以「嗯」开头

#### Scenario: 生产路径 compose 短句「好心凉」

- **WHEN** `compose_contextual_reply("好心凉", [])` 被调用
- **THEN** 返回含心凉/寒心/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「寒心了」

- **WHEN** `compose_contextual_reply("寒心了", [])` 被调用
- **THEN** 返回含寒心/心凉/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「受够了」

- **WHEN** `compose_contextual_reply("受够了", [])` 被调用
- **THEN** 返回含受够了/陪着/累类共情表述，不返回问卷式 open 兜底；不得套用「撑不住」专用极限话术敷衍

#### Scenario: 既有「撑不住」仍命中

- **WHEN** `compose_contextual_reply("快撑不住了", [])` 被调用
- **THEN** 仍返回撑不住/极限类共情表述，不走心凉/寒心/受够了专用话术中的「心凉」「寒心」表述

#### Scenario: mock 短句「心凉了」对齐

- **WHEN** mock 场景引擎处理整句「心凉了」
- **THEN** 返回含共情/陪伴表述，不返回空串或问卷式 open 兜底语气
