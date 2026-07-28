## ADDED Requirements

### Requirement: 短句考试失利 compose 回应

用户发送整句 ≤12 字且含「考砸」「没考好」或「挂科」的考试失利口语（如「考砸了」「没考好」「挂科了」「考砸了呜」），且非家长育儿语境（不含「孩子」「儿子」「女儿」）时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句先接住挫败/失落感的共情陪伴接话，至多一个问句，禁止落入问卷式 open 兜底（如「好，我接住了。慢慢讲~」「你想到什么就说什么」）；禁止说教式「下次加油」灌鸡汤；回复 MUST NOT 以「嗯」开头；`mock.py` 场景分支 MUST 行为一致。本需求与考前焦虑分支（紧张/高考/考试等）互不抢占。

#### Scenario: 生产路径 compose 短句「考砸了」

- **WHEN** `compose_contextual_reply("考砸了", [])` 被调用
- **THEN** 返回含「考砸」「挫败」「失落」「陪」或「别急」类共情表述，不返回「慢慢讲」类问卷兜底；回复 MUST NOT 以「嗯」开头

#### Scenario: 生产路径 compose 短句「没考好」

- **WHEN** `compose_contextual_reply("没考好", [])` 被调用
- **THEN** 返回含共情/陪伴表述，不返回问卷式 open 兜底；不返回家长育儿焦虑话术

#### Scenario: 生产路径 compose 短句「挂科了」

- **WHEN** `compose_contextual_reply("挂科了", [])` 被调用
- **THEN** 返回含「挂科」「挫败」「陪」或「别急」类共情表述，不返回问卷式 open 兜底

#### Scenario: mock 短句「考砸了」对齐

- **WHEN** mock 场景引擎处理整句「考砸了」
- **THEN** 返回含共情/陪伴表述，不返回问卷式 open 兜底语气
