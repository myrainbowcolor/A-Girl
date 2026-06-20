## Context

`emotion_to_avatar` 在 `user_sentiment < -0.2` 时切换 comfort 表情。极简回复场景（`short_reply_user`）用户常说「还好」「不知道」等整句短语，mock 已生成共情话术，但 `analyze_lexicon` 返回中性，导致音画不一致。

## Goals / Non-Goals

**Goals:**
- 整句极简口语触发偏负向 sentiment，avatar 展示安慰姿态
- 补充场景期望与单测，防止回归
- 最小 diff，仅改 analyzer + scenarios + tests

**Non-Goals:**
- 不改 orchestrator 主路径、不改 mock 话术
- 不做会话级情绪 carryover（复杂度超出本轮）
- 不改 safety / 危机干预

## Decisions

1. **整句精确匹配而非子串扩展**
   - 在 `analyze_lexicon` 开头对 `text.strip()` 做集合匹配
   - 理由：避免「我不知道该怎么办」等长句误判；与 mock.py 极简分支逻辑一致

2. **sentiment 取值**
   - 「还好」「还行」「一般」→ -0.35（略低于 -0.2 阈值，表达.masking 式回应）
   - 「不知道」「说不清」「说不上」→ -0.45（更明确的低落/回避信号）

3. **场景期望加固**
   - `short_reply_user` 第 2～4 轮加 `expect_comfort_avatar=True`（「还好」「不知道」「累」）

## Risks / Trade-offs

- [用户真心说「还好」时显示关切脸] → 可接受：陪伴场景下轻微关切优于呆板平静；话术本就带试探性共情
- [子串误判] → 整句匹配规避

## Migration Plan

无数据迁移。部署后即生效。回滚：移除 analyzer 前置匹配块。

## Open Questions

无
