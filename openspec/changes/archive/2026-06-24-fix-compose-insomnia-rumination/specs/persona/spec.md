## MODIFIED Requirements

### Requirement: 口语化回复约束

系统 SHALL 要求 NPC 像真人发微信：1～2 句、先回应具体内容、每轮最多一个问句，禁止客服腔与连环追问。续聊宠物日常趣事时 MUST 先接住具体行为（如打翻杯子），再表达同频开心，禁止仅用泛化报喜句式敷衍。续聊失眠反刍时 MUST 先接住烦躁/脑子停不下来的感受，禁止仅用通用「是突然还是一阵子」类问卷接话。生产路径 `compose_contextual_reply`（scene_first 编排优先调用）与 `mock.py` 场景分支 MUST 行为一致。

#### Scenario: 生产路径 compose 失眠反刍续聊

- **WHEN** `orchestrator` 以 `scene_first` 策略处理「越躺越清醒，好烦」，且近期用户话含失眠/项目焦虑语境
- **THEN** `compose_contextual_reply` 返回含「清醒」「折磨」或「失眠」类共情表述，不返回「突然这样的，还是已经有一阵子了」类通用烦分支句
