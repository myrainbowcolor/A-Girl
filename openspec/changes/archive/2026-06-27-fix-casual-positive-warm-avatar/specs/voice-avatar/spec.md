## ADDED Requirements

### Requirement: 轻松正向闲聊时温暖表情

当用户发送轻松正向闲聊且 `user_sentiment` 温和正向（> 0.35）时，系统 SHALL 将 avatar expression 映射为「微笑」、animation 为 nod，而非平静 idle。

#### Scenario: long_session_warmup 夸赞天气微笑

- **WHEN** 用户说「今天天气不错」
- **THEN** avatar expression 为「微笑」或「大笑」，animation 为 nod 或 cheer（非平静 idle）

#### Scenario: long_session_warmup 分享电影微笑

- **WHEN** 用户说「刚看完一部挺好的电影」
- **THEN** avatar expression 为「微笑」，animation 为 nod（非平静 idle）

#### Scenario: 带负面情绪的闲聊仍 comfort

- **WHEN** 用户说「天气不错但心情还是很差」
- **THEN** avatar 仍为担心/comfort 类表现
