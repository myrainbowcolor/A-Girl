## MODIFIED Requirements

### Requirement: 用户轮次语气侧重

系统 SHALL 在构建 system prompt 时，根据用户本轮消息的情感倾向（复用 `analyze_lexicon`）追加「本轮侧重」语气指引，使 LLM 回复与 avatar/TTS 的多模态共情表现一致。当用户情感为中性或未提供用户文本时，不追加该段。用户愤怒或发泄类表述（含气死、骂我、生气、辞职冲动等）MUST 使用独立于低落倾诉的「发泄/愤怒」侧重，指引先接住火气、陪着听，禁止说教式劝冷静。用户失眠或反刍类表述（含失眠、睡不着、脑子停不下来、越躺越清醒等）MUST 使用独立于通用负向的「失眠/反刍」侧重，指引先接住烦躁、陪着聊或安静待着，禁止数羊/早睡/助眠建议式说教。用户整句极简 masking/回避口语（「还好」「还行」「一般」「不知道」「说不清」「说不上」）或单字疲惫「累」MUST 使用独立于「封闭边界」的「极简 masking 低落」侧重，指引轻轻接住、耐心陪伴、可轻问一句，禁止问卷连珠炮；真正封闭句（「嗯」「..」「不想说」等）仍走封闭边界侧重。

#### Scenario: 用户倾诉负面时 prompt 含共情侧重

- **WHEN** 构建 system prompt 且 `user_text` 经词典分析为偏负向（sentiment < -0.3），且不含愤怒发泄、失眠反刍或极简 masking 关键词
- **THEN** prompt 包含「本轮侧重」段，指引先接住感受、陪伴倾听，而非轻快闲聊

#### Scenario: 用户愤怒发泄时 prompt 含发泄侧重

- **WHEN** 构建 system prompt 且 `user_text` 含愤怒发泄关键词（如「气死」「骂我」「生气」）
- **THEN** prompt 包含「本轮侧重」段，指引先接住火气、陪着听，不说教、不急着劝「别生气」

#### Scenario: 用户失眠反刍时 prompt 含失眠侧重

- **WHEN** 构建 system prompt 且 `user_text` 含失眠反刍关键词（如「失眠」「睡不着」「脑子停不下来」）
- **THEN** prompt 包含「本轮侧重」段，指引先接住烦躁、陪着聊或安静待着，不给数羊/早睡等助眠建议

#### Scenario: 用户分享好事时 prompt 含同频侧重

- **WHEN** 构建 system prompt 且 `user_text` 经词典分析为偏正向（sentiment > 0.3）
- **THEN** prompt 包含「本轮侧重」段，指引真心替 ta 高兴、语气跟着亮起来

#### Scenario: 中性用户句不追加侧重

- **WHEN** 构建 system prompt 且 `user_text` 情感为中性或为空
- **THEN** prompt 不包含「本轮侧重」段，保持原有「语气微调」不变

#### Scenario: 用户说「还好」时 prompt 含 masking 低落侧重

- **WHEN** 构建 system prompt 且 `user_text` 整句为「还好」「还行」或「一般」
- **THEN** prompt 包含「本轮侧重」段，指引轻轻接住 masking 情绪、耐心陪伴，而非「尊重边界不追问」

#### Scenario: 用户说「不知道」时 prompt 含 masking 低落侧重

- **WHEN** 构建 system prompt 且 `user_text` 整句为「不知道」「说不清」或「说不上」
- **THEN** prompt 包含「本轮侧重」段，指引不逼 ta 想清楚、陪着慢慢理，而非封闭边界侧重

#### Scenario: 用户单字「累」时 prompt 含疲惫共情侧重

- **WHEN** 构建 system prompt 且 `user_text` 整句仅为「累」
- **THEN** prompt 包含「本轮侧重」段，指引接住疲惫、短句体贴，而非封闭边界侧重

#### Scenario: 真正封闭句仍走边界侧重

- **WHEN** 构建 system prompt 且 `user_text` 为「..」「嗯」或含「不想说」「别问」
- **THEN** prompt 包含「本轮侧重」段，指引尊重边界、短句陪伴、禁止追问
