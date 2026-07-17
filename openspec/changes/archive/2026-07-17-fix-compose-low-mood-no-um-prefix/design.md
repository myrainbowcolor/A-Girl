## Context

`scene_first` 编排优先 `compose_contextual_reply`，结果经 `polish_reply` 后下发。emo/心累分支模板含句首「嗯……」，触发 `reply_is_filler_heavy` 后 `polish_reply` 在 `_compose_or_fallback` 处提前返回，跳过末尾 `strip_npc_leading_um`，导致生产路径仍输出机械腔句首。

## Goals / Non-Goals

**Goals:**

- emo/心累与「不开心」compose 与 mock 模板去掉句首「嗯」
- 单测覆盖 compose 与 polish 后不以「嗯」开头

**Non-Goals:**

- 不重构 `polish_reply` 提前返回逻辑（避免波及面广）
- 不批量清理 compose 内其他含「嗯，」的模板（本轮仅低落相关分支）

## Decisions

1. **源头修模板**：在 `dialogue_compose.py` 与 `mock.py` 将「嗯……这种低落」改为「这种低落…」等自然口语，避免触发 filler 误判。
2. **测试策略**：`test_compose_emo_fatigue` 增加 `assert not out.startswith("嗯")`；新增 `polish_reply("心好累", out)` 同样断言。

## Risks / Trade-offs

- [去掉嗯后语气略直] → 保留「我懂」「陪着」等共情词，维持温暖基调
- [仅修低落分支，其他嗯开头模板仍存在] → 后续可按 rule_id 分批处理，本轮范围可控
