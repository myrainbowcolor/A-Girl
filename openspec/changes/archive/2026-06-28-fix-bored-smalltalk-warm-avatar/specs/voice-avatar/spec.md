## ADDED Requirements

### Requirement: 无聊/社交探问闲聊时温暖表情

当用户发送无聊摸鱼或社交探问口语且 `user_sentiment` 温和正向（> 0.35）时，系统 SHALL 将 avatar expression 映射为「微笑」、animation 为 nod，而非平静 idle。

#### Scenario: bored_smalltalk 首轮微笑

- **WHEN** 用户说「好无聊啊」
- **THEN** avatar expression 为「微笑」或「大笑」，animation 为 nod 或 cheer（非平静 idle）

#### Scenario: bored_smalltalk 探问微笑

- **WHEN** 用户说「你在干嘛」
- **THEN** avatar expression 为「微笑」，animation 为 nod（非平静 idle）

#### Scenario: 封闭极简句仍平静或 comfort

- **WHEN** 用户说「嗯」
- **THEN** avatar 不因本需求误判为微笑
