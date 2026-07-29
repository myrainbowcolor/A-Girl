## Context

`is_positive_utterance` 用 `POSITIVE_WORDS`（含「通过」「录取」）经 `contains_keyword` 匹配；但 `_NEGATION_BLOCK` 未覆盖「通过/录取」的否定前缀，导致「没通过」被判为正向，compose/mock 走报喜话术。另：选拔/面试失利短句（面试砸了/面试挂了/落选了/搞砸了）无专属 compose 分支，返回 `None` 落入问卷式 open 兜底。既有考试失利分支只覆盖考砸/没考好/挂科，不覆盖职场/选拔语境。

## Goals / Non-Goals

**Goals**
- 否定「没通过/未通过/不通过」「没录取/未录取」不再被判为正向
- 短句选拔/面试失利走共情陪伴接话，不报喜、不问卷兜底
- mock 与 compose 行为一致

**Non-Goals**
- 不改既有考试失利（考砸/挂科）分支
- 不扩展到长叙事（「面试官问了我三个小时然后说再考虑」）
- 不改调度频率、安全策略、记忆召回、avatar 映射

## Decisions

1. **词典层修否定**：在 `_NEGATION_BLOCK` 为「通过」「录取」加否定前缀，复用既有 `contains_keyword` 机制，避免另起一套否定逻辑。
2. **独立短句 compose 分支**：关键词「面试砸」「面试挂」「没通过」「落选」「搞砸」；`len(text) <= 12`；放在考试失利分支附近、通用 open 之前；话术侧重「选拔/面试挫败」而非「考砸」。
3. **「没通过」双保险**：即使词典未命中否定，compose 分支也会先接住共情，避免再走 `is_positive_utterance` 报喜路径（因 compose 在 positive 分支之后才到？需检查顺序）。

顺序核查：`is_positive_utterance` 分支在约 462 行，考试失利在约 668 行。因此「没通过」若不修词典，会**先**被 positive 分支抢走。**必须先修词典**，compose 分支才能命中。

4. **mock 对齐**：在 `_scene_reply` 增加同关键词短句分支。

## Risks / Trade-offs

- [「通过」否定漏网（如「压根没通过」含「没通过」子串）] → 「没通过」子串匹配已覆盖常见口语
- [「搞砸了」过宽（非面试语境）] → 仍属挫败倾诉，共情话术通用安全；限制 len≤12
- [与考试失利分支重叠] → 关键词不交叉（考砸/挂科 vs 面试砸/落选），互不抢占

## Migration Plan

纯后端逻辑扩展，无 DB/API 变更。回滚即 revert lexicon/compose/mock 改动。

## Open Questions

（无）
