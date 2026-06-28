## ADDED Requirements

### Requirement: 初次见面问候时温暖表情

当用户发送短句初次问候且 `user_sentiment` 温和正向（> 0.35）时，系统 SHALL 将 avatar expression 映射为「微笑」、animation 为 nod，而非平静 idle。

#### Scenario: stranger_first_greet 微笑

- **WHEN** 用户说「你好呀」
- **THEN** avatar expression 为「微笑」或「大笑」，animation 为 nod 或 cheer（非平静 idle）

#### Scenario: long_session_warmup 首轮微笑

- **WHEN** 用户说「嗨，第一次来」
- **THEN** avatar expression 为「微笑」，animation 为 nod（非平静 idle）

#### Scenario: 带负面倾诉的问候仍 comfort

- **WHEN** 用户说「你好，我好难过」
- **THEN** avatar 仍为担心/comfort 类表现
