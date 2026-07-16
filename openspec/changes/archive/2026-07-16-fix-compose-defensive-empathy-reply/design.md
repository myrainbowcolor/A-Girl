## Context

`scene_first` 编排优先调用 `compose_contextual_reply`。`mock.py` 在 `_scene_reply` 有「你不懂/没人懂」防御心态与「不想说/不说了」封闭撤回分支，但 `dialogue_compose.py` 缺失对应逻辑，compose 返回 `None` 后走 scene_engine 或问卷式 open 兜底，共情弱于 mock 直出。

## Goals / Non-Goals

**Goals:**

- `compose_contextual_reply` 对防御心态（你不懂/没人懂）返回共情接话，不反驳、不讲道理
- 扩展封闭边界分支覆盖「不想说/不说了/算了」，与 mock 对齐
- `friend_defensive` 场景在 compose 路径下行为稳定

**Non-Goals:**

- 不改 mock 已有分支
- 不弱化真正封闭极简句（「嗯」「哦」）的边界逻辑
- 不改 avatar 映射或安全策略

## Decisions

1. **插入位置**：防御心态分支放在通用负面 open 兜底之前、失眠/异地等专项分支之后；封闭撤回扩展现有 `("不愿意", "不想聊", "别说了")` 为含「不想说」「不说了」「算了」。
2. **文案来源**：复用 mock 核心句式，用 `_pick` 做确定性变体，去除亲昵前缀（compose 无 `_endearment`）。
3. **至多一问**：防御心态可轻问「愿意多说一点吗」，封闭撤回禁止追问。

## Risks / Trade-offs

- [Risk] 「不懂」出现在学习语境（如「我不懂这道题」）误命中 → Mitigation：要求同时含「你不懂」「没人懂」或「不懂我」等防御口语标记
- [Risk] 「算了」在日常放弃语境误命中封闭分支 → Mitigation：与 mock 一致，仅在含「不想说/不说了/算了」组合时命中
