## ADDED Requirements

### Requirement: emo/低落 compose 句首禁止嗯

系统 SHALL 使 `compose_contextual_reply` 处理 emo/心累口语（含「心好累」「emo」「丧」）及「不开心」时，返回句不以「嗯」开头；经 `polish_reply` 后处理仍不以「嗯」开头。`mock.py` 对应场景分支 MUST 与 compose 行为一致。

#### Scenario: 心好累 compose 不以嗯开头

- **WHEN** `compose_contextual_reply` 处理「心好累」，并经 `polish_reply` 后处理
- **THEN** 返回含「低落」或「陪」类共情表述，且不以「嗯」开头

#### Scenario: 不开心 compose 不以嗯开头

- **WHEN** `compose_contextual_reply` 处理「我不开心了」
- **THEN** 返回不以「嗯」开头的陪伴式接话
