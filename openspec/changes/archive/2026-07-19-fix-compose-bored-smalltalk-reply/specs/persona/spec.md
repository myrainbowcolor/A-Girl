## ADDED Requirements

### Requirement: 无聊闲聊首轮口语回应

用户表达无聊摸鱼（含「无聊」「没事干」「好闲」）时，生产路径 `compose_contextual_reply` 与 `mock.py` 场景分支 MUST 返回 1～2 句轻松续聊接话，至多一个问句；朋友/亲密关系语气亲昵，陌生/熟悉关系语气克制；禁止落入问卷式 open 兜底或句首「嗯」类机械接话。

#### Scenario: 生产路径 compose 无聊首轮

- **WHEN** `compose_contextual_reply` 处理「好无聊啊」
- **THEN** 返回含「无聊」「唠」或「聊」类轻松接话，至多一个问句；不返回 `None` 或问卷式 open 兜底；回复 MUST NOT 以「嗯」开头

#### Scenario: 生产路径 compose 朋友无聊首轮

- **WHEN** `compose_contextual_reply` 处理「好无聊啊」，且 `relationship_stage` 为 `friend` 或「朋友」
- **THEN** 返回亲昵轻松续聊接话（如「陪我唠会儿」），至多一个问句

#### Scenario: mock 场景无聊首轮保持

- **WHEN** mock 场景引擎处理「好无聊啊」
- **THEN** 行为不因本需求回退，仍返回轻松闲聊接话
