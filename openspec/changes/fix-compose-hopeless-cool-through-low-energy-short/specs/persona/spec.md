## ADDED Requirements

### Requirement: 短句没救了/凉透了/提不起劲 compose 回应

用户发送整句 ≤12 字且含「没救」「凉透」「彻底凉」「提不起劲」或「提不起精神」的短句口语（如「没救了」「我没救了」「凉透了」「心都凉透了」「彻底凉了」「提不起劲」「提不起劲来」「提不起精神」）时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句先接住绝望泄气、凉透心寒或提不起劲无力感的共情陪伴接话，至多一个问句，禁止落入问卷式 open 兜底；回复 MUST NOT 以「嗯」开头；回复 MUST NOT 套用「心凉了」「没劲」「心死了」专用话术中的「心凉」「没劲」「心死」表述敷衍；`mock.py` 场景路径 MUST 行为一致。既有心凉/寒心/受够了、心灰/心死/麻了、短句低落（含「没劲」）路径 MUST 不受破坏。本需求不将「没救了」视为危机信号（危机仍仅由 `safety.py` 既有关键词触发）。

#### Scenario: 生产路径 compose 短句「没救了」

- **WHEN** `compose_contextual_reply("没救了", [])` 被调用
- **THEN** 返回含没救/空/陪着/缓类共情表述，不返回「好，我收到了」类 open 兜底；回复 MUST NOT 以「嗯」开头；不得触发危机热线话术

#### Scenario: 生产路径 compose 短句「我没救了」

- **WHEN** `compose_contextual_reply("我没救了", [])` 被调用
- **THEN** 返回含没救/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「凉透了」

- **WHEN** `compose_contextual_reply("凉透了", [])` 被调用
- **THEN** 返回含凉透/凉/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「心都凉透了」

- **WHEN** `compose_contextual_reply("心都凉透了", [])` 被调用
- **THEN** 返回含凉透/凉/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「彻底凉了」

- **WHEN** `compose_contextual_reply("彻底凉了", [])` 被调用
- **THEN** 返回含彻底凉/凉透/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「提不起劲」

- **WHEN** `compose_contextual_reply("提不起劲", [])` 被调用
- **THEN** 返回含提不起劲/没劲/无力/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「提不起精神」

- **WHEN** `compose_contextual_reply("提不起精神", [])` 被调用
- **THEN** 返回含提不起精神/提不起劲/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 既有「心凉了」仍命中心凉分支

- **WHEN** `compose_contextual_reply("心凉了", [])` 被调用
- **THEN** 仍返回心凉专用共情表述，不走没救了/凉透了/提不起劲专用话术中的「没救」「彻底凉」「提不起劲」表述

#### Scenario: 既有「没劲」仍命中短句低落

- **WHEN** `compose_contextual_reply("没劲", [])` 被调用
- **THEN** 仍返回短句低落/没劲共情表述，不走没救了/凉透了专用话术

#### Scenario: mock 短句「没救了」对齐

- **WHEN** mock 场景引擎处理整句「没救了」
- **THEN** 返回含共情/陪伴表述，不返回空串或问卷式 open 兜底语气；不得含危机热线
