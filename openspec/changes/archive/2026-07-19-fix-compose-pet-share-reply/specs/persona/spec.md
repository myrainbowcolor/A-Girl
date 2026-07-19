## ADDED Requirements

### Requirement: 养宠物首轮分享口语回应

用户首轮分享养宠物（含「猫」「狗」「宠物」，且非「记得」记忆追问）时，生产路径 `compose_contextual_reply` 与 `mock.py` 场景分支 MUST 返回 1～2 句轻松亲昵接话，表达同频开心并轻问宠物习惯；至多一个问句；禁止落入问卷式 open 兜底或句首「嗯」类机械接话。分支须在宠物捣蛋续聊（代词「它」）之前命中。

#### Scenario: 生产路径 compose 养猫分享首轮

- **WHEN** `compose_contextual_reply` 处理「我养了一只叫橘子的猫，超粘人」
- **THEN** 返回含「猫」「粘人」或「撒娇」类亲昵接话，至多一个问句；不返回 `None` 或问卷式 open 兜底

#### Scenario: 生产路径 compose 泛宠物分享首轮

- **WHEN** `compose_contextual_reply` 处理「家里养了只狗，特别黏人」
- **THEN** 返回含「狗」「毛孩子」或「性格」类接话，至多一个问句；不返回 open 兜底

#### Scenario: 记忆追问不误入分享分支

- **WHEN** `compose_contextual_reply` 处理「你还记得我的猫叫什么吗」
- **THEN** 不返回养宠分享接话，由记忆召回或其他分支处理

#### Scenario: mock 场景养宠分享保持

- **WHEN** mock 场景引擎处理「我养了一只叫橘子的猫，超粘人」
- **THEN** 行为不因本需求回退，仍返回亲昵养宠接话
