## Why

对话质量评测 26 场景全绿，无 open `dialogue-quality` Issue。但生产路径 `scene_first` 优先调用 `compose_contextual_reply`，在 `stranger_late_night_lonely` 场景用户说「凌晨了还睡不着，有点孤独」时，compose 误命中通用失眠分支，返回「失眠的时候脑子特别吵…是什么事在转？」类话术，未接住「孤独」核心感受；用户同时表达失眠与孤独时，应先陪伴孤独感，而非仅聚焦睡不着。

修复前 transcript 片段：
- 用户：凌晨了还睡不着，有点孤独
- NPC：失眠的时候脑子特别吵，我懂这种难受。先别逼自己睡着，我陪你慢慢说，是什么事在转？

## What Changes

- 在 `backend/app/dialogue_compose.py` 的 `compose_contextual_reply` 中，于通用失眠关键词分支之前增加「孤独 + 失眠/睡不着」复合分支，先接住孤独与深夜难熬感，禁止仅用纯失眠反刍话术
- 补充 `test_dialogue_compose.py` 单测，覆盖「凌晨了还睡不着，有点孤独」话术
- 不改 orchestrator 调度、安全策略、mock.py 主路径、API 契约

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: 生产路径（dialogue_compose）在用户同时表达孤独与失眠时须先接住孤独感，与陪伴倾听场景一致，禁止仅返回失眠反刍式接话

## Impact

- `backend/app/dialogue_compose.py` — 孤独+失眠复合分支
- `backend/tests/test_dialogue_compose.py` — 新增测试
- 不影响 API 契约、安全策略、记忆检索、avatar、调度逻辑
