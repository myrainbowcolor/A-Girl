## Context

`scene_first` 编排优先 `compose_contextual_reply`。短句烦躁分支（`好烦`/`有点烦`/`烦死了` 且 len≤10）在 insomnia 长句等分支之后、封闭极简分支之前命中。当前首条模板以「嗯，」开头，触发 `reply_starts_with_um` → `robotic_tone` major。

## Goals / Non-Goals

**Goals:**

- 短句烦躁 compose 模板去掉句首「嗯，」
- 单测覆盖 compose 与 polish 后不以「嗯」开头

**Non-Goals:**

- 不批量清理 compose 内其他含「嗯，」的模板（如「后来呢」兜底、公园闲聊等，后续分批）
- 不重构 `polish_reply` 或 mock 通用负面分支

## Decisions

1. **源头修模板**：将「嗯，听起来心里挺堵的」改为「听起来心里挺堵的」或「心里挺堵的吧」，保留至多一个问句的共情接话。
2. **测试策略**：新增 `test_compose_short_annoyance_no_um_prefix`，断言 `好烦`/`有点烦` compose 与 polish 后不以「嗯」开头。

## Risks / Trade-offs

- [去掉嗯后语气略直] → 保留「堵」「缠人」等共情词，维持温暖基调
- [仅修短句烦躁分支] → 范围可控，与 emo/倦怠极限修复模式一致
