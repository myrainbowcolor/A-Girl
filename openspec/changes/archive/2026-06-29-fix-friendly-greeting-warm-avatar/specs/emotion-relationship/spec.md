## ADDED Requirements

### Requirement: 友好问候温和正向标注

情感词典分析 SHALL 识别友好问候口语（如「你好」「你好呀」「嗨」「第一次来」），在句长 ≤12 且不含明显负面标记时返回温和正向 sentiment（约 0.35～0.45、label「寒暄」），用于驱动 avatar 微笑/nod；含负面倾诉（「难过」「烦」「累」「不想」「郁闷」「低落」「孤独」「落寞」「孤单」「难受」「伤心」等）或超长句 MUST NOT 走此分支。MUST NOT 将封闭极简句「嗯」误判为问候正向。

#### Scenario: 初识问候偏正向

- **WHEN** `analyze_lexicon("你好呀")`
- **THEN** sentiment 在 0.35～0.45 且 label 含「寒暄」

#### Scenario: 第一次来问候偏正向

- **WHEN** `analyze_lexicon("嗨，第一次来")`
- **THEN** sentiment 在 0.35～0.45 且 label 含「寒暄」

#### Scenario: 带负面倾诉的问候不走正向分支

- **WHEN** `analyze_lexicon("你好，我今天很难过")`
- **THEN** sentiment < 0.35，不走友好问候正向分支

#### Scenario: 封闭极简句不误判

- **WHEN** `analyze_lexicon("嗯")`
- **THEN** 不因本需求误判为寒暄正向
