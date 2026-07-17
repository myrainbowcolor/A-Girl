## ADDED Requirements

### Requirement: 日常闲聊 compose 口语回应

用户发送天气/电影轻松闲聊（含「天气」「电影」「不错」「挺好」且句长 ≤16）、表达感谢（含「谢谢」「感谢」「多谢」）、道别晚安（含「晚安」「睡了」「再见」「拜拜」「先走了」）或 emo/心累低落口语（含「emo」「丧」「心累」）时，生产路径 `compose_contextual_reply` 与 `mock.py` 场景分支 MUST 返回 1～2 句口语化接话，至多一个问句；感谢分支 MUST 在 `is_positive_utterance` 开心分享之前命中，禁止将纯感谢句误判为报喜。

#### Scenario: 生产路径 compose 天气闲聊

- **WHEN** `compose_contextual_reply` 处理「今天天气不错」
- **THEN** 返回含「天气」或「晒」类轻松接话，至多一个问句；不返回 `None` 或问卷式 open 兜底

#### Scenario: 生产路径 compose 电影闲聊

- **WHEN** `compose_contextual_reply` 处理「刚看完一部挺好的电影」
- **THEN** 返回含「电影」或「片子」类轻松接话，至多一个问句；不返回 `None`

#### Scenario: 生产路径 compose 感谢接话

- **WHEN** `compose_contextual_reply` 处理「感觉你挺温柔的，谢谢」
- **THEN** 返回含「客气」或「高兴」类感谢回应，不返回「开心起来了」类报喜套话

#### Scenario: 生产路径 compose 晚安道别

- **WHEN** `compose_contextual_reply` 处理「晚安」
- **THEN** 返回含「晚安」或「好梦」类道别接话，至多一个问句

#### Scenario: 生产路径 compose emo 心累

- **WHEN** `compose_contextual_reply` 处理「心好累」
- **THEN** 返回含「低落」或「陪」类共情表述，不返回问卷式 open 兜底

#### Scenario: mock 场景日常闲聊保持

- **WHEN** mock 场景引擎处理「今天天气不错」
- **THEN** 行为不因本需求回退，仍返回轻松闲聊接话
