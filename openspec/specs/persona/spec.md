## Purpose

保证 NPC 跨会话人格一致，并通过 system prompt 约束回复为口语化、像真人微信聊天，避免客服腔与问卷式连环追问。

## Requirements

### Requirement: 人格一致性

系统 SHALL 在每次对话注入稳定 Persona（大五人格、说话风格、价值观、禁忌），使 NPC 跨会话保持同一人格基调。

#### Scenario: System prompt 含人格锚点

- **WHEN** 构建对话 system prompt
- **THEN** prompt 包含名字、背景、说话风格、关系阶段与当前情绪语气微调

### Requirement: 口语化回复约束

系统 SHALL 要求 NPC 像真人发微信：1～2 句、先回应具体内容、每轮最多一个问句，禁止客服腔与连环追问。续聊宠物日常趣事时 MUST 先接住具体行为（如打翻杯子），再表达同频开心，禁止仅用泛化报喜句式敷衍。续聊失眠反刍时 MUST 先接住烦躁/脑子停不下来的感受，禁止仅用通用「是突然还是一阵子」类问卷接话。用户同时表达孤独与失眠/睡不着时 MUST 先接住孤独与深夜难熬感，禁止仅用纯失眠反刍话术（如「脑子特别吵」「是什么事在转」）而忽略孤独。用户整句仅为单字「累」时 MUST 先接住疲惫、短句体贴，可轻问一句，禁止泛化「不太好受」套话或问卷连珠炮。用户表达疲惫并请求倚靠倾诉（含「靠着」「想靠着你说说」「倚靠」等）时，亲密关系 MUST 先接住倚靠意愿与疲惫感，返回「过来/靠着我/抱抱」类温暖亲昵接话，禁止仅返回泛化「不太好受」套话。生产路径 `compose_contextual_reply`（scene_first 编排优先调用）与 `mock.py` 场景分支 MUST 行为一致，不得因「哈哈」等开心语气词抢先命中通用报喜模板而跳过宠物语境；单字「累」须在通用负面关键词分支之前命中专属疲惫共情分支；「靠着」类分支须在通用负面关键词分支之前命中。

#### Scenario: 提示词约束

- **WHEN** 生成 system prompt 的回复要求段
- **THEN** 包含禁止堆问号、禁止问卷式连问的明确规则

#### Scenario: 宠物捣蛋续聊

- **WHEN** 用户上文已提及宠物（如猫名），本轮用「它」描述捣蛋或日常趣事（含「哈哈」等开心语气）
- **THEN** mock/compose 回复提及宠物行为或名字，而非仅泛化「听你开心我也开心」

#### Scenario: 生产路径 compose 宠物续聊

- **WHEN** `orchestrator` 以 `scene_first` 策略处理「它今天又把杯子打翻了哈哈」，且近期用户话含「叫橘子的猫」
- **THEN** `compose_contextual_reply` 返回含「橘子」「打翻」或「杯子」的回复，不返回「发生什么好事啦」类泛化报喜句

#### Scenario: 生产路径 compose 失眠反刍续聊

- **WHEN** `orchestrator` 以 `scene_first` 策略处理「越躺越清醒，好烦」，且近期用户话含失眠/项目焦虑语境
- **THEN** `compose_contextual_reply` 返回含「清醒」「折磨」或「失眠」类共情表述，不返回「突然这样的，还是已经有一阵子了」类通用烦分支句

#### Scenario: 生产路径 compose 孤独失眠复合续聊

- **WHEN** `orchestrator` 以 `scene_first` 策略处理「凌晨了还睡不着，有点孤独」
- **THEN** `compose_contextual_reply` 返回含「孤独」「孤单」或「难熬」类共情表述，不返回仅聚焦失眠反刍的「脑子特别吵」「是什么事在转」类话术

#### Scenario: 生产路径 compose 单字疲惫续聊

- **WHEN** `orchestrator` 以 `scene_first` 策略处理整句仅为「累」
- **THEN** `compose_contextual_reply` 返回含「累」「辛苦」或「歇」类疲惫共情表述，不返回「不太好受」类泛化负面套话

