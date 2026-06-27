## ADDED Requirements

### Requirement: 轻松正向闲聊温和正向标注

情感词典分析 SHALL 识别含轻松正向闲聊标记的用户消息（如「天气不错」「天气真好」「挺好的电影」「好看的电影」等），返回温和正向 sentiment（约 0.35～0.45、label「闲聊」），用于驱动 avatar 微笑/nod；含明显负面标记（「难过」「烦」「累」「不想」等）的同类句 MUST NOT 走此分支。

#### Scenario: 夸赞天气偏正向

- **WHEN** `analyze_lexicon("今天天气不错")`
- **THEN** sentiment 在 0.35～0.45 且 label 含「闲聊」

#### Scenario: 分享好看电影偏正向

- **WHEN** `analyze_lexicon("刚看完一部挺好的电影")`
- **THEN** sentiment 在 0.35～0.45 且 label 含「闲聊」

#### Scenario: 正向闲聊但带负面情绪不走闲聊分支

- **WHEN** `analyze_lexicon("天气不错但心情还是很差")`
- **THEN** sentiment < 0.35，不走闲聊正向分支

#### Scenario: 普通中性句保持中性

- **WHEN** `analyze_lexicon("今天要开会")`
- **THEN** sentiment 保持中性，不因本需求误判为闲聊正向
