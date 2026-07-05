## Context

`orchestrator._generate_chat_reply` 在 `scene_first` 策略下优先调用 `compose_contextual_reply`；仅当返回 None 时才回退 `SceneReplyEngine`（`mock._scene_reply`）。`friend_breakup_sad` 场景用户话「我们分手了」「我还是忍不住想哭」「你觉得我还能好起来吗」含分手/想哭/好起来关键词，mock 已有专属分支（`mock.py` 第 509–519、707–712、875–881 行），但 compose 缺失，回退 open 兜底会输出问卷式「突然还是一阵子」。

参考既有改动（如 `fix-compose-exam-anxiety-reply`）：在 compose 中按关键词优先级插入分支，使用 `_pick` 确定性变体，与 mock 话术对齐。

## Goals / Non-Goals

**Goals:**

- `compose_contextual_reply` 命中失恋/分手倾诉时返回共情接话
- 分支位于通用负面 open 兜底之前，避免问卷式「突然还是一阵子」
- 单测锁定 `friend_breakup_sad` 三轮话术；全量 pytest + dialogue quality strict 保持绿

**Non-Goals:**

- 不改 mock.py 场景分支（已正确）
- 不改 evaluator 规则或新增场景
- 不扩展其他 compose 缺口（生病/节日孤独/撑不住等留待后续 change）

## Decisions

1. **关键词与 mock 对齐**：
   - 首轮：`分手`/`失恋`/`分开了`
   - 续聊哭：`想哭`/`哭了`/`忍不住哭` 且近期用户话含分手语境
   - 续聊希望：`好起来`/`会好` 且含 `?` 或 `吗`
2. **插入位置**：放在考试焦虑分支之后、失眠/孤独复合分支之前；确保先于 `compose_open_reply` 负面池。
3. **话术风格**：compose 不含 `dear`/`mood` 前缀，保持 1～2 句口语、至多一个问句；先接住悲伤，陪伴倾听，不急于给建议。

## Risks / Trade-offs

- [compose 抢先命中导致与 mock 话术略有差异] → 单测断言关键词与共情标记，dialogue quality 全量回归
- [「好起来」误伤非分手语境] → 要求含 `?` 或 `吗`，与 mock 第 707–712 行一致