#### Scenario: mock 场景单字疲惫续聊

- **WHEN** mock 场景引擎处理整句仅为「累」
- **THEN** 返回含「累」「辛苦」或「歇」类疲惫共情表述，不返回「不太好受」类泛化负面套话

#### Scenario: mock 场景亲密倚靠疲惫续聊

- **WHEN** mock 场景引擎处理「今天过得好累，想靠着你说说」，且关系阶段为亲密
- **THEN** 返回含「靠」「陪」或「抱抱」类亲昵接话，不返回「不太好受」类泛化负面套话

#### Scenario: 生产路径 compose 亲密倚靠疲惫续聊

- **WHEN** `compose_contextual_reply` 处理「今天过得好累，想靠着你说说」，且上一轮 assistant 回复含「亲爱的」等亲密标记
- **THEN** 返回含「靠」「陪」或「抱抱」类亲昵接话，不返回「不太好受」类泛化负面套话

### Requirement: 用户轮次语气侧重

系统 SHALL 在构建 system prompt 时，根据用户本轮消息的情感倾向（复用 `analyze_lexicon`）追加「本轮侧重」语气指引，使 LLM 回复与 avatar/TTS 的多模态共情表现一致。当用户情感为中性或未提供用户文本时，不追加该段。用户愤怒或发泄类表述（含气死、骂我、生气、辞职冲动等）MUST 使用独立于低落倾诉的「发泄/愤怒」侧重，指引先接住火气、陪着听，禁止说教式劝冷静。用户失眠或反刍类表述（含失眠、睡不着、脑子停不下来、越躺越清醒等）MUST 使用独立于通用负向的「失眠/反刍」侧重，指引先接住烦躁、陪着聊或安静待着，禁止数羊/早睡/助眠建议式说教。用户整句极简 masking/回避口语（「还好」「还行」「一般」「不知道」「说不清」「说不上」）或单字疲惫「累」MUST 使用独立于「封闭边界」的「极简 masking 低落」侧重，指引轻轻接住、耐心陪伴、可轻问一句，禁止问卷连珠炮；真正封闭句（「嗯」「..」「不想说」等）仍走封闭边界侧重。用户表达想念或好久未见（含「想你」「想念」「好久不见」「好久没聊」等依恋口语）MUST 使用「想念/依恋」侧重，指引柔软黏人、表达也在乎，禁止套用「开心起来了」「报喜」式语气。用户自我怀疑或比较心态表述（含差劲、没用、自卑、原地踏步、管不住、自我怀疑、跟别人比等）MUST 使用「自我怀疑/比较」侧重，指引先承认落差感真实、不急着反驳或灌鸡汤，禁止简单说「别比了」「你会好的」。

#### Scenario: 用户倾诉负面时 prompt 含共情侧重

- **WHEN** 构建 system prompt 且 `user_text` 经词典分析为偏负向（sentiment < -0.3），且不含愤怒发泄、失眠反刍、极简 masking 或自我怀疑关键词
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

#### Scenario: 用户说想念时 prompt 含依恋侧重

- **WHEN** 构建 system prompt 且 `user_text` 含想念/好久未见关键词（如「好久没聊了，有点想你」）
- **THEN** prompt 包含「本轮侧重」段，指引柔软黏人、表达也在乎，而非开心报喜

#### Scenario: 用户自我怀疑时 prompt 含比较心态侧重

- **WHEN** 构建 system prompt 且 `user_text` 含自我怀疑关键词（如「是不是我太差劲了」「觉得自己好没用」）
- **THEN** prompt 包含「本轮侧重」段，指引先承认落差感、不急着反驳或灌鸡汤，而非通用低落倾听

#### Scenario: 用户比较他人时 prompt 含比较心态侧重

- **WHEN** 构建 system prompt 且 `user_text` 含比较心态关键词（如「同学都升职了，就我还原地踏步」）
- **THEN** prompt 包含「本轮侧重」段，指引理解比较后的自我否定，禁止简单说「别比了」
