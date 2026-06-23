## Why

对话质量评测 `memory_pet_name` 场景第 2 轮，用户说「它今天又把杯子打翻了哈哈」，生产路径（`scene_first`）实际回复为泛化句「哈哈，听你笑我也跟着轻松点了～发生什么好事啦？」，未接住宠物捣蛋细节。根因是 `orchestrator._generate_chat_reply` 优先调用 `compose_contextual_reply`，其中通用「哈哈」分支抢在 `mock.py` 已修复的宠物捣蛋场景之前命中；`mock.py` 单测通过但编排路径未生效。

## What Changes

- 在 `backend/app/dialogue_compose.py` 的 `compose_contextual_reply` 中，于通用「哈哈/嘿嘿」分支之前增加宠物捣蛋续聊分支：当近期用户话或记忆含猫/狗/宠物语境，且本轮用「它」描述打翻杯子等捣蛋行为时，生成贴合宠物名的口语回复
- 补充 `test_dialogue_compose.py` 单测，覆盖「打翻杯子哈哈」续聊话术
- 可选：为 `memory_pet_name` 第 2 轮补充 evaluator 期望（提及宠物行为），防止回归

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: 生产路径（dialogue_compose）在宠物续聊场景须与 mock 一致，先回应具体趣事再表达同频开心，禁止泛化报喜句式

## Impact

- `backend/app/dialogue_compose.py` — 宠物捣蛋续聊分支
- `backend/tests/test_dialogue_compose.py` — 新增测试
- 不影响 API 契约、安全策略、记忆检索、orchestrator 调度顺序
