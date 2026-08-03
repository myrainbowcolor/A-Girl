## ADDED Requirements

### Requirement: 短句被鸽/放鸽子 compose 回应

用户发送整句 ≤12 字且含「被鸽」「放鸽子」「放我鸽子」或「爽约」的被放鸽子/爽约口语（如「被鸽了」「放鸽子了」「放我鸽子」「又被鸽了」「他放我鸽子了」「爽约了」）时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句先接住被放鸽子/爽约的失落与委屈感的共情陪伴接话，至多一个问句，禁止落入问卷式 open 兜底；回复 MUST NOT 以「嗯」开头；回复 MUST NOT 套用失恋分手专用话术（如「分手」「失恋」）或吵架冷战专用话术敷衍；`mock.py` 场景路径 MUST 行为一致。既有失恋分手、吵架冷战、短句低落倾诉路径 MUST 不受破坏。

#### Scenario: 生产路径 compose 短句「被鸽了」

- **WHEN** `compose_contextual_reply("被鸽了", [])` 被调用
- **THEN** 返回含被鸽/放鸽子/爽约/陪着/失落/委屈类共情表述，不返回「好，我收到了」类 open 兜底；回复 MUST NOT 以「嗯」开头；不得套用「分手」「失恋」类话术敷衍

#### Scenario: 生产路径 compose 短句「放鸽子了」

- **WHEN** `compose_contextual_reply("放鸽子了", [])` 被调用
- **THEN** 返回含放鸽子/被鸽/陪着/失落类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「放我鸽子」

- **WHEN** `compose_contextual_reply("放我鸽子", [])` 被调用
- **THEN** 返回含放鸽子/被鸽/陪着类共情表述，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 短句「爽约了」

- **WHEN** `compose_contextual_reply("爽约了", [])` 被调用
- **THEN** 返回含爽约/陪着/失落类共情表述，不返回问卷式 open 兜底

#### Scenario: 既有失恋短句仍命中

- **WHEN** `compose_contextual_reply("分手了", [])` 被调用
- **THEN** 仍返回失恋/分手共情表述，不走被鸽/放鸽子专用话术

#### Scenario: mock 短句「被鸽了」对齐

- **WHEN** mock 场景引擎处理整句「被鸽了」
- **THEN** 返回含共情/陪伴表述，不返回空串或问卷式 open 兜底语气；不得套用「分手」「失恋」类话术
