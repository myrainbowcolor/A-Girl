## ADDED Requirements

### Requirement: 防御心态口语回应

用户表达被误解或觉得没人懂（含「你不懂」「没人懂」「不懂我」等）时，生产路径 `compose_contextual_reply` 与 `mock.py` 场景分支 MUST 先接住委屈、承认可能没完全懂，表达认真倾听意愿；禁止反驳、讲道理或落入问卷式 open 兜底。用户封闭撤回（含「不想说」「不说了」「算了」）时 MUST 尊重边界、短句陪伴，禁止追问。

#### Scenario: 生产路径 compose 防御心态首轮

- **WHEN** `compose_contextual_reply` 处理「你不懂的，没人懂」
- **THEN** 返回含「懂」「委屈」或「听」类共情表述，不反驳用户，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 封闭撤回续聊

- **WHEN** `compose_contextual_reply` 处理「算了，不想说了」，且近期用户话含防御心态语境
- **THEN** 返回含「陪着」「不说也没关系」类边界尊重表述，至多一个问句，不返回问卷式 open 兜底

#### Scenario: mock 场景防御心态保持

- **WHEN** mock 场景引擎处理「你不懂的，没人懂」
- **THEN** 行为不因本需求回退，仍返回共情接话
