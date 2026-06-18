## ADDED Requirements

### Requirement: 主动消息口语化

系统 SHALL 使 welcome、idle、emotion 及规则生成的 insight 主动开场白口语化、像真人微信，每轮最多一个问句，禁止「最近怎么样？随便说点也行」类问卷式连环引导。

#### Scenario: 长时间未互动 idle 开场

- **WHEN** 触发 idle 主动消息
- **THEN** 文案为 1～2 句口语化问候，全句至多一个问号，不含叠问或「随便说点小事也行」类第二引导

#### Scenario: 洞察 comfort 规则模板

- **WHEN** mock/规则路径生成 comfort 类主动消息
- **THEN** 先表达陪伴意愿，至多一个轻问句，不说教、不连环追问
