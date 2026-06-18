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
