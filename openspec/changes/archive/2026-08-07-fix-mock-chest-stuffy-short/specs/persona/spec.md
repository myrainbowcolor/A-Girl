## ADDED Requirements

### Requirement: 短句心里堵/堵得慌 mock 与 compose 对齐

用户发送整句 ≤10 字且命中「堵得慌 / 心里堵 / 堵心 / 心堵 / 好堵」的短句口语（如「心好堵」「好心堵」「堵得慌」「心里堵得慌」「心堵得慌」「心里堵」「堵心」「心堵」「好堵」「堵得慌啊」）时，`mock.py` 场景路径 MUST 返回 1～2 句先接住心里堵感受的共情陪伴接话，与生产路径 `compose_contextual_reply` 既有分支行为一致；至多一个轻问句；禁止返回空串或问卷式 open 兜底语气；回复 MUST NOT 以「嗯」开头；不得触发危机热线话术。本需求不将「堵 / 心堵 / 堵得慌」视为危机信号（危机仍仅由 `safety.py` 既有关键词触发）。既有 compose「心里堵 / 堵得慌」分支 MUST 保持可用。

#### Scenario: mock 短句「堵得慌」对齐

- **WHEN** mock 场景引擎处理整句「堵得慌」
- **THEN** 返回含堵/陪着/消化/缠人类共情表述，不返回空串或问卷式 open 兜底语气；不得含危机热线；回复 MUST NOT 以「嗯」开头

#### Scenario: mock 短句「心好堵」对齐

- **WHEN** mock 场景引擎处理整句「心好堵」
- **THEN** 返回含堵/陪着类共情表述，不返回空串

#### Scenario: mock 短句「好心堵」对齐

- **WHEN** mock 场景引擎处理整句「好心堵」
- **THEN** 返回含堵/陪着类共情表述，不返回空串

#### Scenario: mock 短句「心里堵」对齐

- **WHEN** mock 场景引擎处理整句「心里堵」
- **THEN** 返回含堵/陪着类共情表述，不返回空串；回复 MUST NOT 以「嗯」开头

#### Scenario: mock 短句「好堵」对齐

- **WHEN** mock 场景引擎处理整句「好堵」
- **THEN** 返回含堵/陪着类共情表述，不返回空串

#### Scenario: 既有 compose「堵得慌」仍可用

- **WHEN** `compose_contextual_reply("堵得慌", [])` 被调用
- **THEN** 仍返回含堵或陪类共情表述，不返回 `None` 或问卷式 open 兜底
