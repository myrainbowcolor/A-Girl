## Purpose

跨轮分析用户行为、意图、说话方式与思想模式，驱动右栏洞察展示与个性化主动沟通，并支持累积合并避免泛化回退。

## Requirements

### Requirement: 每轮洞察更新

系统 SHALL 在每轮对话后分析用户历史消息，更新 user_behavior、user_intent、user_state、user_speaking_style、user_thought_pattern、user_profile_summary。

#### Scenario: 多轮对话后具体画像

- **WHEN** 用户已发送多条消息且 interaction_count ≥ 3
- **THEN** 洞察面板展示非泛化的说话方式与思想倾向

### Requirement: 跨轮累积

系统 SHALL 合并新旧洞察，避免每轮退回「正常互动/闲聊」等泛化文案。

#### Scenario: 保留更具体的历史描述

- **WHEN** 新分析结果比已存储洞察更泛化
- **THEN** 系统保留已有的具体 speaking_style 或 thought_pattern

### Requirement: 洞察驱动主动沟通

系统 SHALL 根据 proactive_need（follow_up/comfort/celebrate/reconnect）生成个性化主动开场白。

#### Scenario: 情绪低落

- **WHEN** sentiment_ema 低于阈值且 idle 满足洞察触发条件
- **THEN** proactive_need 为 comfort，主动消息体现关怀
