## Context

主动消息由 `ProactivityEngine`（固定触发）与 `rule_proactive_message`（洞察规则路径）生成。当前 idle/reconnect 模板在同一句叠加「怎么样？」与「随便说点小事也行」，违反 persona 的「每轮最多一个问句」原则，削弱拟真感。调度逻辑、冷却与 API 均已稳定，本轮仅改文案字符串。

## Goals / Non-Goals

**Goals:**

- welcome / idle / emotion 固定文案更口语、单问句
- `rule_proactive_message` 各 need 模板去掉叠问与客服腔
- 单元测试断言问句数量 ≤ 1

**Non-Goals:**

- 不改 `proactive_idle_seconds`、冷却、触发优先级
- 不改 LLM 主动消息 system prompt（真实 LLM 路径保持现有逻辑）
- 不改事件触发（birthday/interview/exam）模板——已较自然

## Decisions

1. **文案策略**：用「陈述 + 单问句」或「纯陈述邀请」替代「问句 + 第二引导」。例如 idle 改为「好久没聊了，有点想你～最近还好吗？」（一问句）或「好久没聊了，想听听你最近怎么样。」（零问句陈述邀请）。
2. **测试方式**：在 `test_proactivity` / `test_user_insight` 增加辅助函数 `_question_count(msg) <= 1`，覆盖 welcome/idle/emotion 与 rule 模板四类 need。
3. **不动 event 模板**：考试/面试/生日文案已符合单问句或零问句，避免无关 diff。

## Risks / Trade-offs

- [文案变短可能显得冷淡] → 保留「想你」「陪着」等情感词，维持温暖基调
- [测试只数问号可能漏掉「吗」无问号句] → 当前模板均用「？」结尾问句，足够覆盖
