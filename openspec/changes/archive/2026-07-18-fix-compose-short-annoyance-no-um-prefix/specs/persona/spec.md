## ADDED Requirements

### Requirement: 短句烦躁 compose 句首禁止嗯

系统 SHALL 使 `compose_contextual_reply` 处理短句烦躁口语（含「好烦」「有点烦」「挺烦」「烦死了」且整句 len≤10）时，返回句不以「嗯」开头；经 `polish_reply` 后处理仍不以「嗯」开头。

#### Scenario: 好烦 compose 不以嗯开头

- **WHEN** `compose_contextual_reply` 处理「好烦」，并经 `polish_reply` 后处理
- **THEN** 返回含「堵」或「烦」类共情表述，且不以「嗯」开头

#### Scenario: 有点烦 compose 不以嗯开头

- **WHEN** `compose_contextual_reply` 处理「有点烦」
- **THEN** 返回不以「嗯」开头的共情接话，至多一个问句
