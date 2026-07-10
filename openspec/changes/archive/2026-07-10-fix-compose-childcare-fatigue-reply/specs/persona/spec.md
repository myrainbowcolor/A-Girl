## ADDED Requirements

### Requirement: 育儿疲惫口语回应

用户表达一边上班一边哄娃/带娃的疲惫（含「哄娃」「带娃」「神兽」「孩子闹」与「累」「辛苦」「心累」「好累」等）时，生产路径 `compose_contextual_reply` 与 `mock.py` 场景分支 MUST 先接住育儿疲惫、表达陪伴，轻问今天最累的是哪一段；禁止落入问卷式 open 兜底或仅泛化「不太好受」套话。

#### Scenario: 生产路径 compose 哄娃疲惫续聊

- **WHEN** `compose_contextual_reply` 处理「但回家还要哄娃，心好累」，且近期用户话含报喜语境（如「项目过了」「超开心」）
- **THEN** 返回含「顾娃」「哄娃」或「带娃」类共情表述，表达陪伴意愿，至多一个问句；不返回「突然还是一阵子」类问卷套话

#### Scenario: 生产路径 compose 带娃心累首轮

- **WHEN** `compose_contextual_reply` 处理「一边上班一边带娃，心好累」
- **THEN** 返回含「带娃」「辛苦」或「耗」类共情表述，不返回问卷式 open 兜底

#### Scenario: mock 场景育儿疲惫保持

- **WHEN** mock 场景引擎处理「但回家还要哄娃，心好累」
- **THEN** 行为不因本需求回退，仍返回育儿疲惫共情接话
