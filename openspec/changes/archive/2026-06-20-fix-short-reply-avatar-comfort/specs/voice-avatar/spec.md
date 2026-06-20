## ADDED Requirements

### Requirement: 整句极简低落口语触发安慰表情

当用户整句消息仅为极简口语（如「还好」「还行」「一般」「不知道」「说不清」「说不上」）时，系统 SHALL 将 `user_sentiment` 判为偏负向（< -0.2），使 `emotion_to_avatar` 展示担心/comfort 类表情与动作，与陪伴式话术一致。

#### Scenario: 用户说「不知道」时 avatar 安慰

- **WHEN** 用户整句输入为「不知道」
- **THEN** avatar expression 为「担心」或「难过」，animation 为 comfort

#### Scenario: 用户说「还好」时 avatar 轻微关切

- **WHEN** 用户整句输入为「还好」
- **THEN** avatar 倾向担心/comfort，而非平静 idle
