## ADDED Requirements

### Requirement: 无聊/社交探问闲聊温和正向标注

情感词典分析 SHALL 识别无聊摸鱼与社交探问口语（如「好无聊啊」「你在干嘛」「在干嘛」），返回温和正向 sentiment（约 0.35～0.45、label「闲聊」），用于驱动 avatar 微笑/nod；含明显负面标记（「难过」「烦」「累」「不想」「郁闷」「低落」「孤独」「落寞」「不想活」等）的同类句 MUST NOT 走此分支。MUST NOT 将「无聊」加入 `_NEGATIVE` 词典。

#### Scenario: 无聊摸鱼偏正向

- **WHEN** `analyze_lexicon("好无聊啊")`
- **THEN** sentiment 在 0.35～0.45 且 label 含「闲聊」

#### Scenario: 社交探问偏正向

- **WHEN** `analyze_lexicon("你在干嘛")`
- **THEN** sentiment 在 0.35～0.45 且 label 含「闲聊」

#### Scenario: 无聊但带负面情绪不走闲聊分支

- **WHEN** `analyze_lexicon("好无聊，心情还是很差")`
- **THEN** sentiment < 0.35，不走无聊社交闲聊分支

#### Scenario: 封闭极简句仍中性或偏负

- **WHEN** `analyze_lexicon("嗯")`
- **THEN** 不因本需求误判为闲聊正向
