## MODIFIED Requirements

### Requirement: 极简口语整句情感标注

情感词典分析 SHALL 对整句极简口语（「还好」「还行」「一般」「不知道」「说不清」「说不上」）返回偏负向 sentiment，用于驱动 avatar 与关系评估；长句中含相同子串时 MUST NOT 误触发（仅整句精确匹配）。用户表达想念或好久未见（含「想你」「想念」「好久不见」「好久没聊」等）SHALL 返回温和正向 sentiment（约 0.35～0.45、label「想念」），驱动 avatar 微笑/nod，MUST NOT 误判为纯报喜（sentiment≥0.6 导致大笑 cheer）。

#### Scenario: 想念句温和正向

- **WHEN** `analyze_lexicon("好久没聊了，有点想你")`
- **THEN** sentiment 在 0.35～0.45 且 label 含「想念」，avatar 倾向微笑/nod 而非大笑 cheer

#### Scenario: 真开心分享仍偏正向

- **WHEN** `analyze_lexicon("今天好开心，考试过了！")`
- **THEN** sentiment > 0.5，可走开心分享分支
