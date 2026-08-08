## Context

见 proposal.md — Why。生产路径 `compose_contextual_reply` 已对 ≤12 字「没劲 / 没意思 / 低落」返回低落共情；`mock.py` 的 emo 分支仅覆盖「emo / 丧 / 心累」，`_LOW` 含「没劲」却缺「没意思」，导致「没意思了」等短句 mock 空串。增量对齐既有短句低落模式（参考 archive `fix-compose-feeling-empty-hollowed-short`）。

## Goals / Non-Goals

**Goals:**

- mock 对「没意思」短句与 compose 同条件共情接住
- `_LOW` / `_user_tone` 识别「没意思」，避免中性空串
- 单测覆盖变体；既有没劲/emo/心累回归

**Non-Goals:**

- 不改 `safety.py`、危机词、avatar、proactivity 调度
- 不修「空虚 / 心塞 / 好空虚误走异地」等其它缺口（留给后续轮次）
- 不改 API / DB / 编排主路径结构

## Decisions

1. **扩展既有 emo/低落分支，而非新建独立分支**  
   将 mock 条件改为与 compose 一致：`emo|丧` 或 `心累|心好累` 或（≤12 且含 `没劲|没意思|低落`）。话术复用既有「这种低落的感觉我懂…」。  
   备选：单独「没意思」分支 — 冗余，拒绝。

2. **「没意思」加入 `_LOW` 与 `_user_tone` negative**  
   保证倾诉分类与场景分支一致；不把裸词写入危机表。

3. **不碰 compose**  
   compose 已通过；仅扩展测试变体回归。

## Risks / Trade-offs

- [误伤] 长句含「没意思」但非低落 → 以 ≤12 字门槛缓解，与 compose 一致  
- [回归] emo/心累/没劲话术被改坏 → 保留既有关键词与参数化回归测
