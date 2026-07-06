## Context

`orchestrator._generate_chat_reply` 在 `scene_first` 策略下优先调用 `compose_contextual_reply`；仅当返回 None 时才回退 `SceneReplyEngine`（`mock._scene_reply`）。`festival_lonely` 场景用户话「过年一个人，有点落寞」「看到别人团圆就更难受」含节日孤独关键词，mock 已有专属分支（`mock.py` 第 613–623 行），但 compose 缺失，回退 open 兜底会输出问卷式「突然还是一阵子」。

参考既有改动（如 `fix-compose-sick-care-reply`）：在 compose 中按关键词优先级插入分支，使用 `_pick` 确定性变体，与 mock 话术对齐；句首避免「嗯」以符合 `robotic_tone` 规则。

## Goals / Non-Goals

**Goals:**

- `compose_contextual_reply` 命中节日孤独/想家时返回陪伴式共情接话
- 分支位于通用负面 open 兜底之前，避免问卷式「突然还是一阵子」
- 单测锁定 `festival_lonely` 两轮话术；全量 pytest + dialogue quality strict 保持绿

**Non-Goals:**

- 不改 mock.py 场景分支（已正确）
- 不改 evaluator 规则或新增场景
- 不扩展其他 compose 缺口（怀旧童年/育儿焦虑/你不懂等留待后续 change）

## Decisions

1. **关键词与 mock 对齐**：`落寞`/`团圆`/`过年`/`一个人`；续聊子分支 `团圆`/`更难受`/`看到别人`
2. **插入位置**：放在生病关心分支之后、失眠/反刍分支之前；确保先于 `compose_open_reply` 负面池
3. **话术风格**：1～2 句口语、至多一个问句；先看见孤独感、陪伴倾听，禁止假热闹转移话题；句首不以「嗯」开头

## Risks / Trade-offs

- [「一个人」误伤其他语境] → 与 mock 一致，仅命中含节日/落寞/团圆标记的组合；单测 + dialogue quality 全量回归
- [与通用孤独分支重叠] → 节日分支在失眠孤独复合之前独立命中；「过年一个人」含落寞，优先节日分支
