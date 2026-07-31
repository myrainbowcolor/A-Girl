## ADDED Requirements

### Requirement: 短句内耗/心态崩 compose 回应

用户发送整句 ≤12 字且含「内耗」「心态崩」「心态炸」「心态爆炸」或「被掏空」的低落口语（如「内耗」「好内耗」「心态崩了」「心态炸了」「被掏空了」）时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句先接住情绪的共情陪伴接话，至多一个问句，禁止落入问卷式 open 兜底；回复 MUST NOT 以「嗯」开头；`mock.py` 场景/倾诉路径 MUST 行为一致（不得返回空串或「好，我收到了」类问卷兜底）。本需求通过扩展既有短句低落关键词实现，与难过/委屈/绝望/失望等分支共享话术池。

#### Scenario: 生产路径 compose 短句「内耗」

- **WHEN** `compose_contextual_reply("内耗", [])` 被调用
- **THEN** 返回含共情/陪伴表述（如「不太好受」「陪着」「沉」「听着」），不返回「好，我收到了」类 open 兜底；回复 MUST NOT 以「嗯」开头

#### Scenario: 生产路径 compose 短句「好内耗」

- **WHEN** `compose_contextual_reply("好内耗", [])` 被调用
- **THEN** 返回含共情/陪伴表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「心态崩了」

- **WHEN** `compose_contextual_reply("心态崩了", [])` 被调用
- **THEN** 返回含共情/陪伴表述，不返回「好，我收到了」类 open 兜底

#### Scenario: 生产路径 compose 短句「心态炸了」

- **WHEN** `compose_contextual_reply("心态炸了", [])` 被调用
- **THEN** 返回含共情/陪伴表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「被掏空了」

- **WHEN** `compose_contextual_reply("被掏空了", [])` 被调用
- **THEN** 返回含共情/陪伴表述，不返回问卷式 open 兜底

#### Scenario: mock 短句「内耗」对齐

- **WHEN** mock 场景引擎处理整句「内耗」
- **THEN** 返回含共情/陪伴表述，不返回空串或问卷式 open 兜底语气
