## Context

`orchestrator._generate_chat_reply` 在 `scene_first` 策略下优先调用 `compose_contextual_reply`；仅当返回 None 时才回退 `SceneReplyEngine`（`mock._scene_reply`）。`angry_at_boss` 场景两轮用户话含责骂/愤怒与辞职冲动关键词，mock 已有专属分支（`mock.py` 第 632–643 行），但 compose 缺失，导致生产路径与 mock 不一致。

参考既有改动（如 `fix-compose-reconcile-fight-reply`）：在 compose 中按关键词优先级插入分支，使用 `_pick` 确定性变体，与 mock 话术对齐。

## Goals / Non-Goals

**Goals:**

- `compose_contextual_reply` 命中当众被骂倾诉与冲动辞职念头时返回共情接话
- 分支位于通用负面 open 兜底（`好烦`/`烦` 等）之前，避免问卷式「突然还是一阵子」
- 单测锁定 `angry_at_boss` 两轮话术；全量 pytest + dialogue quality strict 保持绿

**Non-Goals:**

- 不改 mock.py 场景分支（已正确）
- 不改 evaluator 规则或新增场景
- 不扩展其他 compose 缺口（节日孤独/育儿焦虑/撑不住等留待后续 change）

## Decisions

1. **关键词与 mock 对齐**：检测 `气死`、`骂我`、`骂`、`老板`；续轮检测 `辞职` + (`想`/`要`/`立刻`) 且排除「辞职信」文书请求。
2. **插入位置**：放在吵架和好分支之后、`好烦`/`烦` 短句分支之前，与 mock 愤怒发泄优先级一致。
3. **话术风格**：compose 不含 `dear`/`mood` 前缀，保持 1～2 句口语、至多一个问句，禁止站队煽动辞职或说教式劝冷静。

## Risks / Trade-offs

- [compose 抢先命中导致与 mock 话术略有差异] → 单测断言关键词与共情标记，dialogue quality 全量回归
- [误伤含「骂」的其他句子] → 与 mock 同规则，已有场景全绿基线
