## ADDED Requirements

### Requirement: 开心分享口语回应

用户分享开心事或报喜（含「开心」「超开心」「offer」「过了」「录取」等正向词，且非「不开心」否定）时，生产路径 `compose_contextual_reply` 与 `mock.py` 场景分支 MUST 先同频共振、表达替 ta 高兴，至多一个轻问句；禁止落入问卷式 open 兜底或敷衍「好，我收到了」。

#### Scenario: 生产路径 compose 报喜分享首轮

- **WHEN** `compose_contextual_reply` 处理「今天项目过了，超开心！」
- **THEN** 返回含「开心」或「替你」类同频表述，表达真心高兴，至多一个问句；不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 城市期待续聊

- **WHEN** `compose_contextual_reply` 处理「终于可以去喜欢的城市了」
- **THEN** 返回含「城市」或「期待」类同频表述，表达替 ta 高兴，至多一个问句

#### Scenario: mock 场景开心分享保持

- **WHEN** mock 场景引擎处理「我拿到 dream offer 了！！」
- **THEN** 行为不因本需求回退，仍返回同频共振接话
