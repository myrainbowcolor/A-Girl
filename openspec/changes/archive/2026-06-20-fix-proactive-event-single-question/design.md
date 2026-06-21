## Context

`ProactivityEngine._event_message` 为生日/面试/考试等事件生成固定开场白。上一轮 `improve-proactive-message-naturalness` 已优化 welcome/idle/emotion 与 insight 规则模板，但 event 模板未纳入，birthday 仍含两个问号。

## Goals / Non-Goals

**Goals:**

- 所有 event 模板全句至多一个问号，语气口语、像真人微信
- 补充 pytest 覆盖事件触发文案约束

**Non-Goals:**

- 不改事件抽取、调度优先级、冷却、API
- 不引入 LLM 生成 event 文案（仍用规则模板）

## Decisions

1. **birthday 保留祝福语气、去掉第二问句**  
   将「有没有给自己留一点放松的时间？」改为陈述式陪伴（如「记得给自己留点放松时间」），全句仅保留「生日快乐」相关的一个轻问句或改为感叹句。

2. **interview / exam / other 复核**  
   已符合单问句约束则不动；仅 birthday 必改。

3. **测试**  
   在 `test_event_trigger_has_priority` 或新增 `test_event_message_single_question` 中对各 kind 断言 `?` + `？` ≤ 1。

## Risks / Trade-offs

- [Risk] 生日文案变短、情感略减 → 用口语化陈述补陪伴感，避免空泛客服腔
- [Risk] 仅 mock/规则路径 → 与现有架构一致，真实 LLM 主动消息走 insight 路径
