## Context

`persona.py` 已在 2026-06-19 引入 `_user_turn_tone_hint()`，按正/负/怀旧注入「本轮侧重」。愤怒场景（`angry_at_boss`）mock 模板已能「先陪发火」，但 prompt 层仍把愤怒与低落共用负向指引，真实 LLM 易偏安抚说教。

## Goals / Non-Goals

**Goals:**

- 愤怒/发泄关键词命中时，优先返回独立语气侧重
- 与 `emotion/analyzer.py` 负面词表、`mock.py` 愤怒分支语义一致
- 单元测试覆盖愤怒句与纯低落句的 prompt 差异

**Non-Goals:**

- 不改 mock 回复模板（已满足场景）
- 不改 avatar 映射或安全策略
- 不调整亲密度/关系阶段逻辑

## Decisions

1. **关键词优先于 sentiment 阈值**：在 `_user_turn_tone_hint()` 中，怀旧关键词之后、sentiment 判断之前，检查 `_ANGER_KEYWORDS` 元组（气死、骂我、生气、愤怒、火大、太过分、辞职 等）。命中则返回 `angry` 侧重，避免「气死了」仅走通用负向。
2. **侧重文案**：`ta 这轮在发泄怒气；先接住这股火，陪着听，别讲大道理也别催着冷静。` — 与 mock 愤怒回复、evaluator 共情标记对齐。
3. **测试**：`test_persona.py` 新增愤怒句断言含「火气」或「发泄」类指引；纯「心好累」句仍走原负向指引。

## Risks / Trade-offs

- [误判] 「辞职」单独出现可能触发愤怒侧重 → 仅在组合语境（气死/骂我/生气等）或明确发泄词时命中；`辞职` 与 `想/立刻` 同在 mock 已处理，prompt 侧重可包含「辞职」作为关键词之一，因场景多为冲动发泄。
- [与 mock 重复] prompt 层与 mock 层双重约束 → 仅影响真实 LLM 路径，mock CI 行为不变，可接受。
