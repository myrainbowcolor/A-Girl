## ADDED Requirements

### Requirement: 短句废了/完了/提不起兴趣 compose 回应

用户发送整句 ≤12 字且命中「废了」「好废」「完蛋」「我完了」、整句精确「完了」，或含「提不起兴趣」的短句口语（如「废了」「我废了」「好废」「整个人废了」「完了」「我完了」「完蛋了」「提不起兴趣」「提不起兴趣来」）时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句先接住自我否定泄气、完蛋感或提不起兴趣无力感的共情陪伴接话，至多一个问句，禁止落入问卷式 open 兜底；回复 MUST NOT 以「嗯」开头；回复 MUST NOT 套用「没救了」「提不起劲」「心累」专用话术中的「没救」「提不起劲」「心累」表述敷衍；`mock.py` 场景路径 MUST 行为一致。完成义短句（如「做完了」「写完了」）MUST NOT 因含「完了」子串误入本分支。既有没救了/凉透了/提不起劲、短句低落（含「心累」）路径 MUST 不受破坏。本需求不将「废了 / 完了」视为危机信号（危机仍仅由 `safety.py` 既有关键词触发）。

#### Scenario: 生产路径 compose 短句「废了」

- **WHEN** `compose_contextual_reply("废了", [])` 被调用
- **THEN** 返回含废/泄气/陪着/缓类共情表述，不返回「好，我收到了」类 open 兜底；回复 MUST NOT 以「嗯」开头；不得触发危机热线话术

#### Scenario: 生产路径 compose 短句「我废了」

- **WHEN** `compose_contextual_reply("我废了", [])` 被调用
- **THEN** 返回含废/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「好废」

- **WHEN** `compose_contextual_reply("好废", [])` 被调用
- **THEN** 返回含废/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「完了」

- **WHEN** `compose_contextual_reply("完了", [])` 被调用
- **THEN** 返回含完/完蛋/泄气/陪着类共情表述，不返回问卷式 open 兜底；不得触发危机热线话术

#### Scenario: 生产路径 compose 短句「我完了」

- **WHEN** `compose_contextual_reply("我完了", [])` 被调用
- **THEN** 返回含完/完蛋/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「完蛋了」

- **WHEN** `compose_contextual_reply("完蛋了", [])` 被调用
- **THEN** 返回含完蛋/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「提不起兴趣」

- **WHEN** `compose_contextual_reply("提不起兴趣", [])` 被调用
- **THEN** 返回含兴趣/提不起/发沉/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「提不起兴趣来」

- **WHEN** `compose_contextual_reply("提不起兴趣来", [])` 被调用
- **THEN** 返回含兴趣/提不起/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 完成义「做完了」不误入本分支

- **WHEN** `compose_contextual_reply("做完了", [])` 被调用
- **THEN** 不命中废了/完了/提不起兴趣专用共情话术（不得仅因含「完了」子串返回完蛋感话术）

#### Scenario: 既有「提不起劲」仍命中提不起劲分支

- **WHEN** `compose_contextual_reply("提不起劲", [])` 被调用
- **THEN** 仍返回提不起劲专用共情表述，不走废了/完了/提不起兴趣专用话术中的「废了」「完蛋」「提不起兴趣」表述

#### Scenario: 既有「没救了」仍命中没救分支

- **WHEN** `compose_contextual_reply("没救了", [])` 被调用
- **THEN** 仍返回没救专用共情表述，不走废了/完了专用话术

#### Scenario: mock 短句「废了」对齐

- **WHEN** mock 场景引擎处理整句「废了」
- **THEN** 返回含共情/陪伴表述，不返回空串或问卷式 open 兜底语气；不得含危机热线
