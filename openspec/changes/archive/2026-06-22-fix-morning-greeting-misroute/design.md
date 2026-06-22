## Context

`scene_first` 策略下回复生成顺序为：`compose_contextual_reply` → `generate_scene_reply` → `compose_open_reply`。`mock.py` 的 `_scene_reply` 已有早安分支（约 L423），但 `compose_contextual_reply` 在更前执行，其工作压力短句规则（含「上班」且 len≤12）会先命中「早呀，今天又要上班了」（10 字），导致场景引擎的早安模板永远到不了。

## Goals / Non-Goals

**Goals:**
- 早安 + 通勤口语走自然寒暄，1～2 句、最多一个问句
- 真正的工作倾诉（「上班好累」「加班到十点」）仍走共情 vent 分支

**Non-Goals:**
- 不改 scene_first 优先级链
- 不改 mock.py 早安模板文案（已正确，作为参考）
- 不新增 API 或 DB 字段

## Decisions

1. **在 `compose_contextual_reply` 顶部区域（工作压力规则之前）增加 `_MORNING_GREETING_MARKERS` 检测**
   - 触发词：`早呀`、`早安`、`早上好`、`早啊`，或「又要上班」类通勤口语
   - 回复池参考 mock.py：`早呀～又要开工啦？今天想怎么撑过去？` 等口语化模板

2. **收紧工作压力短句规则**
   - 原：`("工作","上班",...) and len<=12`
   - 新：排除含早安问候标记的句子；且「又要上班」单独走早安分支而非 vent

3. **测试**
   - 单元：`compose_contextual_reply("早呀，今天又要上班了", [])` 不含「不公平」「忙不过来」
   - 场景：`run_dialogue_quality --scenario morning_checkin` 全绿

## Risks / Trade-offs

- 风险：极少数「上班」+ 早安混合的真实 vent 被误判为寒暄 → 缓解：若同时含「累/烦/加班/好烦」等 vent 词仍走工作压力分支
