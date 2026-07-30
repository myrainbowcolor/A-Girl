## ADDED Requirements

### Requirement: 短句失望/灰心 compose 回应

用户发送整句 ≤12 字且含「失望」「失落」「灰心」或「心酸」的低落口语（如「好失望」「失落」「灰心了」「好心酸」）时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句先接住情绪的共情陪伴接话，至多一个问句，禁止落入问卷式 open 兜底；回复 MUST NOT 以「嗯」开头；`mock.py` 场景/倾诉路径 MUST 行为一致（不得返回空串或「好，我收到了」类问卷兜底）。本需求通过扩展既有短句低落关键词实现，与难过/委屈/绝望等分支共享话术池。

#### Scenario: 生产路径 compose 短句「好失望」

- **WHEN** `compose_contextual_reply("好失望", [])` 被调用
- **THEN** 返回含共情/陪伴表述（如「不太好受」「陪着」「沉」「听着」），不返回「好，我收到了」类 open 兜底；回复 MUST NOT 以「嗯」开头

#### Scenario: 生产路径 compose 短句「失落」

- **WHEN** `compose_contextual_reply("失落", [])` 被调用
- **THEN** 返回含共情/陪伴表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「灰心了」

- **WHEN** `compose_contextual_reply("灰心了", [])` 被调用
- **THEN** 返回含共情/陪伴表述，不返回「好，我收到了」类 open 兜底

#### Scenario: 生产路径 compose 短句「好心酸」

- **WHEN** `compose_contextual_reply("好心酸", [])` 被调用
- **THEN** 返回含共情/陪伴表述，不返回问卷式 open 兜底

#### Scenario: mock 短句「好失望」对齐

- **WHEN** mock 场景引擎处理整句「好失望」
- **THEN** 返回含共情/陪伴表述，不返回空串或问卷式 open 兜底语气
