## Why

无 open 的 `dialogue-quality` Issue，基线评测 26/26 全绿，但探针发现常见疲惫口语变体（「累了」「好累啊」「今天好累」「有点累」「累死了」）在 `scene_first` 生产路径下 `compose_contextual_reply` 返回 `None`，落入 `compose_open_reply` 问卷式兜底（如「是突然这样，还是已经有一阵子了？」）。单字「累」与整句「好累」已有专属分支，上述高频变体应同等覆盖。

## What Changes

- `dialogue_compose.py`：抽取 `is_minimal_fatigue_utterance` 辅助函数，覆盖「累了」「好累啊」「今天好累」「有点累」「累死了」等整句疲惫口语
- `mock.py`：对齐上述分支，与 compose 行为一致
- 补充 `test_dialogue_compose.py` 单测
- 更新 `openspec/specs/persona/spec.md` delta

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：口语化回复约束中补充疲惫口语变体的 compose/mock 行为要求

## Impact

- `backend/app/dialogue_compose.py`
- `backend/app/llm/mock.py`
- `backend/tests/test_dialogue_compose.py`
- 不影响安全、危机干预、记忆主路径
