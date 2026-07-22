## MODIFIED Requirements

### Requirement: 短句烦躁 compose 句首禁止嗯

系统 SHALL 使 `compose_contextual_reply` 处理短句烦躁口语（含「好烦」「有点烦」「挺烦」「烦死了」且整句 len≤10）时，返回句不以「嗯」开头；先接住烦躁、表达陪伴，禁止「是突然这样的，还是已经有一阵子了」类问卷式 open 兜底；经 `polish_reply` 后处理仍不以「嗯」开头。`mock.py` `_empathy_reply` 陌生关系「烦」分支 MUST 与 compose 行为一致，不得含「突然还是一阵子」套话。

#### Scenario: 好烦 compose 不以嗯开头

- **WHEN** `compose_contextual_reply` 处理「好烦」，并经 `polish_reply` 后处理
- **THEN** 返回含「堵」或「烦」类共情表述，且不以「嗯」开头；回复 MUST NOT 含「突然」与「一阵子」

#### Scenario: 有点烦 compose 不以嗯开头

- **WHEN** `compose_contextual_reply` 处理「有点烦」
- **THEN** 返回不以「嗯」开头的共情接话，至多一个问句；回复 MUST NOT 含「突然」与「一阵子」

#### Scenario: mock 陌生关系烦分支对齐

- **WHEN** mock `_empathy_reply` 处理「好烦」，关系阶段为「陌生」
- **THEN** 返回共情接话，不含「突然还是一阵子」类问卷套话
