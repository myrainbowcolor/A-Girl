## ADDED Requirements

### Requirement: 早安寒暄时温暖表情

当用户发送无困倦标记的早安寒暄且 `user_sentiment` 温和正向（> 0.35）时，系统 SHALL 将 avatar expression 映射为「微笑」、animation 为 nod，而非平静 idle。

#### Scenario: morning_checkin 首轮微笑

- **WHEN** 用户说「早呀，今天又要上班了」
- **THEN** avatar expression 为「微笑」或「大笑」，animation 为 nod 或 cheer（非平静 idle）

#### Scenario: 困倦早安仍 comfort

- **WHEN** 用户说「困死了，不想起床」
- **THEN** avatar 仍为担心/comfort 类表现
