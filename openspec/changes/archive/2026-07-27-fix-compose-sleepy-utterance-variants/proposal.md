## Why

无 open `dialogue-quality` Issue，基线 26/26 全绿；但 compose 路径探测发现：用户发送困倦口语变体「困了」「好困啊」时 `compose_contextual_reply` 返回 `None`，scene_first 编排落入问卷式 open 兜底（如「好，我收到了。不用一次说完~」「我听着。哪一块你现在最想提？」），体验机械。上一轮已补齐「困/好困/有点困」短句分支，但未覆盖常见口语变体「困了」「好困啊」。

## What Changes

- `sentiment_lexicon.py`：新增 `is_minimal_sleepy_utterance`，覆盖困倦口语变体集合
- `dialogue_compose.py`：困倦分支改用 `is_minimal_sleepy_utterance`，与 mock 困倦共情对齐
- `llm/mock.py`：困倦变体命中专属共情分支，避免 empathy 问卷兜底
- `test_dialogue_compose.py`：补充「困了」「好困啊」探针单测
- 不改调度/安全/记忆主路径

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：补充困倦口语变体「困了」「好困啊」的 compose/mock 路径要求

## Impact

- `backend/app/sentiment_lexicon.py`
- `backend/app/dialogue_compose.py`
- `backend/app/llm/mock.py`
- `backend/tests/test_dialogue_compose.py`
- 影响模块：dialogue_compose 场景分支；不影响 `safety.py`、危机干预、记忆编排
