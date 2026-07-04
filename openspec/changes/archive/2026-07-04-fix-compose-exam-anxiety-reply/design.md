## Context

`orchestrator._generate_chat_reply` 在 `scene_first` 策略下优先调用 `compose_contextual_reply`；仅当返回 None 时才回退 `SceneReplyEngine`（`mock._scene_reply`）。`acquainted_exam_anxiety` 场景用户话「下周就要高考了，我好紧张」「感觉什么都记不住」含高考/紧张/记不住关键词，mock 已有专属分支（`mock.py` 第 645–657 行），但 compose 缺失，回退 open 兜底会输出问卷式「突然还是一阵子」。

参考既有改动（如 `fix-compose-overtime-vent-reply`）：在 compose 中按关键词优先级插入分支，使用 `_pick` 确定性变体，与 mock 话术对齐。

## Goals / Non-Goals

**Goals:**

- `compose_contextual_reply` 命中考试/学业焦虑倾诉时返回共情接话
- 分支位于通用负面 open 兜底之前，避免问卷式「突然还是一阵子」
- 单测锁定 `acquainted_exam_anxiety` 两轮话术；全量 pytest + dialogue quality strict 保持绿

**Non-Goals:**

- 不改 mock.py 场景分支（已正确）
- 不改 evaluator 规则或新增场景
- 不扩展其他 compose 缺口（生病/分手/节日孤独/撑不住等留待后续 change）

## Decisions

1. **关键词与 mock 对齐**：检测 `紧张`/`焦虑`/`记不住`/`考不上`/`高考`/`考试`/`期末`/`考研`；排除含 `孩子`/`儿子`/`女儿`/`他`/`她` 的家长育儿语境。
2. **插入位置**：放在加班疲惫分支之后、失眠/孤独复合分支之前；确保先于 `compose_open_reply` 负面池（含「焦虑」关键词的问卷兜底）。
3. **续聊逻辑**：「记不住」单独命中；或近期用户话含考试/高考/紧张语境时第二轮「记不住」亦命中。
4. **话术风格**：compose 不含 `dear`/`mood` 前缀，保持 1～2 句口语、至多一个问句；先接住紧张，轻问复习节奏或压力来源，不说教。

## Risks / Trade-offs

- [compose 抢先命中导致与 mock 话术略有差异] → 单测断言关键词与共情标记，dialogue quality 全量回归
- [误伤含「紧张」但非考试的句子] → 要求同时含考试/学业标记（高考/考试/期末/考研/考不上/记不住），或与 prior 考试语境组合
