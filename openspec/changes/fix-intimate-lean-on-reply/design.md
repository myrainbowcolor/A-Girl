## Context

`scene_first` 编排优先调用 `compose_contextual_reply`，未命中时走 `generate_scene_reply`（mock.py `_scene_reply`）。`close_miss_you` 第二轮含「累」与「靠着」，当前被 `_scene_reply` 第 531 行通用负面分支抢先命中，返回 stage 无关的泛化共情话术，浪费了 `_empathy_reply` 中已有的亲密「靠着」模板。

## Goals / Non-Goals

**Goals:**
- 「靠着/想靠着」依恋请求在亲密关系下优先命中专属分支
- compose 与 mock 行为一致，每轮至多一个问句
- `close_miss_you` 第二轮 transcript 含倚靠/陪伴类亲密标记

**Non-Goals:**
- 不改关系阶段计算、亲密度阈值
- 不扩展物理接触边界（未成年人安全策略不变）
- 不改 proactivity、avatar 引擎主逻辑

## Decisions

1. **分支位置**：在 `_scene_reply` 通用负面关键词分支（约 L531）之前插入「靠着」检测；含「靠着」「想靠着」「倚靠」即命中。
2. **stage 分层**：亲密用「过来/靠着我/抱抱」；朋友用「陪着/慢慢说」；陌生/熟悉避免过度亲昵，仍接住疲惫。
3. **compose 推断亲密**：若 `prior_assistant` 含「亲爱的」「宝贝」或用户句含「靠着你说」，走亲密话术池；否则走温和陪伴话术。
4. **场景期望**：`close_miss_you` 第二轮增加对回复含「靠」「陪」「抱抱」之一的软断言（evaluator 已有 empathy 检查，场景可加 developer_notes 或依赖 transcript 人工复核；测试侧用单测锁定）。

## Risks / Trade-offs

- 「靠着」子串误匹配 → 仅匹配明确口语「靠着」「想靠着」「倚靠」，不用单字「靠」
- compose 无 system_prompt stage → 用上文亲昵标记推断，与 close_miss_you 多轮一致

## 参考

- `openspec/specs/persona/spec.md` 口语化与关系阶段约束
- `docs/DIALOGUE_QUALITY.md` rule_id → 模块映射
