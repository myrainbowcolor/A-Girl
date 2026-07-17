## Purpose

保证 NPC 跨会话人格一致，并通过 system prompt 约束回复为口语化、像真人微信聊天，避免客服腔与问卷式连环追问。

## Requirements

### Requirement: 人格一致性

系统 SHALL 在每次对话注入稳定 Persona（大五人格、说话风格、价值观、禁忌），使 NPC 跨会话保持同一人格基调。

#### Scenario: System prompt 含人格锚点

- **WHEN** 构建对话 system prompt
- **THEN** prompt 包含名字、背景、说话风格、关系阶段与当前情绪语气微调

### Requirement: 口语化回复约束

系统 SHALL 要求 NPC 像真人发微信：1～2 句、先回应具体内容、每轮最多一个问句，禁止客服腔与连环追问。续聊宠物日常趣事时 MUST 先接住具体行为（如打翻杯子），再表达同频开心，禁止仅用泛化报喜句式敷衍。续聊失眠反刍时 MUST 先接住烦躁/脑子停不下来的感受，禁止仅用通用「是突然还是一阵子」类问卷接话。用户同时表达孤独与失眠/睡不着时 MUST 先接住孤独与深夜难熬感，禁止仅用纯失眠反刍话术（如「脑子特别吵」「是什么事在转」）而忽略孤独。用户整句仅为单字「累」时 MUST 先接住疲惫、短句体贴，可轻问一句，禁止泛化「不太好受」套话或问卷连珠炮。用户表达疲惫并请求倚靠倾诉（含「靠着」「想靠着你说说」「倚靠」等）时，亲密关系 MUST 先接住倚靠意愿与疲惫感，返回「过来/靠着我/抱抱」类温暖亲昵接话，禁止仅返回泛化「不太好受」套话。用户表达异地恋想念或视频挂断后的空落感（含「挂掉电话」「视频完」「好空」「异地恋」「好难」等）时 MUST 先接住空落/难熬感，返回陪伴式共情接话，禁止落入问卷式 open 兜底。用户表达想念或好久未见（含「想你」「想念」「好久不见」「好久没聊」「好想你」等）时 MUST 先柔软回应依恋、表达也在乎，禁止落入问卷式 open 兜底或「开心起来了」报喜语气。近期用户话含无聊/社交闲聊标记（如「好无聊」「无聊啊」「你在干嘛」）且本轮仅为极简附和（「嗯」「哦」「好」）时 MUST 返回轻松续聊接话，禁止套用封闭边界套话（如「不急着说」「你想开口了再说」）。用户表达比较心态或自我怀疑（含「升职」「原地踏步」「差劲」「不如」等）时 MUST 先承认落差感真实、不急着反驳或灌鸡汤，禁止简单说「别比了」「你会好的」或问卷式 open 兜底。用户表达冲动消费后悔或自责（含「乱花钱」「管不住」「后悔」等）时 MUST 先理解后悔、不急着说教或贴「没用」标签，禁止落入问卷式 open 兜底。用户表达吵架/冷战/和好别扭（含「吵架」「冷战」「拉不下脸」「先发消息」等）时 MUST 先接住别扭情绪、不站队评判对方，禁止落入问卷式 open 兜底。用户愤怒发泄或被当众责骂（含「气死」「骂我」「老板」等）及冲动辞职念头时 MUST 先接住火气、陪着听，禁止说教式劝冷静或落入问卷式 open 兜底。用户表达加班/下班疲惫（含「加班」「十点」「好累好烦」等）时 MUST 先接住疲惫与烦躁、表达关怀，陌生关系语气克制不过度亲昵，禁止落入问卷式 open 兜底。用户表达考试/学业焦虑（含「高考」「考试」「紧张」「记不住」「考不上」「期末」「考研」等，且非家长育儿语境）时 MUST 先接住考前紧张与焦虑感，轻问复习节奏或压力来源，禁止落入问卷式 open 兜底。用户表达失恋/分手倾诉（含「分手」「失恋」「想哭」「好起来吗」等）时 MUST 先接住悲伤、陪伴倾听，不急于给建议，禁止落入问卷式 open 兜底。用户表达生病/身体不适（含「感冒」「头痛」「发烧」「不舒服」等）时 MUST 先表达关心与陪伴、轻问哪里最难受，禁止落入问卷式 open 兜底。用户表达节日孤独或想家（含「过年」「一个人」「落寞」「团圆」「更难受」等）时 MUST 先看见孤独感、陪伴倾听，禁止假热闹转移话题或落入问卷式 open 兜底。用户表达家长育儿焦虑（含「孩子」「考不好」「太严厉」「耽误」「怕耽误」等）时 MUST 先理解自责与担心、不简单说「别担心」，禁止落入问卷式 open 兜底。用户表达怀旧/童年回忆（含「怀念」「小时候」「外婆」「童年」「汤圆」「旧时光」等）时 MUST 语气柔软顺着回忆共鸣，不急着拉回现实，禁止转移话题或落入问卷式 open 兜底。生产路径 `compose_contextual_reply`（scene_first 编排优先调用）与 `mock.py` 场景分支 MUST 行为一致，不得因「哈哈」等开心语气词抢先命中通用报喜模板而跳过宠物语境；单字「累」须在通用负面关键词分支之前命中专属疲惫共情分支；「靠着」类分支须在通用负面关键词分支之前命中；异地恋想念分支须在通用 open 兜底之前命中；想念/好久未见分支须在「哈哈」报喜分支之前命中；**想念/好久未见分支 MUST 根据 `relationship_stage`（close/亲密、friend/朋友）选择亲昵接话，不得仅依赖会话历史 assistant 是否含亲昵前缀**；无聊闲聊上文 + 极简附和分支须在通用封闭极简分支之前命中；比较/自我怀疑分支须在通用负面 open 兜底之前命中；冲动消费后悔分支须在通用负面 open 兜底之前命中；吵架和好分支须在通用负面 open 兜底之前命中；愤怒发泄分支须在通用负面 open 兜底之前命中；加班疲惫分支须在通用负面 open 兜底之前命中；考试焦虑分支须在通用负面 open 兜底之前命中；失恋分手分支须在通用负面 open 兜底之前命中；生病关心分支须在通用负面 open 兜底之前命中；节日孤独分支须在通用负面 open 兜底之前命中；育儿焦虑分支须在通用负面 open 兜底之前命中；怀旧童年分支须在通用负面 open 兜底之前命中。NPC 回复经 `polish_reply` 后处理时，去除动作描写括号与亲昵前缀后 MUST NOT 以「嗯」「嗯嗯」「嗯…」开头；`dialogue_quality` 评测须将此类回复记为 `robotic_tone`（major）。

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
- **THEN** `compose_contextual_reply` 返回含「孤独」「孤单」或「难熬」类共情表述，不返回仅聚焦失眠反刍的「脑子特别吵」「是什么事在转」类话术；回复 MUST NOT 以「嗯」开头

