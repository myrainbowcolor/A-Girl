## ADDED Requirements

### Requirement: 倦怠极限口语回应

用户表达快到承受极限（含「撑不住」「扛不住」「受不了」）时，生产路径 `compose_contextual_reply` 与 `mock.py` 场景分支 MUST 先接住「快到极限」感受、表达陪伴意愿，至多一个轻问句；禁止落入问卷式 open 兜底或句首「嗯」类机械接话。

#### Scenario: 生产路径 compose 倦怠极限续聊

- **WHEN** `compose_contextual_reply` 处理「有时候觉得自己快撑不住了」，且近期用户话含育儿疲惫语境（如「哄娃」「心好累」）
- **THEN** 返回含「极限」「陪」或「累」类共情表述，表达陪伴意愿，至多一个问句；不返回 `None` 或问卷式 open 兜底

#### Scenario: 生产路径 compose 扛不住首轮

- **WHEN** `compose_contextual_reply` 处理「我真的扛不住了」
- **THEN** 返回含「极限」或「陪」类共情表述，不返回 open 兜底

#### Scenario: mock 场景倦怠极限保持

- **WHEN** mock 场景引擎处理「有时候觉得自己快撑不住了」
- **THEN** 行为不因本需求回退，仍返回倦怠极限共情接话
