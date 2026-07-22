## Why

对话质量基线 26/26 全绿，无 open `dialogue-quality` Issue。但生产路径 `compose_contextual_reply` 处理短句烦躁口语（「好烦」「有点烦」「挺烦」「烦死了」，整句 len≤10）时，模板之一为「是突然这样的，还是已经有一阵子了？」——与 persona spec 禁止的问卷式 open 兜底一致，真实 LLM/scene_first 路径下体验偏机械。mock `_scene_reply` 对含「烦」的短句走通用低落共情（「不太好受…我陪着」），compose 应与之对齐并去掉「突然还是一阵子」套话。

## What Changes

- 在 `dialogue_compose.py` 短句烦躁分支替换问卷式模板，改为先接住烦躁、表达陪伴，至多一个轻问句（如「是什么事最缠人」）
- 同步 `mock.py` `_empathy_reply` 陌生关系「烦」分支，去掉「突然还是一阵子」套话
- 补充 `test_dialogue_compose.py` 断言：回复不含问卷 marker，且不以「嗯」开头

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: 短句烦躁 compose/mock 路径 MUST 先接住烦躁、禁止「突然还是一阵子」类问卷接话；回复 MUST NOT 以「嗯」开头

## Impact

- `backend/app/dialogue_compose.py`：短句烦躁模板
- `backend/app/llm/mock.py`：`_empathy_reply` 陌生「烦」分支
- `backend/tests/test_dialogue_compose.py`：新增/加强探针
- 不影响 safety、危机干预、记忆主路径