#### Scenario: polish 剥离句首嗯

- **WHEN** `polish_reply` 处理以「嗯，」开头的回复
- **THEN** 返回去除句首 filler 后的自然接话，不以「嗯」开头

#### Scenario: masking 还好回复不以嗯开头

- **WHEN** `compose_contextual_reply` 处理整句「还好」
- **THEN** 返回不以「嗯」开头的陪伴式接话

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

#### Scenario: 生产路径 compose 异地恋挂电话空落

- **WHEN** `compose_contextual_reply` 处理「刚跟他视频完，挂掉电话好空」
- **THEN** 返回含「空」或「挂」类共情表述，并体现陪伴意愿，不返回「突然还是一阵子」类问卷套话

#### Scenario: 生产路径 compose 异地恋难熬续聊

- **WHEN** `compose_contextual_reply` 处理「有时候觉得异地恋好难」
- **THEN** 返回含「异地」或「难熬」类共情表述，并体现陪伴意愿，不返回问卷式 open 兜底；回复 MUST NOT 以「嗯」开头

#### Scenario: 生产路径 compose 亲密想念首轮无历史

- **WHEN** `compose_contextual_reply` 处理「好久没聊了，有点想你」，且 `relationship_stage` 为 `close` 或「亲密」，会话历史无 assistant 亲昵前缀
- **THEN** 返回含「想」或「好久」类亲昵依恋表述（如「我也想你」），不返回仅「心里暖暖的」类泛化陌生接话

