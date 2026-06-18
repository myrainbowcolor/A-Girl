## Why

对话质量评测 `memory_pet_name` 场景第 2 轮，用户说「它今天又把杯子打翻了哈哈」，NPC 却回复泛化开心句「哇，听你这么说我也跟着开心起来了！快多跟我说说～」，未接住宠物捣蛋的具体细节，拟真度不足。根因是 mock 模板因「哈哈」命中通用开心分支，且代词「它」未关联上文「橘子」的宠物语境。

## What Changes

- 在 `backend/app/llm/mock.py` 增加宠物捣蛋/日常趣事分支：当上文或记忆含猫/狗/宠物信息，且本轮用「它」描述捣蛋行为（打翻杯子等）时，生成贴合宠物名的口语回复
- 该分支优先级高于通用「哈哈/开心」分支，避免误匹配
- 补充单元测试覆盖「打翻杯子」续聊话术

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: mock 回复在宠物续聊场景应先回应具体趣事再表达同频开心，而非泛化报喜句式

## Impact

- `backend/app/llm/mock.py` — 场景化回复分支
- `backend/tests/test_mock_llm.py` — 新增/更新测试
- 不影响 API 契约、安全策略、记忆检索主路径
