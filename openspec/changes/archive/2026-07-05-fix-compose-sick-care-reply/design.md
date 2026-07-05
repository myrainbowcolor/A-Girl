## Context

`orchestrator._generate_chat_reply` 在 `scene_first` 策略下优先调用 `compose_contextual_reply`；仅当返回 None 时才回退 `SceneReplyEngine`（`mock._scene_reply`）。`acquainted_sick_care` 场景用户话「我感冒了，头好痛」含感冒/头痛关键词，mock 已有专属分支（`mock.py` 第 671–691 行），但 compose 缺失，回退 open 兜底会输出问卷式「突然还是一阵子」。

参考既有改动（如 `fix-compose-breakup-sad-reply`）：在 compose 中按关键词优先级插入分支，使用 `_pick` 确定性变体，与 mock 话术对齐。

## Goals / Non-Goals

**Goals:**

- `compose_contextual_reply` 命中生病/身体不适时返回关心接话
- 分支位于通用负面 open 兜底之前，避免问卷式「突然还是一阵子」
- 单测锁定 `acquainted_sick_care` 话术；全量 pytest + dialogue quality strict 保持绿

**Non-Goals:**

- 不改 mock.py 场景分支（已正确）
- 不改 evaluator 规则或新增场景
- 不扩展其他 compose 缺口（节日孤独/撑不住/你不懂等留待后续 change）

## Decisions

1. **关键词与 mock 对齐**：`感冒`/`发烧`/`生病`/`头痛`/`头疼`/`不舒服`
2. **插入位置**：放在失恋分手分支之后、失眠/孤独复合分支之前；确保先于 `compose_open_reply` 负面池
3. **语气分层**：compose 无 relationship stage，用 `prior_assistant` 含「亲爱的」「宝贝」「抱抱」判定亲密语气，否则用熟悉/朋友式关心（与 mock familiar 话术对齐）
4. **话术风格**：1～2 句口语、至多一个问句；先表达关心与陪伴，轻问哪里最难受

## Risks / Trade-offs

- [compose 无 stage 导致语气与 mock 略有差异] → 单测断言关键词与共情标记，dialogue quality 全量回归
- [「不舒服」误伤非生病语境] → 与 mock 一致，仅命中明确身体不适表述
