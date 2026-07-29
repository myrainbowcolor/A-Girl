## ADDED Requirements

### Requirement: 正向关键词否定前缀（通过/录取）

系统 SHALL 在情感词典中为正向词「通过」「录取」配置常见否定前缀（「没通过」「未通过」「不通过」「没录取」「未录取」），使 `is_positive_utterance` / `contains_keyword` 对含上述否定形式的用户话 MUST NOT 判为正向报喜语境。

#### Scenario: 「没通过」不判正向

- **WHEN** 调用 `is_positive_utterance("没通过")`
- **THEN** 返回 `False`

#### Scenario: 「未通过」不判正向

- **WHEN** 调用 `is_positive_utterance("面试未通过")`
- **THEN** 返回 `False`

#### Scenario: 「通过了」仍判正向

- **WHEN** 调用 `is_positive_utterance("面试通过了")`
- **THEN** 返回 `True`

### Requirement: 短句选拔/面试失利 compose 回应

用户发送整句 ≤12 字且含「面试砸」「面试挂」「没通过」「落选」或「搞砸」的选拔/面试失利口语（如「面试砸了」「面试挂了」「没通过」「落选了」「搞砸了」）时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句先接住挫败/失落感的共情陪伴接话，至多一个问句，禁止落入问卷式 open 兜底，禁止「太棒了」「替你开心」类报喜话术；回复 MUST NOT 以「嗯」开头；`mock.py` 场景分支 MUST 行为一致。本需求与考试失利分支（考砸/没考好/挂科）互不抢占。

#### Scenario: 生产路径 compose 短句「面试砸了」

- **WHEN** `compose_contextual_reply("面试砸了", [])` 被调用
- **THEN** 返回含「面试」「挫败」「失落」「陪」或「别急」类共情表述，不返回「太棒了」类报喜或「慢慢讲」类问卷兜底；回复 MUST NOT 以「嗯」开头

#### Scenario: 生产路径 compose 短句「没通过」

- **WHEN** `compose_contextual_reply("没通过", [])` 被调用
- **THEN** 返回含共情/陪伴表述，不返回「太棒了」「替你开心」类报喜话术

#### Scenario: 生产路径 compose 短句「落选了」

- **WHEN** `compose_contextual_reply("落选了", [])` 被调用
- **THEN** 返回含共情/陪伴表述，不返回问卷式 open 兜底

#### Scenario: mock 短句「面试砸了」对齐

- **WHEN** mock 场景引擎处理整句「面试砸了」
- **THEN** 返回含共情/陪伴表述，不返回报喜或问卷式 open 兜底语气