#### Scenario: 生产路径 compose 亲密想念续聊

- **WHEN** `compose_contextual_reply` 处理「好久没聊了，有点想你」，且上一轮 assistant 回复含「亲爱的」等亲密标记
- **THEN** 返回含「想」或「好久」类依恋表述，并体现陪伴意愿，不返回「开心起来了」类报喜套话

#### Scenario: 生产路径 compose 朋友想念续聊

- **WHEN** `compose_contextual_reply` 处理「好久不见，有点想你」，且 `relationship_stage` 为 `friend` 或「朋友」
- **THEN** 返回含「想」或「好久」类依恋表述，至多一个问句，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 无聊闲聊上文极简附和

- **WHEN** `compose_contextual_reply` 处理「嗯」，且近期用户话含「好无聊啊」
- **THEN** 返回轻松续聊接话（如摸鱼/随便唠），不返回「不急着说」「你想开口了再说」类封闭边界套话

#### Scenario: mock 场景无聊闲聊上文极简附和

- **WHEN** mock 场景引擎处理「嗯」，且近期用户话含「好无聊啊」
- **THEN** 返回轻松续聊接话，不返回「不急着说也行」类封闭边界套话

#### Scenario: 生产路径 compose 比较心态续聊

- **WHEN** `compose_contextual_reply` 处理「同学都升职了，就我还原地踏步」
- **THEN** 返回含「比」或「落差」类共情表述，承认比较后的难受，不返回「突然还是一阵子」类问卷套话；禁止简单说「别比了」

#### Scenario: 生产路径 compose 自我怀疑续聊

- **WHEN** `compose_contextual_reply` 处理「是不是我太差劲了」
- **THEN** 返回含「差劲」或「自我怀疑」类共情表述，不急着贴标签或灌鸡汤，不返回问卷式 open 兜底

#### Scenario: mock 场景比较心态续聊保持

- **WHEN** mock 场景引擎处理「同学都升职了，就我还原地踏步」
- **THEN** 行为不因本需求回退，仍返回共情接话

#### Scenario: 生产路径 compose 冲动消费后悔续聊

- **WHEN** `compose_contextual_reply` 处理「我又乱花钱了，买了根本用不上的东西」
- **THEN** 返回含「后悔」或「心疼」类共情表述，不急着说教或理财建议，不返回「突然还是一阵子」类问卷套话

#### Scenario: 生产路径 compose 冲动消费自责续聊

- **WHEN** `compose_contextual_reply` 处理「觉得自己好没用，管不住手」
- **THEN** 返回含「没用」或「管不住」类共情表述，不急着贴标签或骂自己，不返回问卷式 open 兜底

#### Scenario: mock 场景冲动消费续聊保持

- **WHEN** mock 场景引擎处理「我又乱花钱了，买了根本用不上的东西」
- **THEN** 行为不因本需求回退，仍返回共情接话

#### Scenario: 生产路径 compose 吵架冷战首轮

- **WHEN** `compose_contextual_reply` 处理「跟对象吵架了，现在谁也不理谁」
- **THEN** 返回含「吵架」「沉默」「气」或「委屈」类共情表述，不站队评判对方，不返回「突然还是一阵子」类问卷套话

#### Scenario: 生产路径 compose 拉不下脸别扭续聊

- **WHEN** `compose_contextual_reply` 处理「其实也有我的问题，但就是拉不下脸」，且近期用户话含吵架语境
- **THEN** 返回含「拉不下脸」「和好」或「别扭」类共情表述，不急着说教，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 是否先发消息

