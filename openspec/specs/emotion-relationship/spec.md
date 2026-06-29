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

情感词典分析 SHALL 对整句极简口语（「还好」「还行」「一般」「不知道」「说不清」「说不上」）返回偏负向 sentiment，用于驱动 avatar 与关系评估；长句中含相同子串时 MUST NOT 误触发（仅整句精确匹配）。用户表达想念或好久未见（含「想你」「想念」「好久不见」「好久没聊」等）SHALL 返回温和正向 sentiment（约 0.35～0.45、label「想念」），驱动 avatar 微笑/nod，MUST NOT 误判为纯报喜（sentiment≥0.6 导致大笑 cheer）。

#### Scenario: 整句「不知道」偏负向

- **WHEN** `analyze_lexicon("不知道")`
- **THEN** sentiment < -0.2 且 label 为「偏负向」

#### Scenario: 长句不误判

- **WHEN** `analyze_lexicon("我不知道该怎么办")`
- **THEN** 不因「不知道」子串而强制偏负向（走常规模块匹配）

#### Scenario: 无聊闲聊仍中性

- **WHEN** `analyze_lexicon("好无聊啊")`
- **THEN** sentiment 保持中性，不误判为低落

#### Scenario: 想念句温和正向

- **WHEN** `analyze_lexicon("好久没聊了，有点想你")`
- **THEN** sentiment 在 0.35～0.45 且 label 含「想念」，avatar 倾向微笑/nod 而非大笑 cheer

#### Scenario: 真开心分享仍偏正向

- **WHEN** `analyze_lexicon("今天好开心，考试过了！")`
- **THEN** sentiment > 0.5，可走开心分享分支

### Requirement: 早安寒暄温和正向标注

情感词典分析 SHALL 识别含早安标记（「早呀」「早安」「早上好」「早啊」）且**不含**困倦标记（「困」「困死」「不想起床」「起不来」）的用户消息，返回温和正向 sentiment（约 0.35～0.45、label「寒暄」），用于驱动 avatar 微笑/nod；含困倦标记的早安句 MUST NOT 走此分支。

#### Scenario: 通勤早安偏正向

- **WHEN** `analyze_lexicon("早呀，今天又要上班了")`
- **THEN** sentiment 在 0.35～0.45 且 label 含「寒暄」

#### Scenario: 困倦早安仍偏负向

- **WHEN** `analyze_lexicon("困死了，不想起床")`
- **THEN** sentiment < -0.2，不走寒暄正向分支

#### Scenario: 非早安工作压力保持原逻辑

- **WHEN** `analyze_lexicon("今天要开会")`
- **THEN** 不因本需求误判为寒暄正向

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
