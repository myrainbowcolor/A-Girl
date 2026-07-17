## Why

对话质量 26 场景全绿、无 open `dialogue-quality` Issue，但生产路径 `compose_contextual_reply` 处理「心好累」等 emo/低落口语时，模板以「嗯……」开头。`polish_reply` 会将其判为 `reply_is_filler_heavy` 并提前 `return` compose 结果，跳过 `strip_npc_leading_um`，导致用户仍收到句首「嗯」的机械腔回复，违反 persona spec「禁止以嗯开头」。

## What Changes

- 调整 `dialogue_compose.py` emo/心累与「不开心」分支模板，去掉句首「嗯……」
- 同步 `mock.py` 对应场景分支，保持 compose 与 mock 一致
- 补充 `test_dialogue_compose.py` 断言：`compose_contextual_reply("心好累")` 与 `polish_reply` 后均不以「嗯」开头
- 不改安全、危机干预、调度频率或 API 契约

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：明确 emo/心累与不开心 compose 路径返回句不得以「嗯」开头，且经 `polish_reply` 后仍满足该约束

## Impact

- `backend/app/dialogue_compose.py` — emo/不开心模板文案
- `backend/app/llm/mock.py` — 对齐 mock 场景分支
- `backend/tests/test_dialogue_compose.py` — 句首嗯约束测试
- 不影响 orchestrator 主路径、safety、记忆、avatar、proactivity

## 成功标准

- `compose_contextual_reply("心好累")` 与 `polish_reply("心好累", …)` 均不以「嗯」开头
- `python3 -m pytest` 全绿；`run_dialogue_quality.py --strict` 26/26 通过
