## Why

无 open `dialogue-quality` Issue，基线 26/26 全绿；但 compose 路径探测发现：用户发送短句崩溃/难受/郁闷倾诉（如「好崩溃」「难受」「好郁闷」）或疲惫变体（「好累好累」「累坏了」）时 `compose_contextual_reply` 返回 `None`，落入问卷式 open 兜底（如「好，我收到了。不用一次说完~」），而 `mock.py` 通用负面情绪分支已有共情接话。scene_first 编排下体验不自然，缺少先接住情绪的拟真感。

## What Changes

- `dialogue_compose.py`：在 open 兜底之前扩展短句低落倾诉分支关键词（崩溃/难受/郁闷/烦躁等），并扩展 `is_minimal_fatigue_utterance` 覆盖「好累好累」「累坏了」
- `sentiment_lexicon.py`：`_MINIMAL_FATIGUE_UTTERANCES` 追加疲惫变体
- `test_dialogue_compose.py`：补充「好崩溃」「难受」「好郁闷」「好累好累」探针单测
- 不改调度/安全/记忆主路径

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：补充短句崩溃/难受/郁闷及疲惫变体 compose 路径要求，禁止落入问卷式 open 兜底

## Impact

- `backend/app/dialogue_compose.py`
- `backend/app/sentiment_lexicon.py`
- `backend/tests/test_dialogue_compose.py`
- 影响模块：dialogue_compose 场景分支；不影响 `safety.py`、危机干预、记忆编排