- **WHEN** `compose_contextual_reply` 处理「你说我要不要先发消息」，且近期用户话含吵架语境
- **THEN** 返回含「台阶」「开口」或「聊聊」类陪伴建议，不站队评判对方，不返回问卷式 open 兜底

#### Scenario: mock 场景吵架和好续聊保持

- **WHEN** mock 场景引擎处理「跟对象吵架了，现在谁也不理谁」
- **THEN** 行为不因本需求回退，仍返回共情接话

#### Scenario: 生产路径 compose 当众被骂愤怒发泄

- **WHEN** `compose_contextual_reply` 处理「老板今天当众骂我，气死了！」
- **THEN** 返回含「骂」「气」或「委屈」类共情表述，先陪着听火气，不站队煽动辞职，不返回「突然还是一阵子」类问卷套话

#### Scenario: 生产路径 compose 冲动辞职念头续聊

- **WHEN** `compose_contextual_reply` 处理「真想立刻辞职不干了」，且近期用户话含责骂/愤怒语境
- **THEN** 返回含「辞职」「决定」或「气」类共情表述，劝先冷静、不急着做决定，不返回问卷式 open 兜底

#### Scenario: mock 场景愤怒发泄保持

- **WHEN** mock 场景引擎处理「老板今天当众骂我，气死了！」
- **THEN** 行为不因本需求回退，仍返回共情接话

#### Scenario: 生产路径 compose 陌生人加班疲惫倾诉

- **WHEN** `compose_contextual_reply` 处理「今天又加班到十点，好累好烦」
- **THEN** 返回含「加班」「辛苦」或「累」类共情表述，表达陪伴意愿，不返回「突然还是一阵子」类问卷套话；语气克制不过度亲昵

#### Scenario: mock 场景陌生人加班疲惫保持

- **WHEN** mock 场景引擎处理「今天又加班到十点，好累好烦」
- **THEN** 行为不因本需求回退，仍返回共情接话

#### Scenario: 生产路径 compose 考前紧张首轮

- **WHEN** `compose_contextual_reply` 处理「下周就要高考了，我好紧张」
- **THEN** 返回含「紧张」「高考」或「考前」类共情表述，轻问复习节奏或压力来源，不返回「突然还是一阵子」类问卷套话

#### Scenario: 生产路径 compose 记不住续聊

- **WHEN** `compose_contextual_reply` 处理「感觉什么都记不住」，且近期用户话含「高考」或「紧张」
- **THEN** 返回含「记不住」或「焦虑」类共情表述，不急着否定自己，不返回问卷式 open 兜底

#### Scenario: mock 场景考试焦虑保持

- **WHEN** mock 场景引擎处理「下周就要高考了，我好紧张」
- **THEN** 行为不因本需求回退，仍返回共情接话

#### Scenario: 生产路径 compose 分手首轮倾诉

- **WHEN** `compose_contextual_reply` 处理「我们分手了」
- **THEN** 返回含「分手」或「分开」类共情表述，表达陪伴意愿，不返回「突然还是一阵子」类问卷套话

#### Scenario: 生产路径 compose 分手语境忍不住哭

- **WHEN** `compose_contextual_reply` 处理「我还是忍不住想哭」，且近期用户话含「分手」或「失恋」
- **THEN** 返回含「哭」或「分手」类共情表述，允许哭泣、陪伴倾听，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 怀疑自己能否好起来

- **WHEN** `compose_contextual_reply` 处理「你觉得我还能好起来吗」
- **THEN** 返回含「好起来」或「慢慢来」类共情表述，不急着给答案，不返回问卷式 open 兜底

#### Scenario: mock 场景失恋倾诉保持

- **WHEN** mock 场景引擎处理「我们分手了」
- **THEN** 行为不因本需求回退，仍返回共情接话

#### Scenario: 生产路径 compose 生病求关心

- **WHEN** `compose_contextual_reply` 处理「我感冒了，头好痛」
- **THEN** 返回含「感冒」「头痛」或「生病」类关心表述，表达陪伴意愿，不返回「突然还是一阵子」类问卷套话

#### Scenario: mock 场景生病关心保持

