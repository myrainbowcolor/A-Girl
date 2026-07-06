## Context

`orchestrator._generate_chat_reply` 在 `scene_first` 策略下优先调用 `compose_contextual_reply`；仅当返回 None 时才回退 `SceneReplyEngine`（`mock._scene_reply`）。`parent_anxiety` 场景用户话「孩子这次考得不好，我是不是太严厉了」「我很怕耽误他」含育儿焦虑关键词，mock 已有专属分支（`mock.py` 第 659–669 行），但 compose 缺失，回退 open 兜底会输出问卷式「突然还是一阵子」。

参考既有改动（如 `fix-compose-festival-lonely-reply`）：在 compose 中按关键词优先级插入分支，使用 `_pick` 确定性变体，与 mock 话术对齐；句首避免「嗯」以符合 `robotic_tone` 规则。考试焦虑分支已排除含「孩子」的语境，育儿分支须独立命中。

## Goals / Non-Goals

**Goals:**

- `compose_contextual_reply` 命中家长育儿焦虑时返回陪伴式共情接话
- 分支位于通用负面 open 兜底之前，避免问卷式「突然还是一阵子」
- 单测锁定 `parent_anxiety` 两轮话术；全量 pytest + dialogue quality strict 保持绿

**Non-Goals:**

- 不改 mock.py 场景分支（已正确）
- 不改 evaluator 规则或新增场景
- 不扩展其他 compose 缺口（怀旧童年/你不懂/开心分享等留待后续 change）

## Decisions

1. **关键词与 mock 对齐**：`孩子`/`儿子`/`女儿`/`太严厉`/`耽误`/`考不好`；续聊子分支 `耽误`/`害怕`/`怕`
2. **插入位置**：放在考试焦虑分支之后、失恋分手分支之前（或生病分支附近）；确保先于 `compose_open_reply` 负面池
3. **话术风格**：1～2 句口语、至多一个问句；先理解家长自责与担心，禁止简单说「别担心」；句首不以「嗯」开头

## Risks / Trade-offs

- [「孩子」误伤非育儿语境] → 与 mock 一致，需同时命中育儿焦虑标记（严厉/耽误/考不好等）；单测 + dialogue quality 全量回归
- [与考试焦虑分支重叠] → 考试分支已排除含「孩子」的文本；育儿分支独立命中
