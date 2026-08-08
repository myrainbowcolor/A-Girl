## ADDED Requirements

### Requirement: 短句感觉空了/掏空了 compose 回应

用户发送整句 ≤12 字且命中「感觉空了」或「掏空了」的短句口语（如「感觉空了」「掏空了」「感觉掏空了」「被掏空了」）时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句先接住发空/被掏空感的共情陪伴接话，至多一个问句，禁止落入问卷式 open 兜底或返回 `None`；回复 MUST NOT 以「嗯」开头；回复 MUST NOT 套用「空落落」「不想干」专用话术敷衍；`mock.py` 场景路径 MUST 行为一致（不得返回空串）。匹配 MUST NOT 使用裸子串「空了」（避免无关短句误伤）；「整个人」+「空了」既有路径 MUST 保持有效。既有「空落落的 / 空空的 / 心里空」MUST 仍走空落落路径；含「工作 / 上班」等更早工作话题优先分支的句子 MUST 不被本分支抢占。本需求不将「感觉空了 / 掏空了」视为危机信号（危机仍仅由 `safety.py` 既有关键词触发）。

#### Scenario: 生产路径 compose 短句「感觉空了」

- **WHEN** `compose_contextual_reply("感觉空了", [])` 被调用
- **THEN** 返回含空/掏空/陪着/缓/硬撑类共情表述，不返回 `None` 或「好，我收到了」类 open 兜底；回复 MUST NOT 以「嗯」开头；不得触发危机热线话术；不得含「空落落」「不想干」专用表述敷衍

#### Scenario: 生产路径 compose 短句「掏空了」

- **WHEN** `compose_contextual_reply("掏空了", [])` 被调用
- **THEN** 返回含空/掏空/陪着类共情表述，不返回 `None` 或问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「感觉掏空了」

- **WHEN** `compose_contextual_reply("感觉掏空了", [])` 被调用
- **THEN** 返回含空/掏空/陪着类共情表述，不返回 `None` 或问卷式 open 兜底

#### Scenario: 既有「整个人空了」仍命中发空分支

- **WHEN** `compose_contextual_reply("整个人空了", [])` 被调用
- **THEN** 仍返回含空/掏空/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 既有「空落落的」仍命中空落落路径

- **WHEN** `compose_contextual_reply("空落落的", [])` 被调用
- **THEN** 仍返回空落落/陪着类共情表述，不走本分支「感觉空了/掏空了」专用话术抢占断言失败

#### Scenario: 裸「空了」不误伤

- **WHEN** `compose_contextual_reply("空了", [])` 被调用
- **THEN** 不因本分支强制命中发空专用话术（可返回 `None` 或其它既有路径）

#### Scenario: mock 短句「感觉空了」对齐

- **WHEN** mock 场景引擎处理整句「感觉空了」
- **THEN** 返回含共情/陪伴表述，不返回空串或问卷式 open 兜底语气；不得含危机热线

#### Scenario: mock 短句「掏空了」对齐

- **WHEN** mock 场景引擎处理整句「掏空了」
- **THEN** 返回含共情/陪伴表述，不返回空串
