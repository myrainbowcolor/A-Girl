## Purpose

提供 TTS/STT 语音能力与 PAD 驱动的数字人 Avatar 表现，含颜文字过滤朗读与语音模式下的音画同步。

## Requirements

### Requirement: TTS 按需合成

系统 SHALL 提供 `/api/tts`，将文本合成为音频；朗读前 MUST 过滤 emoji/颜文字（strip_for_tts）。

#### Scenario: 颜文字不朗读

- **WHEN** 回复含颜文字或 emoji
- **THEN** TTS 输入为过滤后的文本，界面仍显示原文

### Requirement: 情绪驱动 Avatar

系统 SHALL 根据 PAD 情绪与用户情感映射 AvatarCue（expression/intensity/animation），随 chat 响应下发。

#### Scenario: 用户低落时安慰表情

- **WHEN** 用户情感偏负面
- **THEN** avatar 倾向 comfort/worry 类表情与动作

### Requirement: 语音模式音画同步

系统 SHALL 在语音模式下等 TTS 就绪后再展示完整回复文本，避免台词与声音不同步。

#### Scenario: 开语音时不提前流式全文

- **WHEN** 用户开启语音播放
- **THEN** 气泡文本与 TTS 同步呈现
