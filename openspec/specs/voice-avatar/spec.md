## Purpose

提供 TTS/STT 语音能力与 PAD 驱动的数字人 Avatar 表现，含颜文字过滤朗读与语音模式下的音画同步。

## Requirements

### Requirement: TTS 按需合成

系统 SHALL 提供 `/api/tts`，将文本合成为音频；朗读前 MUST 过滤 emoji/颜文字（strip_for_tts）。

#### Scenario: 颜文字不朗读

- **WHEN** 回复含颜文字或 emoji
- **THEN** TTS 输入为过滤后的文本，界面仍显示原文

### Requirement: 情绪驱动 Avatar

系统 SHALL 根据 PAD 情绪与用户情感映射 AvatarCue（expression/intensity/animation），随 chat 响应下发。当愉悦度 ≤ -0.3 时，无论激活度高低，animation MUST 倾向 comfort 类安抚动作（而非静止 idle），使口播安慰与肢体表现一致。

#### Scenario: 用户低落时安慰表情

- **WHEN** 用户情感偏负面
- **THEN** avatar 倾向 comfort/worry 类表情与动作

#### Scenario: NPC 内在低落时仍展现安抚姿态

- **WHEN** NPC 内在 PAD 愉悦度 ≤ -0.3 且激活度较低（难过表情）
- **THEN** avatar animation 为 comfort，与陪伴倾听场景一致

### Requirement: 整句极简低落口语触发安慰表情

当用户整句消息仅为极简口语（如「还好」「还行」「一般」「不知道」「说不清」「说不上」）时，系统 SHALL 将 `user_sentiment` 判为偏负向（< -0.2），使 `emotion_to_avatar` 展示担心/comfort 类表情与动作，与陪伴式话术一致。

#### Scenario: 用户说「不知道」时 avatar 安慰

- **WHEN** 用户整句输入为「不知道」
- **THEN** avatar expression 为「担心」或「难过」，animation 为 comfort

#### Scenario: 用户说「还好」时 avatar 轻微关切

- **WHEN** 用户整句输入为「还好」
- **THEN** avatar 倾向担心/comfort，而非平静 idle

### Requirement: 早安寒暄时温暖表情

当用户发送无困倦标记的早安寒暄且 `user_sentiment` 温和正向（> 0.35）时，系统 SHALL 将 avatar expression 映射为「微笑」、animation 为 nod，而非平静 idle。

#### Scenario: morning_checkin 首轮微笑

- **WHEN** 用户说「早呀，今天又要上班了」
- **THEN** avatar expression 为「微笑」或「大笑」，animation 为 nod 或 cheer（非平静 idle）

#### Scenario: 困倦早安仍 comfort

- **WHEN** 用户说「困死了，不想起床」
- **THEN** avatar 仍为担心/comfort 类表现

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

### Requirement: 语音模式音画同步

系统 SHALL 在语音模式下等 TTS 就绪后再展示完整回复文本，避免台词与声音不同步。

#### Scenario: 开语音时不提前流式全文

- **WHEN** 用户开启语音播放
- **THEN** 气泡文本与 TTS 同步呈现
