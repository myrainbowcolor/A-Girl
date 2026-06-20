## Purpose

让 NPC 像真人一样主动发起互动：事件、洞察、情绪、轻问候与长时间未聊等触发器，配合调度器与 SSE 推送到客户端。

## Requirements

### Requirement: 触发器优先级

系统 SHALL 按优先级评估主动消息：事件到点 > 首次欢迎 > 用户洞察 > 情绪关怀 > 轻问候 > 长时间未互动。

#### Scenario: 首次来访

- **WHEN** 用户尚无对话历史
- **THEN** 系统可投递 welcome 主动问候

#### Scenario: 长时间未互动

- **WHEN** 距上次互动超过 proactive_idle_seconds
- **THEN** 系统可投递 idle 主动消息

### Requirement: 全局冷却

系统 SHALL 在两次主动消息之间 enforce proactive_global_cooldown_seconds，避免刷屏（welcome/event 除外）。

#### Scenario: 冷却期内

- **WHEN** 距上次主动消息不足全局冷却时间
- **THEN** 系统不触发 insight/emotion/warm/idle 类主动消息

### Requirement: 调度与推送

系统 SHALL 支持后台调度器周期性评估，并通过 SSE `/api/stream/{user_id}` 推送主动消息。

#### Scenario: 调度器启用

- **WHEN** AGIRL_PROACTIVE_SCHEDULER_ENABLED=true
- **THEN** 后台线程定期调用 deliver_proactive 并向订阅客户端 publish

### Requirement: 主动消息口语化

系统 SHALL 使 welcome、idle、emotion、事件触发（event）及规则生成的 insight 主动开场白口语化、像真人微信，每轮最多一个问句，禁止「最近怎么样？随便说点也行」类问卷式连环引导。

#### Scenario: 长时间未互动 idle 开场

- **WHEN** 触发 idle 主动消息
- **THEN** 文案为 1～2 句口语化问候，全句至多一个问号，不含叠问或「随便说点小事也行」类第二引导

#### Scenario: 洞察 comfort 规则模板

- **WHEN** mock/规则路径生成 comfort 类主动消息
- **THEN** 先表达陪伴意愿，至多一个轻问句，不说教、不连环追问

#### Scenario: 事件到点 birthday 开场

- **WHEN** 触发 birthday 类事件主动消息
- **THEN** 文案为 1～2 句口语化祝福，全句至多一个问号，不含叠问或问卷式第二引导
