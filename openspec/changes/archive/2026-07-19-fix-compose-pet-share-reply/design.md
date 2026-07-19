## Context

`orchestrator` 在 `scene_first` 策略下优先调用 `compose_contextual_reply` 拼装无 LLM 回复。`mock.py` 已有「养宠物 / 分享毛孩子」分支（约 270 行），但 `dialogue_compose.py` 仅覆盖代词「它」捣蛋续聊，首轮分享返回 `None`。`test_compose_pet_antics_followup` 的历史 assistant 回复是假设性的，未验证 compose 首轮路径。

架构参考 `docs/ARCHITECTURE.md`：scene_first 第二层为规则拼装，与 mock 场景分支应对齐。

## Goals / Non-Goals

**Goals:**

- 补齐 compose 养宠首轮分享分支，与 mock 话术风格一致
- 排除含「记得」的记忆追问句，避免与记忆召回场景冲突
- 单测覆盖首轮分享，确保不落入 open 兜底

**Non-Goals:**

- 不改记忆抽取/召回逻辑
- 不调整宠物捣蛋续聊（代词「它」）已有分支
- 不修改 API 或编排主路径

## Decisions

1. **分支位置**：放在「你在干嘛」探问之后、宠物捣蛋续聊（代词「它」）之前。首轮分享含「猫/狗/宠物」关键词，不会与代词续聊冲突。
2. **话术来源**：复用 mock 核心语义（养猫亲昵、毛孩子陪伴），用 `_pick` 做确定性变体，与 compose 其他分支一致。
3. **记忆追问排除**：`"记得" not in text`，与 mock 一致，避免「你还记得我的猫叫什么吗」误入分享分支。

## Risks / Trade-offs

- [误命中] 用户句含「猫/狗」但非分享语境 → 风险低，该关键词在自然对话中多为分享；与 mock 行为一致。
- [话术重复] 固定模板可能单调 → 用 `_pick` 多模板缓解，与现有 compose 模式一致。
