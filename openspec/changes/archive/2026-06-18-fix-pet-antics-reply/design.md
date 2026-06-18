## Context

`memory_pet_name` 场景第 2 轮用户输入「它今天又把杯子打翻了哈哈」。mock `_scene_reply` 中通用开心分支（匹配「哈哈」）优先级高于宠物语境判断，导致回复与具体趣事脱节。架构上 mock 采用规则链式匹配（见 `docs/ARCHITECTURE.md` LLM Provider 抽象），本改动仅增一条分支，不改编排接口。

## Goals / Non-Goals

**Goals:**

- 宠物续聊（代词「它」+ 捣蛋关键词）生成贴合上文宠物名的口语回复
- 分支置于通用开心匹配之前，避免「哈哈」误触发
- 保持 26 场景 strict 评测全绿

**Non-Goals:**

- 不改真实 LLM prompt（仅 mock 基线）
- 不扩展记忆检索或 DB schema
- 不调整 avatar 映射逻辑

## Decisions

1. **检测条件**：`prior`（用户历史）或 `memories` 含「猫/狗/宠物/橘子」等，且本轮含「它」+（打翻/杯子/搞破坏/淘气）→ 走宠物捣蛋分支
2. **宠物名提取**：复用 `_format_memory_recall` 中 `叫(.+?)的(?:猫|狗)` 正则；若无则统称「小家伙」
3. **话术风格**：轻松吐槽 + 一个轻问句，关系阶段沿用 `_endearment` / `_scene_mood`
4. **优先级**：插入在「养宠物首次分享」分支之后、「开心分享」分支之前

## Risks / Trade-offs

- [误判] 非宠物语境的「它」+「打翻」→ 限定需 prior 含宠物关键词，降低误触
- [仅 mock] 真实 LLM 不受此规则约束 → 依赖 persona prompt 通用约束，本 change 聚焦 CI 确定性基线
