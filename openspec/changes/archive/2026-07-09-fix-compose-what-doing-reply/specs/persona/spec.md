## ADDED Requirements

### Requirement: 社交探问口语回应

用户直接询问 NPC 在做什么（含「你在干嘛」「在干嘛」「干什么」）时，生产路径 `compose_contextual_reply` 与 `mock.py` 场景分支 MUST 先口语化描述自己在做什么，再轻问用户状态；近期用户话含「无聊」时 MUST 续问「摸鱼」类轻松话题，否则轻问「忙不忙」；禁止落入问卷式 open 兜底或忽略提问。

#### Scenario: 生产路径 compose 无聊上文探问

- **WHEN** `compose_contextual_reply` 处理「你在干嘛」，且近期用户话含「好无聊啊」
- **THEN** 返回含「发呆」「茶」或「沙发」类自述，并含「摸鱼」或「忙不忙」类轻问；不返回「好，我收到了」类 open 兜底

#### Scenario: 生产路径 compose 普通探问

- **WHEN** `compose_contextual_reply` 处理「你在干嘛」，且无无聊上文
- **THEN** 返回含「发呆」或「茶」类自述，并轻问用户「忙不忙」或「在做什么」；至多一个问句

#### Scenario: mock 场景探问保持

- **WHEN** mock 场景引擎处理「你在干嘛」
- **THEN** 行为不因本需求回退，仍返回口语化自述 + 轻问