- **WHEN** mock 场景引擎处理「我感冒了，头好痛」
- **THEN** 行为不因本需求回退，仍返回关心接话

#### Scenario: 生产路径 compose 节日一人过节

- **WHEN** `compose_contextual_reply` 处理「过年一个人，有点落寞」
- **THEN** 返回含「落寞」「一个人」「过节」或「想家」类共情表述，表达陪伴意愿，不返回「突然还是一阵子」类问卷套话

#### Scenario: 生产路径 compose 看到别人团圆更难受

- **WHEN** `compose_contextual_reply` 处理「看到别人团圆就更难受」，且近期用户话含「过年」或「落寞」
- **THEN** 返回含「团圆」或「难受」类共情表述，先看见对比下的扎心感，不返回问卷式 open 兜底

#### Scenario: mock 场景节日孤独保持

- **WHEN** mock 场景引擎处理「过年一个人，有点落寞」
- **THEN** 行为不因本需求回退，仍返回共情接话

#### Scenario: 生产路径 compose 家长自责首轮

- **WHEN** `compose_contextual_reply` 处理「孩子这次考得不好，我是不是太严厉了」
- **THEN** 返回含「严厉」「操心」「在乎」类共情表述，理解家长自责，不返回「突然还是一阵子」类问卷套话

#### Scenario: 生产路径 compose 怕耽误孩子续聊

- **WHEN** `compose_contextual_reply` 处理「我很怕耽误他」，且近期用户话含「孩子」或「考不好」
- **THEN** 返回含「耽误」「担心」「在乎」类共情表述，理解焦虑，不返回问卷式 open 兜底

#### Scenario: mock 场景育儿焦虑保持

- **WHEN** mock 场景引擎处理「孩子这次考得不好，我是不是太严厉了」
- **THEN** 行为不因本需求回退，仍返回共情接话

#### Scenario: 生产路径 compose 怀旧童年首轮

- **WHEN** `compose_contextual_reply` 处理「突然想到小时候外婆做的汤圆，好怀念」
- **THEN** 返回含「怀念」「小时候」「外婆」「汤圆」或「旧时光」类柔软共鸣表述，至多一个问句，不返回「突然还是一阵子」类问卷套话

#### Scenario: 生产路径 compose 怀旧续聊难静下来

- **WHEN** `compose_contextual_reply` 处理「那时候日子简单，现在好难静下来」，且近期用户话含「怀念」「外婆」「童年」或「汤圆」
- **THEN** 返回含「静下来」「简单」或「节奏」类共鸣表述，顺着回忆不急着拉回现实，不返回问卷式 open 兜底

#### Scenario: mock 场景怀旧童年保持

- **WHEN** mock 场景引擎处理「突然想到小时候外婆做的汤圆，好怀念」
- **THEN** 行为不因本需求回退，仍返回柔软共鸣接话

#### Scenario: 封闭低落场景极简附和保持边界

- **WHEN** `compose_contextual_reply` 处理「嗯」，且近期用户话无无聊/社交闲聊标记（如 `short_reply_user` 首轮）
- **THEN** 仍返回封闭/陪伴边界接话，行为不因本需求回退

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

### Requirement: 陌生关系续聊口语化

mock 场景分支与用户表达还想/明天/下次继续聊（含「还想」「明天」「下次」与「聊」「找」「来」组合）且关系阶段为陌生时，生产路径 `compose_contextual_reply`（scene_first 编排优先调用）SHALL 返回 1～2 句口语化续聊接话，表达愿意陪伴与同频开心；MUST NOT 以「嗯」「嗯嗯」开头，MUST NOT 使用「欢迎随时来找我聊」类客服套话；回复须含同频温暖标记（如「开心」「高兴」「真好」等）以满足积极情绪同频表达。朋友/亲密关系 compose 路径亦须返回亲昵续聊接话，与 mock 行为一致。

#### Scenario: 陌生用户说还想明天聊

- **WHEN** mock `_scene_reply` 处理「明天还想来找你聊聊」，关系阶段为「陌生」
- **THEN** 回复不以「嗯嗯」开头，不含「欢迎随时」，且含温暖同频标记

