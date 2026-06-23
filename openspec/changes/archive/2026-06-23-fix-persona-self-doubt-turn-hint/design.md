## Context

`persona.py` 的 `_user_turn_tone_hint()` 已按用户轮次情感注入「本轮侧重」，覆盖愤怒、失眠、masking、想念等独立分支。自我怀疑/比较类口语（差劲、没用、原地踏步等）目前落入通用 `negative` 侧重，与 `_EMOTION_TONE["自我怀疑"]` 及 mock 比较分支的接话策略不一致。参考 `2026-06-19-persona-user-turn-anger-hint` 的增量模式，仅扩展 prompt 指引，不改编排主路径。

## Goals / Non-Goals

**Goals:**

- 自我怀疑/比较类用户句获得独立「本轮侧重」，指引先承认落差感、不急着反驳或灌鸡汤
- 检测优先于通用负向 sentiment 判断，与 `emotion.analyzer` 中已有 `_NEGATIVE` 关键词对齐
- 补充单元测试，确保 `jealous_comparison`、`impulse_regret` 相关句命中新侧重

**Non-Goals:**

- 不修改 `mock.py` 模板（已有关键词分支）
- 不调整 avatar、亲密度、安全策略
- 不新增对话质量场景

## Decisions

1. **关键词集合**：复用 `emotion.analyzer._NEGATIVE` 中与自我怀疑相关的子集（差劲、没用、自卑、原地踏步、管不住、自我怀疑），另加「不如」比较口语。放在 `persona.py` 独立常量 `_SELF_DOUBT_KEYWORDS`，与 analyzer 保持语义一致。
2. **检测顺序**：在 `is_longing_utterance` 之后、`analyze_lexicon` 负向判断之前插入自我怀疑检测；愤怒、失眠等更高优先级分支保持不变。
3. **侧重文案**：`self_doubt` 指引强调「别急着反驳或贴标签、先承认落差感真实、可轻问具体卡点」，与 `_EMOTION_TONE["自我怀疑"]` 语义对齐。

## Risks / Trade-offs

- [误判] 「不如你去休息」等含「不如」的非自我怀疑句 → 要求同时命中比较/自我否定语境词（差劲、没用、踏步等）或整句以自我否定为主；仅用「不如」不触发
- [与 mock 路径无关] mock 已有分支，本改动主要惠及真实 LLM → 靠 `test_persona.py` 断言 prompt 内容
