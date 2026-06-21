## Purpose

用 PAD 连续情绪空间与亲密度关系模型，使 NPC 情绪与关系随用户互动演化，并驱动语气、UI 与数字人表现。

## Requirements

### Requirement: PAD 情绪评估

系统 SHALL 根据用户消息更新 NPC 的 pleasure/arousal/dominance，并映射为可读情绪标签供 UI 与语气使用。

#### Scenario: 负面消息降低愉悦度

- **WHEN** 用户表达烦恼、压力或难过
- **THEN** pleasure 趋向负值，关系与 avatar 反映共情倾向

### Requirement: 关系阶段

系统 SHALL 根据亲密度 affinity 计算关系阶段（陌生/熟悉/朋友/亲密），并影响 prompt 中的关系指引。

#### Scenario: 亲密度提升

- **WHEN** 多轮正向互动累积 affinity
- **THEN** 关系阶段可升级，语气指引更亲昵

### Requirement: 关系归纳

系统 SHALL 按间隔刷新关系健康度与 LLM/规则关系摘要，供 prompt 与 UI 展示。

#### Scenario: 定期刷新摘要

- **WHEN** interaction_count 达到 relationship_summary_every_n 倍数
- **THEN** 系统更新 relationship_summary 与 health_score

### Requirement: 极简口语整句情感标注

情感词典分析 SHALL 对整句极简口语（「还好」「还行」「一般」「不知道」「说不清」「说不上」）返回偏负向 sentiment，用于驱动 avatar 与关系评估；长句中含相同子串时 MUST NOT 误触发（仅整句精确匹配）。

#### Scenario: 整句「不知道」偏负向

- **WHEN** `analyze_lexicon("不知道")`
- **THEN** sentiment < -0.2 且 label 为「偏负向」

#### Scenario: 长句不误判

- **WHEN** `analyze_lexicon("我不知道该怎么办")`
- **THEN** 不因「不知道」子串而强制偏负向（走常规模块匹配）

#### Scenario: 无聊闲聊仍中性

- **WHEN** `analyze_lexicon("好无聊啊")`
- **THEN** sentiment 保持中性，不误判为低落
