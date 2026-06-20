## ADDED Requirements

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
