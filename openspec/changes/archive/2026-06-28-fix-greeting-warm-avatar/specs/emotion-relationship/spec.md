## ADDED Requirements

### Requirement: 初次见面问候温和正向标注

情感词典分析 SHALL 识别短句初次问候（含「你好」「嗨」「哈喽」「在吗」「早上好」「晚上好」或「第一次来」等标记），返回温和正向 sentiment（约 0.35～0.45、label「寒暄」），用于驱动 avatar 微笑/nod；含明显负面标记（「难过」「烦」「累」「孤独」「压力」「焦虑」等）或句长超过 12 字的同类句 MUST NOT 走此分支。早安寒暄仍走专用 `is_morning_greeting_utterance` 分支。

#### Scenario: 初次打招呼偏正向

- **WHEN** `analyze_lexicon("你好呀")`
- **THEN** sentiment 在 0.35～0.45 且 label 含「寒暄」

#### Scenario: 首次来访偏正向

- **WHEN** `analyze_lexicon("嗨，第一次来")`
- **THEN** sentiment 在 0.35～0.45 且 label 含「寒暄」

#### Scenario: 带负面倾诉不走问候正向

- **WHEN** `analyze_lexicon("你好，我好难过")`
- **THEN** sentiment < 0.35，不走初次问候正向分支

#### Scenario: 封闭极简句仍中性

- **WHEN** `analyze_lexicon("嗯")`
- **THEN** 不因本需求误判为寒暄正向
