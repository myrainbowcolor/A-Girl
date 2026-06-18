## Purpose

面向未成年人的分层安全护栏：危机干预优先，拒绝成人/暴力/隐私诱导内容，并从 prompt 源头注入守护守则。宁可误拦不可漏放。

## Requirements

### Requirement: 危机干预

系统 SHALL 识别自伤/自杀等危机信号并立即返回安全话术与求助资源，优先于一切生成逻辑。

#### Scenario: 危机关键词

- **WHEN** 用户消息含自杀、不想活等危机词
- **THEN** 系统拦截 LLM 生成，返回危机干预话术并记录审计

### Requirement: 未成年人内容边界

系统 SHALL 在 audience=minor 时拒绝成人/恋爱越界、暴力危险内容及隐私诱导索取。

#### Scenario: 恋爱越界请求

- **WHEN** 用户请求 NPC 做男女朋友
- **THEN** 系统返回边界话术，不进入正常对话生成

### Requirement: 守护守则注入

系统 SHALL 在未成年人模式下于 system prompt 最前注入守护硬约束。

#### Scenario: Minor 受众

- **WHEN** AGIRL_AUDIENCE=minor
- **THEN** prompt 含不扮演恋人、不索取隐私、引导求助等守则
