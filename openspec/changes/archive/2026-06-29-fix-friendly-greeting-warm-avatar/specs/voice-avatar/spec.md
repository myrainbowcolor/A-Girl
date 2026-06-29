## ADDED Requirements

### Requirement: 友好问候时温暖表情

当用户发送友好问候且 `user_sentiment` 温和正向（> 0.35）时，系统 SHALL 将 avatar expression 映射为「微笑」、animation 为 nod，而非平静 idle。

#### Scenario: stranger_first_greet 微笑

- **WHEN** 用户说「你好呀」
- **THEN** avatar expression 为「微笑」或「大笑」，animation 为 nod 或 cheer（非平静 idle）

#### Scenario: long_session_warmup 初识微笑

- **WHEN** 用户说「嗨，第一次来」
- **THEN** avatar expression 为「微笑」，animation 为 nod（非平静 idle）

#### Scenario: 封闭极简句仍平静或 comfort

- **WHEN** 用户说「嗯」
- **THEN** avatar 不因本需求误判为微笑
