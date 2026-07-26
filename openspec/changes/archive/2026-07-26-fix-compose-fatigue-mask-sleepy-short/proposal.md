## Why

无 open `dialogue-quality` Issue，基线 26/26 全绿；但 compose 路径探测发现：用户发送「今天好累啊」「一般般」或短句困倦口语（「困」「好困」「有点困」）时 `compose_contextual_reply` 返回 `None`，落入问卷式 open 兜底（如「好，我收到了。不用一次说完~」），而 `is_minimal_fatigue_utterance` 已覆盖「今天好累」但未覆盖「今天好累啊」；masking 分支已覆盖「一般」但未覆盖口语变体「一般般」。scene_first 编排下体验不自然，缺少先接住疲惫/masking/困倦的拟真感。

## What Changes

- `sentiment_lexicon.py`：`_MINIMAL_FATIGUE_UTTERANCES` 补充「今天好累啊」
- `dialogue_compose.py`：masking 分支补充「一般般」；新增短句困倦口语分支（困/好困/有点困，len≤6，排除困死等通勤语境）
- `persona.py`、`emotion/analyzer.py`：`_MINIMAL_MASKING` 补充「一般般」，与 compose/avatar 对齐
- `test_dialogue_compose.py`：补充探针单测
- 不改调度/安全/记忆主路径

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：补充「今天好累啊」疲惫变体、「一般般」masking 变体、短句困倦 compose 路径要求

## Impact

- `backend/app/sentiment_lexicon.py`
- `backend/app/dialogue_compose.py`
- `backend/app/persona.py`
- `backend/app/emotion/analyzer.py`
- `backend/tests/test_dialogue_compose.py`
- 影响模块：dialogue_compose 场景分支；不影响 `safety.py`、危机干预、记忆编排
