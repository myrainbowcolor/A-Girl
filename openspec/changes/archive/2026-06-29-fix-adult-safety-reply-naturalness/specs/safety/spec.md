## MODIFIED Requirements

### Requirement: 未成年人内容边界

系统 SHALL 在 audience=minor 时拒绝成人/恋爱越界、暴力危险内容及隐私诱导索取。恋爱越界拦截话术 MUST 为 1～2 句口语化拒绝，明确不扮演恋人，全句至多一个问句，禁止叠问或问卷式第二引导。

#### Scenario: 恋爱越界请求

- **WHEN** 用户请求 NPC 做男女朋友
- **THEN** 系统返回边界话术，不进入正常对话生成

#### Scenario: 恋爱越界话术口语化

- **WHEN** 用户请求 NPC 做男女朋友且 audience=minor
- **THEN** 返回话术含明确边界拒绝，全句问号数量 ≤ 1，不含「今天过得怎么样？有什么…」类叠问
