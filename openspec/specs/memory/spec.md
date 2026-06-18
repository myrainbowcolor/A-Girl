## Purpose

实现长期陪伴所需的记忆流：情景记忆写入、加权检索注入 prompt，以及定期反思生成高层洞察，支撑「她记得你」的连续感。

## Requirements

### Requirement: 记忆检索打分

系统 SHALL 按相关性、时近性、重要性加权检索 Top-K 记忆注入 prompt。

#### Scenario: 检索相关记忆

- **WHEN** 用户消息与某条历史记忆语义相关
- **THEN** 该记忆可被检索并出现在 prompt 的已知事实段

### Requirement: 情景记忆写入

系统 SHALL 将用户消息沉淀为情景记忆，重要度随情感强度与关键信息 cues 提升。

#### Scenario: 高情感消息

- **WHEN** 用户表达强负面情绪或含生日/面试等关键词
- **THEN** 系统写入较高 importance 的记忆条目

### Requirement: 反思触发

系统 SHALL 在累计足够新记忆后触发反思，生成高层洞察记忆（类型 REFLECTION）。

#### Scenario: 达到反思阈值

- **WHEN** 新记忆数达到配置的 reflection_every_n_memories
- **THEN** 系统调用 LLM（若可用）生成反思并存储
