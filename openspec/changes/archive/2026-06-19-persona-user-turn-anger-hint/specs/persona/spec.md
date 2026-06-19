## MODIFIED Requirements

### Requirement: 用户轮次语气侧重

系统 SHALL 在构建 system prompt 时，根据用户本轮消息的情感倾向（复用 `analyze_lexicon`）追加「本轮侧重」语气指引，使 LLM 回复与 avatar/TTS 的多模态共情表现一致。当用户情感为中性或未提供用户文本时，不追加该段。用户愤怒或发泄类表述（含气死、骂我、生气、辞职冲动等）MUST 使用独立于低落倾诉的「发泄/愤怒」侧重，指引先接住火气、陪着听，禁止说教式劝冷静。

#### Scenario: 用户倾诉负面时 prompt 含共情侧重

- **WHEN** 构建 system prompt 且 `user_text` 经词典分析为偏负向（sentiment < -0.3），且不含愤怒发泄关键词
- **THEN** prompt 包含「本轮侧重」段，指引先接住感受、陪伴倾听，而非轻快闲聊

#### Scenario: 用户愤怒发泄时 prompt 含发泄侧重

- **WHEN** 构建 system prompt 且 `user_text` 含愤怒发泄关键词（如「气死」「骂我」「生气」）
- **THEN** prompt 包含「本轮侧重」段，指引先接住火气、陪着听，不说教、不急着劝「别生气」

#### Scenario: 用户分享好事时 prompt 含同频侧重

- **WHEN** 构建 system prompt 且 `user_text` 经词典分析为偏正向（sentiment > 0.3）
- **THEN** prompt 包含「本轮侧重」段，指引真心替 ta 高兴、语气跟着亮起来

#### Scenario: 中性用户句不追加侧重

- **WHEN** 构建 system prompt 且 `user_text` 情感为中性或为空
- **THEN** prompt 不包含「本轮侧重」段，保持原有「语气微调」不变
