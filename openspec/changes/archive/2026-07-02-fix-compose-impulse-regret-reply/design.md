## Context

`orchestrator._generate_reply` 在 `scene_first` 策略下优先调用 `compose_contextual_reply`；仅当返回 None 时才回退 `SceneReplyEngine`（`mock.generate_scene_reply`）。`impulse_regret` 场景两轮用户话均含冲动消费/自责关键词，mock 已有专属分支（`mock.py` 第 391–403 行），但 compose 缺失，导致生产路径与 mock 不一致。

参考既有改动（如 `fix-compose-self-doubt-reply`）：在 compose 中按关键词优先级插入分支，使用 `_pick` 确定性变体，与 mock 话术对齐。

## Goals / Non-Goals

**Goals:**

- `compose_contextual_reply` 命中冲动消费后悔（乱花钱/后悔）与自责（没用/管不住手）时返回共情接话
- 分支位于通用负面 open 兜底（`好烦`/`烦` 等）之前，避免问卷式「突然还是一阵子」
- 单测锁定 `impulse_regret` 两轮话术；全量 pytest + dialogue quality strict 保持绿

**Non-Goals:**

- 不改 mock.py 场景分支（已正确）
- 不改 evaluator 规则或新增场景
- 不扩展其他 compose 缺口（吵架和好/加班吐槽等留待后续 change）

## Decisions

1. **关键词与 mock 对齐**：检测 `乱花钱`、`管不住`、`没用`、`后悔`，且需同时含消费语境词（`钱`、`买`、`手`、`花`）以避免误伤；自责子分支额外检测 `没用`、`管不住手`。
2. **插入位置**：放在比较/自我怀疑分支之后、`好烦`/`烦` 短句分支之前，与 mock 优先级一致。
3. **话术风格**：compose 不含 `dear`/`mood` 前缀，保持 1～2 句口语、至多一个问句，禁止说教式理财建议。

## Risks / Trade-offs

- [compose 抢先命中导致与 mock 话术略有差异] → 单测断言关键词与共情标记，dialogue quality 全量回归
- [误伤其他含「后悔」的句子] → 与 mock 同规则（需消费语境词），已有场景全绿基线
