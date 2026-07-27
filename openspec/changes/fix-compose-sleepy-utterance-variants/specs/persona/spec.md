## MODIFIED Requirements

### Requirement: 短句困倦口语 compose 回应

用户发送整句困倦极简口语（「困」「好困」「有点困」「困了」「好困啊」，经 `is_minimal_sleepy_utterance` 识别），且非含「困死」「不想起床」等通勤长句时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句接住困倦/想睡的体贴接话，至多一个问句，禁止落入问卷式 open 兜底；回复 MUST NOT 以「嗯」开头。`mock.py` 场景分支 MUST 对同等困倦变体返回困倦共情接话，禁止落入 empathy 问卷兜底。

#### Scenario: 生产路径 compose 短句「好困」

- **WHEN** `compose_contextual_reply("好困", [])` 被调用
- **THEN** 返回含「困」或「歇」类体贴表述，不返回 `None` 或问卷式 open 兜底；回复 MUST NOT 以「嗯」开头

#### Scenario: 生产路径 compose 短句「有点困」

- **WHEN** `compose_contextual_reply("有点困", [])` 被调用
- **THEN** 返回含「困」或「歇」类体贴表述，不返回 `None` 或问卷式 open 兜底

#### Scenario: 生产路径 compose 单字「困」

- **WHEN** `compose_contextual_reply("困", [])` 被调用
- **THEN** 返回含「困」或「歇」类体贴表述，不返回 `None` 或「好，我收到了」类 open 兜底

#### Scenario: 生产路径 compose 困倦变体「困了」

- **WHEN** `compose_contextual_reply("困了", [])` 被调用
- **THEN** 返回含「困」或「歇」类体贴表述，不返回 `None` 或问卷式 open 兜底；回复 MUST NOT 以「嗯」开头

#### Scenario: 生产路径 compose 困倦变体「好困啊」

- **WHEN** `compose_contextual_reply("好困啊", [])` 被调用
- **THEN** 返回含「困」或「歇」类体贴表述，不返回 `None` 或问卷式 open 兜底；回复 MUST NOT 以「嗯」开头

#### Scenario: mock 场景困倦变体「困了」

- **WHEN** mock 场景引擎处理整句仅为「困了」
- **THEN** 返回含「困」或「歇」类困倦共情表述，不返回 empathy 问卷兜底
