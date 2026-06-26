## Context

`scene_first` 编排优先调用 `compose_contextual_reply`，未命中时走 `SceneReplyEngine`（mock.py `_scene_reply`）。`long_distance_miss` 场景 mock 已有「异地 / 挂掉电话 / 视频完 / 好空」分支（约第 432–442 行），但 compose 层缺失对应分支，导致 compose 返回 None 后虽能 fallback 到 mock，但 compose 优先路径无法直接产出异地恋共情话术。

## Goals / Non-Goals

**Goals:**

- 在 `compose_contextual_reply` 增加与 mock 对齐的异地恋想念分支
- 挂电话空落落、异地恋好难两类输入均有专属共情回复
- 补充 compose 单测，确保不落入「突然还是一阵子」类问卷套话

**Non-Goals:**

- 不改 mock.py 已有分支（已满足评测）
- 不改 orchestrator 路由顺序
- 不扩展新场景或 API

## Decisions

1. **关键词与 mock 对齐**：检测 `异地`、`挂掉电话`、`好空`、`视频完`；当同时含「异地」与「难」时走「异地恋不容易」模板，否则走「刚挂电话心里空」模板。
   - 理由：与 mock.py 第 432–442 行保持一致，降低双路径漂移风险。

2. **分支位置**：放在通用「空落落」分支之后、失眠分支之前，避免「好空」被泛化空落模板抢先误路由。
   - 理由：「挂掉电话好空」需更具体的异地恋语境接话，而非通用「没具体的事也会难受」。

3. **不引入 stage/dear 参数**：compose 层无 relationship stage，回复用中性亲密口语（不含「亲爱的」），与 compose 其他分支风格一致。
   - 理由：compose 函数签名不变，最小 diff。

## Risks / Trade-offs

- [「好空」误匹配其他语境] → 要求同时含「挂掉电话」「视频完」或「异地」之一，避免单独「好空」误触
- [与 mock 措辞不完全一致] → 单测断言关键词（空、异地、陪）而非逐字相同
