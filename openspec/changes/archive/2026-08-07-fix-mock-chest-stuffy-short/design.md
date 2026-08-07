## Context

See proposal.md - Why。生产路径 `compose_contextual_reply` 已对 ≤10 字「堵得慌 / 心里堵 / 堵心 / 心堵 / 好堵」返回共情接话；`mock.py` 未收录同关键词，短句落入空串，导致 CI/mock 与 compose 不一致。

## Goals / Non-Goals

**Goals:**
- mock 对「心好堵 / 堵得慌」等短句返回与 compose 对齐的共情话术
- `_VENT` / `_user_tone` 识别为负面倾诉，避免中性空串
- 既有 compose 心里堵分支与对话质量基线回归通过
- 最小 diff，可测可回滚

**Non-Goals:**
- 不改 `dialogue_compose.py` 关键词表与话术（已覆盖）
- 不改安全策略、avatar、记忆/编排主路径、调度频率
- 不扩「感觉空了 / 掏空了 / 没意思了 mock」等旁路缺口（另开 change）
- 不新增 dialogue_quality 场景（基线已 26/26）
- 不用裸「堵」以免「堵车」等误伤

## Decisions

1. **关键词**：与 compose 对齐：`堵得慌`、`心里堵`、`堵心`、`心堵`、`好堵`（覆盖「心好堵 / 好心堵 / 心里堵得慌」等）。不用裸「堵」。
2. **位置**：置于「什么都不想干 / 整个人空了」分支之后、泛化低落（含「烦」）分支之前。
3. **话术**：复用 compose 同款「心里堵着 / 堵得慌……陪着你」模板，加 mock 的 dear/mood 前缀；至多一个问句。
4. **长度**：`len(text) <= 10`，与 compose 一致。
5. **测试**：mock 参数化覆盖代表性变体；compose 参数化扩展「心好堵 / 好心堵 / 好堵」。

## Risks / Trade-offs

- [「好堵」过宽] → 限制 ≤10 字，且不用裸「堵」；「堵车」不含上述关键词
- [与烦躁分支混淆] → 独立关键词，话术以「堵」为核心，不套用「烦死了」专用表述
- [危机误报] → 不改 `safety.py`
