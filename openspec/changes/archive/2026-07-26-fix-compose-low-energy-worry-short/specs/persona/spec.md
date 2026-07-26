## MODIFIED Requirements

### Requirement: 短句低落倾诉 compose 回应

用户发送整句 ≤12 字的低落倾诉（含「难过」「伤心」「委屈」「想哭」「心情不好」「不好受」「孤独」「孤单」「寂寞」「压力」「崩溃」「难受」「郁闷」「烦躁」「痛苦」「绝望」「无助」「迷茫」「空虚」「破防」「憋屈」「心痛」「心碎」「泪目」「要哭」等关键词，且非已由其他 compose 分支覆盖的长句场景）时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句先接住情绪的共情陪伴接话，至多一个问句，禁止落入问卷式 open 兜底；回复 MUST NOT 以「嗯」开头；与 `mock.py` 通用负面情绪分支行为一致。用户整句仅为单字「烦」或极简「烦啊」（≤4 字且含「烦」）时 MUST 先接住烦躁/心里堵的感受，至多一个轻问句，禁止落入问卷式 open 兜底。

用户发送短句没劲/没意思/低落口语（含「没劲」「好没劲」「没意思」「低落」，整句 len≤12）时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句接住低落感的共情接话，禁止落入问卷式 open 兜底；与 mock `_LOW` 分支行为一致。

用户发送短句心里堵/堵心口语（含「堵」「堵心」「堵得慌」「心里堵」，整句 len≤10）时，生产路径 `compose_contextual_reply` MUST 先接住心里堵的感受，至多一个轻问句，禁止落入问卷式 open 兜底；回复 MUST NOT 以「嗯」开头。

用户发送短句慌张/担心口语（含「慌」「害怕」「好怕」「担心」「好担心」，整句 len≤10，且非育儿焦虑语境）时，生产路径 `compose_contextual_reply` MUST 先接住慌张/担心感、表达陪伴，至多一个轻问句，禁止落入问卷式 open 兜底；回复 MUST NOT 以「嗯」开头。

#### Scenario: 生产路径 compose 短句「没劲」

- **WHEN** `compose_contextual_reply("没劲", [])` 被调用
- **THEN** 返回含「没劲」「低落」或「陪」类共情表述，不返回「好，我收到了」类 open 兜底

#### Scenario: 生产路径 compose 短句「好没劲」

- **WHEN** `compose_contextual_reply("好没劲", [])` 被调用
- **THEN** 返回含低落/陪伴类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「没意思」

- **WHEN** `compose_contextual_reply("没意思", [])` 被调用
- **THEN** 返回含低落/陪伴类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「心里堵」

- **WHEN** `compose_contextual_reply("心里堵", [])` 被调用
- **THEN** 返回含「堵」或「陪」类共情表述，不返回 `None` 或问卷式 open 兜底；回复 MUST NOT 以「嗯」开头

#### Scenario: 生产路径 compose 短句「堵得慌」

- **WHEN** `compose_contextual_reply("堵得慌", [])` 被调用
- **THEN** 返回含「堵」或「陪」类共情表述，不返回 open 兜底

#### Scenario: 生产路径 compose 短句「慌」

- **WHEN** `compose_contextual_reply("慌", [])` 被调用
- **THEN** 返回含「慌」或「陪」类共情表述，不返回 `None` 或问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「好担心」

- **WHEN** `compose_contextual_reply("好担心", [])` 被调用
- **THEN** 返回含「担心」或「陪」类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「好绝望」

- **WHEN** `compose_contextual_reply("好绝望", [])` 被调用
- **THEN** 返回含共情/陪伴表述，不返回「好，我收到了」类 open 兜底

#### Scenario: 生产路径 compose 单字「烦」

- **WHEN** `compose_contextual_reply("烦", [])` 被调用
- **THEN** 返回含「烦」或「堵」类共情表述，至多一个问句，不返回「好，我收到了」类 open 兜底
