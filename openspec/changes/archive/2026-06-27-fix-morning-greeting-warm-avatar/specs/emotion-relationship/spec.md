## ADDED Requirements

### Requirement: 早安寒暄温和正向标注

情感词典分析 SHALL 识别含早安标记（「早呀」「早安」「早上好」「早啊」）且**不含**困倦标记（「困」「困死」「不想起床」「起不来」）的用户消息，返回温和正向 sentiment（约 0.35～0.45、label「寒暄」），用于驱动 avatar 微笑/nod；含困倦标记的早安句 MUST NOT 走此分支。

#### Scenario: 通勤早安偏正向

- **WHEN** `analyze_lexicon("早呀，今天又要上班了")`
- **THEN** sentiment 在 0.35～0.45 且 label 含「寒暄」

#### Scenario: 困倦早安仍偏负向

- **WHEN** `analyze_lexicon("困死了，不想起床")`
- **THEN** sentiment < -0.2，不走寒暄正向分支

#### Scenario: 非早安工作压力保持原逻辑

- **WHEN** `analyze_lexicon("上班好累")`
- **THEN** 不因本需求误判为寒暄正向
