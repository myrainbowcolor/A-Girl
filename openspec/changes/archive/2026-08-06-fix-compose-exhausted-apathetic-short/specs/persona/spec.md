## ADDED Requirements

### Requirement: 短句累透了/不想动/没盼头/无所谓了 compose 回应

用户发送整句 ≤12 字且命中「累透」「累趴」「不想动」「懒得动」「没盼头」「没啥盼头」或「无所谓了」的短句口语（如「累透了」「我累透了」「累趴了」「不想动」「不想动了」「懒得动」「我懒得动」「没盼头」「没啥盼头」「无所谓了」「我无所谓了」「都无所谓了」）时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句先接住力竭、动不起来、没盼头或无所谓泄气感的共情陪伴接话，至多一个问句，禁止落入问卷式 open 兜底；回复 MUST NOT 以「嗯」开头；回复 MUST NOT 套用「心累」「提不起劲」「废了」专用话术中的「心累」「提不起劲」「废了」表述敷衍；`mock.py` 场景路径 MUST 行为一致。既有「心累透了」MUST 仍走心累分支，不得因含「累透」误入本分支专用话术。既有极简疲惫（如「好累啊」）、提不起劲、废了/完了路径 MUST 不受破坏。本需求不将「无所谓了 / 没盼头」视为危机信号（危机仍仅由 `safety.py` 既有关键词触发）。

#### Scenario: 生产路径 compose 短句「累透了」

- **WHEN** `compose_contextual_reply("累透了", [])` 被调用
- **THEN** 返回含累透/力竭/陪着/缓类共情表述，不返回「好，我收到了」类 open 兜底；回复 MUST NOT 以「嗯」开头；不得触发危机热线话术

#### Scenario: 生产路径 compose 短句「我累透了」

- **WHEN** `compose_contextual_reply("我累透了", [])` 被调用
- **THEN** 返回含累透/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「累趴了」

- **WHEN** `compose_contextual_reply("累趴了", [])` 被调用
- **THEN** 返回含累趴/力竭/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「不想动」

- **WHEN** `compose_contextual_reply("不想动", [])` 被调用
- **THEN** 返回含不想动/动不了/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「懒得动」

- **WHEN** `compose_contextual_reply("懒得动", [])` 被调用
- **THEN** 返回含懒得动/不想动/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「没盼头」

- **WHEN** `compose_contextual_reply("没盼头", [])` 被调用
- **THEN** 返回含盼头/空/陪着类共情表述，不返回问卷式 open 兜底；不得触发危机热线话术

#### Scenario: 生产路径 compose 短句「无所谓了」

- **WHEN** `compose_contextual_reply("无所谓了", [])` 被调用
- **THEN** 返回含无所谓/泄气/陪着类共情表述，不返回问卷式 open 兜底；不得触发危机热线话术

#### Scenario: 既有「心累透了」仍命中心累分支

- **WHEN** `compose_contextual_reply("心累透了", [])` 被调用
- **THEN** 仍返回心累/低落专用共情表述，不走本分支「累透了」专用话术中的「累透了的时候」类表述

#### Scenario: 既有「好累啊」仍命中极简疲惫

- **WHEN** `compose_contextual_reply("好累啊", [])` 被调用
- **THEN** 仍返回极简疲惫共情表述，不走本分支专用「累透/累趴」话术

#### Scenario: 既有「提不起劲」仍命中提不起劲分支

- **WHEN** `compose_contextual_reply("提不起劲", [])` 被调用
- **THEN** 仍返回提不起劲专用共情表述，不走本分支「不想动/懒得动」专用话术

#### Scenario: mock 短句「不想动」对齐

- **WHEN** mock 场景引擎处理整句「不想动」
- **THEN** 返回含共情/陪伴表述，不返回空串或问卷式 open 兜底语气；不得含危机热线
