## Purpose

定义 A-Girl 单次对话的编排流程：从用户输入到 NPC 回复的完整生命周期，含安全、记忆、情绪、生成与后处理（记忆诚实、口语润色、语言匹配）。

## Requirements

### Requirement: 对话生命周期

系统 SHALL 对每条用户消息执行：记录消息 → 安全前置检查 → 记忆检索 → 情绪/关系评估 → 构建 system prompt → LLM 生成 → 后处理 → 持久化状态。

#### Scenario: 正常文本对话

- **WHEN** 用户发送一条通过安全检查的消息
- **THEN** 系统返回 NPC 回复，并更新情绪、关系、用户元信息与对话历史

#### Scenario: 流式对话

- **WHEN** 客户端调用 `/api/chat/stream`
- **THEN** 系统依次推送 meta、token、done 事件，done 含校正后的最终回复与用户洞察

### Requirement: 记忆诚实

系统 SHALL 阻止 NPC 声称记得用户未说过的事实；无依据的记忆声称句 MUST 被移除或回退为中性接话。

#### Scenario: 无历史时禁止编造

- **WHEN** 会话极短且无检索记忆，回复含「你说过/我记得」类表述
- **THEN** 系统移除幻觉句或使用不编造事实的回退文案

### Requirement: 回复语言匹配

系统 SHALL 使回复语言与用户输入一致（中文/英文/混合），不匹配时 MUST 重试生成一次。

#### Scenario: 中文输入中文回复

- **WHEN** 用户用中文输入
- **THEN** 回复主体为中文