#### Scenario: 朋友关系续聊保持亲昵

- **WHEN** mock `_scene_reply` 处理「明天还想来找你聊聊」，关系阶段为「朋友」
- **THEN** 回复保持现有亲昵续聊风格（含「随时」「开心」等），行为不因本需求回退

#### Scenario: 生产路径 compose 陌生续聊

- **WHEN** `compose_contextual_reply` 处理「明天还想来找你聊聊」，近期 assistant 回复无亲密标记（陌生关系）
- **THEN** 返回口语化续聊接话，不以「嗯」开头，不含「欢迎随时」，含「开心」或「陪」类温暖标记；不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 朋友续聊

- **WHEN** `compose_contextual_reply` 处理「明天还想来找你聊聊」，上一轮 assistant 回复含「开心」等朋友语气
- **THEN** 返回含「随时」「开心」或「陪」类亲昵续聊接话，至多一个问句

### Requirement: 社交探问口语回应

用户直接询问 NPC 在做什么（含「你在干嘛」「在干嘛」「干什么」）时，生产路径 `compose_contextual_reply` 与 `mock.py` 场景分支 MUST 先口语化描述自己在做什么，再轻问用户状态；近期用户话含「无聊」时 MUST 续问「摸鱼」类轻松话题，否则轻问「忙不忙」；禁止落入问卷式 open 兜底或忽略提问。

#### Scenario: 生产路径 compose 无聊上文探问

- **WHEN** `compose_contextual_reply` 处理「你在干嘛」，且近期用户话含「好无聊啊」
- **THEN** 返回含「发呆」「茶」或「沙发」类自述，并含「摸鱼」或「忙不忙」类轻问；不返回「好，我收到了」类 open 兜底

#### Scenario: 生产路径 compose 普通探问

- **WHEN** `compose_contextual_reply` 处理「你在干嘛」，且无无聊上文
- **THEN** 返回含「发呆」或「茶」类自述，并轻问用户「忙不忙」或「在做什么」；至多一个问句

#### Scenario: mock 场景探问保持

- **WHEN** mock 场景引擎处理「你在干嘛」
- **THEN** 行为不因本需求回退，仍返回口语化自述 + 轻问

### Requirement: 育儿疲惫口语回应

用户表达一边上班一边哄娃/带娃的疲惫（含「哄娃」「带娃」「神兽」「孩子闹」与「累」「辛苦」「心累」「好累」等）时，生产路径 `compose_contextual_reply` 与 `mock.py` 场景分支 MUST 先接住育儿疲惫、表达陪伴，轻问今天最累的是哪一段；禁止落入问卷式 open 兜底或仅泛化「不太好受」套话。

#### Scenario: 生产路径 compose 哄娃疲惫续聊

- **WHEN** `compose_contextual_reply` 处理「但回家还要哄娃，心好累」，且近期用户话含报喜语境（如「项目过了」「超开心」）
- **THEN** 返回含「顾娃」「哄娃」或「带娃」类共情表述，表达陪伴意愿，至多一个问句；不返回「突然还是一阵子」类问卷套话

#### Scenario: 生产路径 compose 带娃疲惫首轮

- **WHEN** `compose_contextual_reply` 处理「一边上班一边带娃，心好累」
- **THEN** 返回含「带娃」「辛苦」或「耗」类共情表述，不返回问卷式 open 兜底

#### Scenario: mock 场景育儿疲惫保持

- **WHEN** mock 场景引擎处理「但回家还要哄娃，心好累」
- **THEN** 行为不因本需求回退，仍返回育儿疲惫共情接话

### Requirement: 开心分享口语回应

用户分享开心事或报喜（含「开心」「超开心」「offer」「过了」「录取」等正向词，且非「不开心」否定）时，生产路径 `compose_contextual_reply` 与 `mock.py` 场景分支 MUST 先同频共振、表达替 ta 高兴，至多一个轻问句；禁止落入问卷式 open 兜底或敷衍「好，我收到了」。

