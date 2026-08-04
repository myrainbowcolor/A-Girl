## ADDED Requirements

### Requirement: 短句「怕了」与无育儿语境害怕 compose/mock 回应

用户发送整句 ≤10 字且含「怕了」的慌张口语（如「怕了」「我怕了」），且非育儿焦虑语境时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句先接住害怕/慌张感的共情陪伴接话，至多一个问句，禁止落入问卷式 open 兜底；回复 MUST NOT 以「嗯」开头。本需求通过扩展既有短句慌张/担心关键词（追加「怕了」）实现。

`mock.py` 场景路径与 `_empathy_reply` MUST 与 compose 对齐：无育儿语境的「害怕」「好害怕」「好怕」「怕了」MUST 返回慌张/担心共情，MUST NOT 套用家长育儿焦虑话术（如「当家长担心孩子」），不得返回空串。既有含「孩子」「儿子」「女儿」「太严厉」「耽误」「考不好」的育儿焦虑路径 MUST 不受破坏；既有「慌」「好担心」短句路径 MUST 不受破坏。

#### Scenario: 生产路径 compose 短句「怕了」

- **WHEN** `compose_contextual_reply("怕了", [])` 被调用
- **THEN** 返回含慌/怕/陪着/绷类共情表述，不返回 `None` 或「好，我收到了」类 open 兜底；回复 MUST NOT 以「嗯」开头

#### Scenario: 生产路径 compose 短句「我怕了」

- **WHEN** `compose_contextual_reply("我怕了", [])` 被调用
- **THEN** 返回含慌/怕/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: mock 短句「好害怕」不误路由育儿

- **WHEN** mock 场景引擎处理整句「好害怕」（无孩子/儿子/女儿/严厉/耽误等育儿语境）
- **THEN** 返回慌张/担心共情陪伴表述，MUST NOT 含「家长」或「孩子」类育儿焦虑话术；不得返回空串

#### Scenario: mock 短句「怕了」对齐

- **WHEN** mock 场景引擎处理整句「怕了」
- **THEN** 返回含共情/陪伴表述，不返回空串或问卷式 open 兜底语气

#### Scenario: 既有「慌」短句仍命中

- **WHEN** `compose_contextual_reply("慌", [])` 被调用
- **THEN** 仍返回慌张/陪伴类共情表述，不返回 `None`

#### Scenario: 既有育儿焦虑「害怕耽误」仍命中

- **WHEN** mock 场景引擎处理含「害怕耽误」且含孩子/耽误等育儿语境的倾诉
- **THEN** 仍返回家长育儿焦虑共情表述，不走纯慌张短句话术敷衍
