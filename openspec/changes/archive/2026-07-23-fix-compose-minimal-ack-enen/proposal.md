## Why

无 open `dialogue-quality` Issue，基线 26/26 全绿；但 compose 路径探测发现：用户整句回复「嗯嗯」时 `compose_contextual_reply` 返回 `None`，落入问卷式 open 兜底；同时 mock/persona/reply_guard 将整句「嗯嗯」误判为「吐槽敷衍」投诉（`"嗯嗯" in "嗯嗯"`），返回道歉话术而非极简附和接话。与「嗯」「哦」「好」等封闭极简句处理不一致，scene_first 编排下体验不自然。

## What Changes

- `sentiment_lexicon.py`：新增 `user_complains_filler_reply`，区分「整句嗯嗯附和」与「别嗯嗯/太敷衍」类投诉
- `dialogue_compose.py`：封闭极简附和分支补充「嗯嗯」，与「嗯」「哦」「好」对齐
- `llm/mock.py`、`reply_guard.py`、`persona.py`：复用新识别函数，修复误判
- `test_dialogue_compose.py`、`test_sentiment_lexicon.py`：补充单测
- 不改调度/安全/记忆主路径

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：补充整句「嗯嗯」极简附和 compose 路径与 filler 投诉识别要求

## Impact

- `backend/app/sentiment_lexicon.py`
- `backend/app/dialogue_compose.py`
- `backend/app/llm/mock.py`
- `backend/app/reply_guard.py`
- `backend/app/persona.py`
- `backend/tests/test_dialogue_compose.py`
- `backend/tests/test_sentiment_lexicon.py`
- 影响模块：dialogue_compose、mock 场景分支、reply_guard；不影响 `safety.py`、危机干预、记忆编排
