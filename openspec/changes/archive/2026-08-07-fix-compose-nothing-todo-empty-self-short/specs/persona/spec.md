## ADDED Requirements

### Requirement: 短句什么都不想干/整个人空了 compose 回应

用户发送整句 ≤12 字且命中「不想干」，或命中「整个人空了 / 整个人都空了」（含「整个人」且含「空了」）的短句口语（如「什么都不想干」「我什么都不想干」「啥也不想干」「啥都不想干」「什么也不想干」「整个人空了」「整个人都空了」）时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句先接住提不起干劲或整个人发空的共情陪伴接话，至多一个问句，禁止落入问卷式 open 兜底；回复 MUST NOT 以「嗯」开头；回复 MUST NOT 套用「不想动」「懒得动」「空落落」专用话术中的「不想动」「懒得动」「空落落」表述敷衍；`mock.py` 场景路径 MUST 行为一致。既有「不想动 / 懒得动」MUST 仍走既有分支；既有「空落落的」MUST 仍走空落落路径。本需求不将「不想干 / 整个人空了」视为危机信号（危机仍仅由 `safety.py` 既有关键词触发）。

#### Scenario: 生产路径 compose 短句「什么都不想干」

- **WHEN** `compose_contextual_reply("什么都不想干", [])` 被调用
- **THEN** 返回含不想干/干劲/陪着/缓类共情表述，不返回「好，我收到了」类 open 兜底；回复 MUST NOT 以「嗯」开头；不得触发危机热线话术；不得含「不想动」「懒得动」专用表述

#### Scenario: 生产路径 compose 短句「我什么都不想干」

- **WHEN** `compose_contextual_reply("我什么都不想干", [])` 被调用
- **THEN** 返回含不想干/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「啥也不想干」

- **WHEN** `compose_contextual_reply("啥也不想干", [])` 被调用
- **THEN** 返回含不想干/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「整个人空了」

- **WHEN** `compose_contextual_reply("整个人空了", [])` 被调用
- **THEN** 返回含空/掏空/陪着类共情表述，不返回问卷式 open 兜底；不得含「空落落」专用表述敷衍

#### Scenario: 生产路径 compose 短句「整个人都空了」

- **WHEN** `compose_contextual_reply("整个人都空了", [])` 被调用
- **THEN** 返回含空/掏空/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 既有「不想动」仍命中不想动分支

- **WHEN** `compose_contextual_reply("不想动", [])` 被调用
- **THEN** 仍返回不想动专用共情表述，不走本分支「不想干」专用话术

#### Scenario: 既有「空落落的」仍命中空落落路径

- **WHEN** `compose_contextual_reply("空落落的", [])` 被调用
- **THEN** 仍返回空落落/陪着类共情表述，不走本分支「整个人空了」专用话术

#### Scenario: mock 短句「什么都不想干」对齐

- **WHEN** mock 场景引擎处理整句「什么都不想干」
- **THEN** 返回含共情/陪伴表述，不返回空串或问卷式 open 兜底语气；不得含危机热线