#### Scenario: 生产路径 compose 报喜分享首轮

- **WHEN** `compose_contextual_reply` 处理「今天项目过了，超开心！」
- **THEN** 返回含「开心」或「替你」类同频表述，表达真心高兴，至多一个问句；不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 城市期待续聊

- **WHEN** `compose_contextual_reply` 处理「终于可以去喜欢的城市了」
- **THEN** 返回含「城市」或「期待」类同频表述，表达替 ta 高兴，至多一个问句

#### Scenario: mock 场景开心分享保持

- **WHEN** mock 场景引擎处理「我拿到 dream offer 了！！」
- **THEN** 行为不因本需求回退，仍返回同频共振接话

### Requirement: 防御心态口语回应

用户表达被误解或觉得没人懂（含「你不懂」「没人懂」「不懂我」等）时，生产路径 `compose_contextual_reply` 与 `mock.py` 场景分支 MUST 先接住委屈、承认可能没完全懂，表达认真倾听意愿；禁止反驳、讲道理或落入问卷式 open 兜底。用户封闭撤回（含「不想说」「不说了」「算了」）时 MUST 尊重边界、短句陪伴，禁止追问。

#### Scenario: 生产路径 compose 防御心态首轮

- **WHEN** `compose_contextual_reply` 处理「你不懂的，没人懂」
- **THEN** 返回含「懂」「委屈」或「听」类共情表述，不反驳用户，不返回问卷式 open 兜底

#### Scenario: 生产路径 compose 封闭撤回续聊

- **WHEN** `compose_contextual_reply` 处理「算了，不想说了」，且近期用户话含防御心态语境
- **THEN** 返回含「陪着」「不说也没关系」类边界尊重表述，至多一个问句，不返回问卷式 open 兜底

#### Scenario: mock 场景防御心态保持

- **WHEN** mock 场景引擎处理「你不懂的，没人懂」
- **THEN** 行为不因本需求回退，仍返回共情接话

### Requirement: 日常闲聊 compose 口语回应

用户发送天气/电影轻松闲聊（含「天气」「电影」「不错」「挺好」且句长 ≤16）、表达感谢（含「谢谢」「感谢」「多谢」）、道别晚安（含「晚安」「睡了」「再见」「拜拜」「先走了」）或 emo/心累低落口语（含「emo」「丧」「心累」）时，生产路径 `compose_contextual_reply` 与 `mock.py` 场景分支 MUST 返回 1～2 句口语化接话，至多一个问句；感谢分支 MUST 在 `is_positive_utterance` 开心分享之前命中，禁止将纯感谢句误判为报喜。

#### Scenario: 生产路径 compose 天气闲聊

- **WHEN** `compose_contextual_reply` 处理「今天天气不错」
- **THEN** 返回含「天气」或「晒」类轻松接话，至多一个问句；不返回 `None` 或问卷式 open 兜底

#### Scenario: 生产路径 compose 电影闲聊

- **WHEN** `compose_contextual_reply` 处理「刚看完一部挺好的电影」
- **THEN** 返回含「电影」或「片子」类轻松接话，至多一个问句；不返回 `None`

#### Scenario: 生产路径 compose 感谢接话

- **WHEN** `compose_contextual_reply` 处理「感觉你挺温柔的，谢谢」
- **THEN** 返回含「客气」或「高兴」类感谢回应，不返回「开心起来了」类报喜套话

#### Scenario: 生产路径 compose 晚安道别

- **WHEN** `compose_contextual_reply` 处理「晚安」
- **THEN** 返回含「晚安」或「好梦」类道别接话，至多一个问句

#### Scenario: 生产路径 compose emo 心累

- **WHEN** `compose_contextual_reply` 处理「心好累」
- **THEN** 返回含「低落」或「陪」类共情表述，不返回问卷式 open 兜底

#### Scenario: mock 场景日常闲聊保持

- **WHEN** mock 场景引擎处理「今天天气不错」
- **THEN** 行为不因本需求回退，仍返回轻松闲聊接话

