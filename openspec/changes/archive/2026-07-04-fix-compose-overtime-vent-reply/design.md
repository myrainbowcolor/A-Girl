## Context

`orchestrator._generate_chat_reply` 在 `scene_first` 策略下优先调用 `compose_contextual_reply`；仅当返回 None 时才回退 `SceneReplyEngine`（`mock._scene_reply`）。`stranger_work_vent` 场景用户话「今天又加班到十点，好累好烦」含加班/十点/累/烦关键词，mock 已有专属分支（`mock.py` 第 245–252、325–333 行），但 compose 缺失：现有「工作上的事」分支要求 `len(text) <= 12`，「好烦」短句分支要求 `len(text) <= 10`，均无法命中该句。

参考既有改动（如 `fix-compose-angry-at-boss-reply`）：在 compose 中按关键词优先级插入分支，使用 `_pick` 确定性变体，与 mock 话术对齐。

## Goals / Non-Goals

**Goals:**

- `compose_contextual_reply` 命中加班/下班疲惫倾诉时返回共情接话
- 分支位于通用负面 open 兜底（`好烦`/`烦` 短句等）之前，避免问卷式「突然还是一阵子」
- 单测锁定 `stranger_work_vent` 话术；全量 pytest + dialogue quality strict 保持绿

**Non-Goals:**

- 不改 mock.py 场景分支（已正确）
- 不改 evaluator 规则或新增场景
- 不扩展其他 compose 缺口（节日孤独/育儿焦虑/撑不住等留待后续 change）

## Decisions

1. **关键词与 mock 对齐**：检测 `加班`/`下班`/`十点`/`很晚`/`熬夜` 与 `累`/`烦`/`辛苦`/`熬`/`撑` 组合；或 `加班`/`996`/`KPI`/`开会到` 单独命中。
2. **插入位置**：放在 `_is_morning_greeting` 与工作短话题分支之后、失眠/孤独复合分支之前；亦可在愤怒发泄分支之前增加独立加班疲惫块，确保先于 `好烦` 短句（`len <= 10`）分支。
3. **话术风格**：compose 不含 `dear`/`mood` 前缀，保持 1～2 句口语、至多一个问句；陌生关系用克制关怀语气（「辛苦你了」「我陪着」），不过度亲昵。

## Risks / Trade-offs

- [compose 抢先命中导致与 mock 话术略有差异] → 单测断言关键词与共情标记，dialogue quality 全量回归
- [误伤含「加班」但非倾诉的句子] → 与 mock 同规则，要求同时含疲惫/烦躁标记
