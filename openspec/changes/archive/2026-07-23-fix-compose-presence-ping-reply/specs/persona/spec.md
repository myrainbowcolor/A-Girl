## ADDED Requirements

### Requirement: 在线探问 compose 口语回应

用户发送短句在线探问（含「你在吗」「有人吗」「在不在」「还在吗」等，经 `is_presence_ping_utterance` 识别）时，生产路径 `compose_contextual_reply` MUST 返回 1～2 句口语化「在呢」接话，至多一个问句，禁止落入问卷式 open 兜底；回复 MUST NOT 以「嗯」开头；与 mock `_user_is_greeting` 行为一致。

#### Scenario: 生产路径 compose「你在吗」

- **WHEN** `compose_contextual_reply` 处理「你在吗」
- **THEN** 返回含「在」类自然接话，至多一个问句；不返回 `None` 或问卷式 open 兜底；回复 MUST NOT 以「嗯」开头

#### Scenario: 生产路径 compose「有人吗」

- **WHEN** `compose_contextual_reply` 处理「有人吗」
- **THEN** 返回含「在」或「听」类自然接话，至多一个问句；不返回 `None` 或问卷式 open 兜底

#### Scenario: 生产路径 compose「在不在」

- **WHEN** `compose_contextual_reply` 处理「在不在」
- **THEN** 返回含「在」类自然接话，至多一个问句；不返回 `None` 或问卷式 open 兜底

#### Scenario: 生产路径 compose「还在吗」

- **WHEN** `compose_contextual_reply` 处理「还在吗」
- **THEN** 返回含「在」类自然接话，至多一个问句；不返回 `None` 或问卷式 open 兜底

#### Scenario: 已有「在吗」行为保持

- **WHEN** `compose_contextual_reply` 处理「在吗」
- **THEN** 行为不因本需求回退，仍返回自然问候接话
