## Why

无 open `dialogue-quality` Issue，基线 26/26 全绿；但 compose 路径探测发现：`compose_contextual_reply("在吗")` 有自然接话，而常见变体「你在吗」「有人吗」「在不在」「还在吗」返回 `None`，落入 open 问卷兜底（如「嗯，这事不急。你想从哪儿开始说？」）。mock 的 `_user_is_greeting` 对含「在吗」的短句会走问候分支，生产 `scene_first` 编排优先走 compose，导致探问在线感不自然。

## What Changes

- `sentiment_lexicon.py`：新增 `is_presence_ping_utterance` 识别常见在线探问短句
- `dialogue_compose.py`：友好问候/探问分支复用该识别，覆盖「你在吗」「有人吗」等变体；返回口语化「在呢」接话，至多一个问句；不以「嗯」开头
- `test_dialogue_compose.py`：补充 compose 探问单测
- 与 mock 问候行为对齐，不改调度/安全/记忆主路径

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：补充在线探问 compose 路径与 mock 一致的行为要求

## Impact

- `backend/app/sentiment_lexicon.py`
- `backend/app/dialogue_compose.py`
- `backend/tests/test_dialogue_compose.py`
- 影响模块：`dialogue_compose`（scene_first 第二层）；不影响 `safety.py`、危机干预、记忆编排
