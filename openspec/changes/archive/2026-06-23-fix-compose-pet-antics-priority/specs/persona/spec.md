## MODIFIED Requirements

### Requirement: 口语化回复约束

系统 SHALL 要求 NPC 像真人发微信：1～2 句、先回应具体内容、每轮最多一个问句，禁止客服腔与连环追问。续聊宠物日常趣事时 MUST 先接住具体行为（如打翻杯子），再表达同频开心，禁止仅用泛化报喜句式敷衍。生产路径 `compose_contextual_reply`（scene_first 编排优先调用）与 `mock.py` 场景分支 MUST 行为一致，不得因「哈哈」等开心语气词抢先命中通用报喜模板而跳过宠物语境。

#### Scenario: 提示词约束

- **WHEN** 生成 system prompt 的回复要求段
- **THEN** 包含禁止堆问号、禁止问卷式连问的明确规则

#### Scenario: 宠物捣蛋续聊

- **WHEN** 用户上文已提及宠物（如猫名），本轮用「它」描述捣蛋或日常趣事（含「哈哈」等开心语气）
- **THEN** mock/compose 回复提及宠物行为或名字，而非仅泛化「听你开心我也开心」

#### Scenario: 生产路径 compose 宠物续聊

- **WHEN** `orchestrator` 以 `scene_first` 策略处理「它今天又把杯子打翻了哈哈」，且近期用户话含「叫橘子的猫」
- **THEN** `compose_contextual_reply` 返回含「橘子」「打翻」或「杯子」的回复，不返回「发生什么好事啦」类泛化报喜句
