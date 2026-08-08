## ADDED Requirements

### Requirement: mock 短句没意思低落对齐

用户发送整句 ≤12 字且含「没意思」的低落口语（如「没意思」「没意思了」「好没意思」「真没意思」「感觉没意思」）时，`mock.py` 场景路径 MUST 返回 1～2 句接住低落感的共情陪伴接话，至多一个问句，禁止返回空串或「好，我收到了」类问卷兜底；回复 MUST NOT 以「嗯」开头。匹配条件 MUST 与既有 compose 短句没劲/没意思/低落分支一致（≤12 字含「没劲」「没意思」或「低落」）。既有 compose「没意思 / 没劲 / 低落」路径 MUST 不受破坏；既有「emo / 丧 / 心累」低落分支 MUST 仍有效。本需求不将「没意思」视为危机信号（危机仍仅由 `safety.py` 既有关键词触发）。

#### Scenario: mock 短句「没意思了」对齐

- **WHEN** mock 场景引擎处理整句「没意思了」
- **THEN** 返回含「低落」「硬撑」或「陪」类共情表述，不返回空串或问卷式 open 兜底语气；不得含危机热线；回复 MUST NOT 以「嗯」开头

#### Scenario: mock 短句「好没意思」对齐

- **WHEN** mock 场景引擎处理整句「好没意思」
- **THEN** 返回含低落/陪伴类共情表述，不返回空串

#### Scenario: mock 短句「真没意思」对齐

- **WHEN** mock 场景引擎处理整句「真没意思」
- **THEN** 返回含低落/陪伴类共情表述，不返回空串

#### Scenario: mock 短句「没意思」对齐

- **WHEN** mock 场景引擎处理整句「没意思」
- **THEN** 返回含低落/陪伴类共情表述，不返回空串

#### Scenario: 既有 compose「没意思了」仍命中低落分支

- **WHEN** `compose_contextual_reply("没意思了", [])` 被调用
- **THEN** 仍返回含「低落」「硬撑」或「陪」类共情表述，不返回 `None` 或问卷式 open 兜底

#### Scenario: 既有 compose「没劲」仍命中低落分支

- **WHEN** `compose_contextual_reply("没劲", [])` 被调用
- **THEN** 仍返回短句低落共情表述，不走其它专用话术抢占
