## ADDED Requirements

### Requirement: masking 不知道 compose 口语回应

用户整句仅为极简 masking/回避口语「不知道」或「说不上」时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句轻轻接住、耐心陪伴的共情接话，可轻问一句，禁止落入问卷式 open 兜底；回复 MUST NOT 以「嗯」开头；与 `mock.py` 场景分支行为一致。

#### Scenario: 生产路径 compose 整句「不知道」

- **WHEN** `compose_contextual_reply` 处理整句仅为「不知道」
- **THEN** 返回含「说不清」「不用逼」「陪着」或「慢慢理」类 masking 共情表述，不返回 `None` 或问卷式 open 兜底；回复 MUST NOT 以「嗯」开头

#### Scenario: 生产路径 compose 整句「说不上」

- **WHEN** `compose_contextual_reply` 处理整句仅为「说不上」
- **THEN** 返回含「说不清」「不用逼」「陪着」或「慢慢理」类 masking 共情表述，不返回 `None` 或问卷式 open 兜底

#### Scenario: mock 场景 masking 不知道保持

- **WHEN** mock 场景引擎处理「不知道」
- **THEN** 行为不因本需求回退，仍返回 masking 低落共情接话
