## Context

`orchestrator._generate_chat_reply` 在 `scene_first` 策略下优先调用 `compose_contextual_reply`；仅当返回 None 时才回退 `SceneReplyEngine`（`mock._scene_reply`）。`nostalgic_childhood` 场景用户话「突然想到小时候外婆做的汤圆，好怀念」「那时候日子简单，现在好难静下来」含怀旧关键词，mock 已有专属分支（`mock.py` 第 298–315 行），但 compose 缺失，回退 open 兜底会输出问卷式「突然还是一阵子」。

参考既有改动（如 `fix-compose-festival-lonely-reply`）：在 compose 中按关键词优先级插入分支，使用 `_pick` 确定性变体，与 mock 话术对齐；句首避免「嗯」以符合 `robotic_tone` 规则。

## Goals / Non-Goals

**Goals:**

- `compose_contextual_reply` 命中怀旧/童年时返回柔软共鸣接话
- 分支位于通用负面 open 兜底之前，避免问卷式「突然还是一阵子」
- 单测锁定 `nostalgic_childhood` 两轮话术；全量 pytest + dialogue quality strict 保持绿

**Non-Goals:**

- 不改 mock.py 场景分支（已正确）
- 不改 evaluator 规则或新增场景
- 不扩展其他 compose 缺口

## Decisions

1. **关键词与 mock 对齐**：`怀念`/`小时候`/`外婆`/`童年`/`汤圆`；续聊子分支 `简单`/`静下来`/`现在好难` + 上文含怀旧标记
2. **插入位置**：放在早安寒暄分支之后、工作话题分支之前；确保先于 `compose_open_reply` 负面池
3. **话术风格**：1～2 句口语、至多一个问句；顺着回忆共鸣，不急着拉回现实；句首不以「嗯」开头

## Risks / Trade-offs

- [「好难」误伤其他负面语境] → 续聊子分支要求 prior_users 含怀旧标记，与 mock 一致；单测 + dialogue quality 全量回归
- [与通用低落分支重叠] → 怀旧分支在通用负面 open 之前独立命中；含「怀念」等标记优先怀旧分支
