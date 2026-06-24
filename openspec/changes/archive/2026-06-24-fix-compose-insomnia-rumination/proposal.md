## Why

对话质量评测 26 场景全绿，无 open `dialogue-quality` Issue。但生产路径 `scene_first` 优先调用 `compose_contextual_reply`，在 `insomnia_rumination` 场景第 3 轮用户说「越躺越清醒，好烦」时，compose 误命中通用短句「好烦」分支，返回「是突然这样的，还是已经有一阵子了？」类问卷式接话；而 `mock.py` 已有更贴合失眠反刍的「越躺越清醒真的折磨人」话术。根因是 compose 缺少失眠/反刍专用分支，且通用烦分支优先级过高。

## What Changes

- 在 `backend/app/dialogue_compose.py` 的 `compose_contextual_reply` 中，于通用「好烦」短句分支之前增加失眠反刍分支：「越躺越清醒」、含失眠关键词、项目悬停焦虑（与 mock.py 对齐）
- 补充 `test_dialogue_compose.py` 单测，覆盖「越躺越清醒，好烦」续聊话术
- 不改 orchestrator 调度、安全策略、mock.py 主路径、API 契约

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: 生产路径（dialogue_compose）在失眠反刍续聊场景须与 mock 一致，先接住烦躁/反刍感，禁止通用问卷式「突然还是一阵子」接话

## Impact

- `backend/app/dialogue_compose.py` — 失眠反刍续聊分支
- `backend/tests/test_dialogue_compose.py` — 新增测试
- 不影响 API 契约、安全策略、记忆检索、avatar、调度逻辑
