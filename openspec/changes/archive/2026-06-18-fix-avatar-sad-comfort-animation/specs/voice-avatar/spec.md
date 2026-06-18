## MODIFIED Requirements

### Requirement: 情绪驱动 Avatar

系统 SHALL 根据 PAD 情绪与用户情感映射 AvatarCue（expression/intensity/animation），随 chat 响应下发。当愉悦度 ≤ -0.3 时，无论激活度高低，animation MUST 倾向 comfort 类安抚动作（而非静止 idle），使口播安慰与肢体表现一致。

#### Scenario: 用户低落时安慰表情

- **WHEN** 用户情感偏负面
- **THEN** avatar 倾向 comfort/worry 类表情与动作

#### Scenario: NPC 内在低落时仍展现安抚姿态

- **WHEN** NPC 内在 PAD 愉悦度 ≤ -0.3 且激活度较低（难过表情）
- **THEN** avatar animation 为 comfort，与陪伴倾听场景一致
