## Why

对话质量 26 场景全绿、无 open `dialogue-quality` Issue，但生产路径 `compose_contextual_reply` 处理短句烦躁口语（如「好烦」「有点烦」，len≤10）时，模板以「嗯，」开头。`reply_starts_with_um` 会将其记为 `robotic_tone`（major），违反 persona spec「禁止以嗯开头」，用户收到敷衍机械腔而非自然共情。

示例：`好烦` → `嗯，听起来心里挺堵的。是突然这样的，还是已经有一阵子了？`

## What Changes

- 调整 `dialogue_compose.py` 短句烦躁分支模板，去掉句首「嗯，」
- 补充 `test_dialogue_compose.py` 断言：`compose_contextual_reply("好烦")` 与 `polish_reply` 后均不以「嗯」开头
- 不改安全、危机干预、调度频率或 API 契约

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：明确短句烦躁 compose 路径（「好烦」「有点烦」等 len≤10）返回句不得以「嗯」开头，且经 `polish_reply` 后仍满足该约束

## Impact

- `backend/app/dialogue_compose.py` — 短句烦躁模板文案
- `backend/tests/test_dialogue_compose.py` — 句首嗯约束测试
- 不影响 orchestrator 主路径、safety、记忆、avatar、proactivity、mock.py（mock 无对应短句分支，由 compose 优先命中）

## 成功标准

- `compose_contextual_reply("好烦")` 与 `polish_reply("好烦", …)` 均不以「嗯」开头
- `python3 -m pytest` 全绿；`run_dialogue_quality.py --strict` 26/26 通过
