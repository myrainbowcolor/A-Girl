## Context

`safety.py` 中 `_ADULT_RESPONSE` 在拒绝恋爱越界后使用两个连续问句引导话题，与 persona/proactivity 规范的「每轮最多一个问句」不一致。该话术为硬编码安全响应，不经 LLM，改动面极小。

## Goals / Non-Goals

**Goals:**

- 将 `_ADULT_RESPONSE` 改为口语化、单问句引导
- 保持拒绝恋人角色、拦截行为不变
- 补充单元测试防回归

**Non-Goals:**

- 不修改危机、暴力、隐私类话术（除非同类叠问问题）
- 不调整 `minor_guard_prompt` 或关键词列表
- 不改变 orchestrator 安全前置逻辑

## Decisions

1. **文案策略**：保留前半句明确拒绝（「这个话题我们就不聊啦…好朋友」），后半句合并为单一轻问，如「最近有什么想跟我说的吗？」——比叠问更自然，仍引导到合适话题。
2. **测试**：在 `test_safety.py` 增加 `_question_count` 断言，与 `test_proactivity.py` 一致。
3. **不改 evaluator**：现有 `questionnaire_mode` 可能未覆盖 safety 路径；以单元测试为主，dialogue quality `minor_boundary` 场景仍验证 `expected_safety` 拦截。

## Risks / Trade-offs

- [风险] 新话术过短显得冷淡 → 保留「陪你说说心事、一起开心的好朋友」温暖定位
- [风险] 削弱边界 → 拒绝句不变，仅减少第二问句
