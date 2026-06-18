## Purpose

保证 NPC 跨会话人格一致，并通过 system prompt 约束回复为口语化、像真人微信聊天，避免客服腔与问卷式连环追问。

## Requirements

### Requirement: 人格一致性

系统 SHALL 在每次对话注入稳定 Persona（大五人格、说话风格、价值观、禁忌），使 NPC 跨会话保持同一人格基调。

#### Scenario: System prompt 含人格锚点

- **WHEN** 构建对话 system prompt
- **THEN** prompt 包含名字、背景、说话风格、关系阶段与当前情绪语气微调

### Requirement: 口语化回复约束

系统 SHALL 要求 NPC 像真人发微信：1～2 句、先回应具体内容、每轮最多一个问句，禁止客服腔与连环追问。

#### Scenario: 提示词约束

- **WHEN** 生成 system prompt 的回复要求段
- **THEN** 包含禁止堆问号、禁止问卷式连问的明确规则
