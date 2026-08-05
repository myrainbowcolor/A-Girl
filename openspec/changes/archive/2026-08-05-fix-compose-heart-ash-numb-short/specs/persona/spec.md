## ADDED Requirements

### Requirement: 短句心灰/心死/麻了 compose 回应

用户发送整句 ≤12 字且含「心灰」「心死」「麻了」或「麻木」的短句口语（如「心灰了」「好心灰」「心死了」「好心死」「麻了」「我麻了」「麻木了」）时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句先接住心灰/心死或麻木感的共情陪伴接话，至多一个问句，禁止落入问卷式 open 兜底；回复 MUST NOT 以「嗯」开头；回复 MUST NOT 套用「灰心了」通用短句低落套话与问卷式「是突然还是一阵子」敷衍；`mock.py` 场景路径 MUST 行为一致。既有含「灰心」的短句低落倾诉、心凉/寒心/受够了路径 MUST 不受破坏。本需求不将「心死」视为危机信号（危机仍仅由 `safety.py` 既有关键词触发）。

#### Scenario: 生产路径 compose 短句「心灰了」

- **WHEN** `compose_contextual_reply("心灰了", [])` 被调用
- **THEN** 返回含心灰/灰/陪着/缓类共情表述，不返回「好，我收到了」类 open 兜底；回复 MUST NOT 以「嗯」开头

#### Scenario: 生产路径 compose 短句「好心灰」

- **WHEN** `compose_contextual_reply("好心灰", [])` 被调用
- **THEN** 返回含心灰/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「心死了」

- **WHEN** `compose_contextual_reply("心死了", [])` 被调用
- **THEN** 返回含心死/空/陪着类共情表述，不返回问卷式 open 兜底；不得触发危机热线话术

#### Scenario: 生产路径 compose 短句「麻了」

- **WHEN** `compose_contextual_reply("麻了", [])` 被调用
- **THEN** 返回含麻/麻木/空/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「麻木了」

- **WHEN** `compose_contextual_reply("麻木了", [])` 被调用
- **THEN** 返回含麻木/麻/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 既有「灰心了」仍命中短句低落

- **WHEN** `compose_contextual_reply("灰心了", [])` 被调用
- **THEN** 仍返回短句低落共情表述，不走心灰/心死/麻了专用话术中的「心死」「麻木」表述

#### Scenario: mock 短句「心灰了」对齐

- **WHEN** mock 场景引擎处理整句「心灰了」
- **THEN** 返回含共情/陪伴表述，不返回空串或问卷式 open 兜底语气
