## Context

`docs/ARCHITECTURE.md` 中 orchestrator 流程：安全 → 记忆 → 情绪评估 → 构建 prompt → LLM 生成。Avatar（`avatar.py`）与 TTS（`voice/style.py`）已在 `user_sentiment < -0.2` 时切换 comfort/worry 表现，但 `persona.py` 的 `build_system_prompt` 仅读取 NPC 内在 PAD 标签，未反映用户本轮情感。

情绪引擎带衰减（decay），用户从开心切到「心好累」时，NPC 内在状态可能仍为「平和」，导致真实 LLM 收到「自然闲聊」指引，与安慰表情矛盾。

## Goals / Non-Goals

**Goals:**

- 在 `persona.py` 用现有 `analyze_lexicon()` 为 prompt 追加「本轮侧重」
- 与 avatar/TTS 情感阈值对齐（偏负 / 偏正 / 怀旧关键词）
- 单元测试覆盖负面用户句 + 平和 NPC 情绪场景

**Non-Goals:**

- 不改 orchestrator 传参（已有 `user_text`）
- 不改 mock LLM 模板、安全策略、情绪衰减参数
- 不新增 LLM 调用做情感分析

## Decisions

1. **复用 `analyze_lexicon` 而非 orchestrator 的 `sentiment_for_log`**
   - 理由：`build_system_prompt` 已接收 `user_text`；persona 模块保持自包含，避免 orchestrator 签名变更
   - 与 avatar 使用同一词典，行为一致

2. **阈值与 avatar 对齐：sentiment < -0.3 偏负，> 0.3 偏正**
   - 理由：analyzer 已有 label 分界；avatar 用 -0.2 触发表情，prompt 用 -0.3 避免轻微负词过度共情

3. **怀旧分支：检测「怀念/童年/小时候」等关键词**
   - 理由：lexicon 对怀旧场景 sentiment 可能接近中性，需单独轻量关键词补充

4. **注入位置：紧接「语气微调」之后**
   - 格式：`【本轮侧重】{hint}`，仅 hint 非空时输出

## Risks / Trade-offs

- [词典误判] → 沿用现有 analyzer 词表，与全链路一致；中性时不注入
- [与内在语气冲突] → 「本轮侧重」补充而非替换 `_emotion_tone_hint`，两者并存
- [Mock CI 无感知] → 新增 persona 单测验证；dialogue quality 仍全量跑 strict 作回归
