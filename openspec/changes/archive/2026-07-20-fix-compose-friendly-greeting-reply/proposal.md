## Why

无 open `dialogue-quality` Issue，但 compose 路径探测发现：`compose_contextual_reply("你好呀")` 与 `compose_contextual_reply("嗨，第一次来")` 返回 `None`，落入 open 问卷兜底；而 `mock.py` 与 `sentiment_lexicon.is_friendly_greeting_utterance` 已识别此类初识问候。`stranger_first_greet`、`long_session_warmup` 场景虽在 mock 路径通过，生产 `scene_first` 编排会优先走 compose，导致初识问候不够自然、表情也难与温暖微笑 spec 对齐。

## What Changes

- `dialogue_compose.py`：友好问候分支改用 `is_friendly_greeting_utterance`（或等价前缀匹配），覆盖「你好呀」「嗨，第一次来」等变体；陌生关系返回自然自我介绍，至多一个问句；不以「嗯」开头
- `test_dialogue_compose.py`：补充 compose 友好问候单测
- 与 `mock.py` 行为对齐，不改调度/安全/记忆主路径

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：补充友好问候 compose 路径与 mock 一致的行为要求

## Impact

- `backend/app/dialogue_compose.py`
- `backend/tests/test_dialogue_compose.py`
- 影响模块：`dialogue_compose`（scene_first 第二层）；不影响 `safety.py`、危机干预、记忆编排
