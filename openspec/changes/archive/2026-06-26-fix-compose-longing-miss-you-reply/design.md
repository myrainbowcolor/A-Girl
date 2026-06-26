## Context

`scene_first` 编排优先调用 `compose_contextual_reply`，未命中时走 `SceneReplyEngine`（mock.py `_scene_reply`）。`close_miss_you` 场景 mock 已有「想念 / 好久未见」分支（约第 572–584 行），但 compose 层缺失对应分支，导致 compose 返回 None 后虽能 fallback 到 mock，但 compose 优先路径无法直接产出依恋共情话术。

## Goals / Non-Goals

**Goals:**

- 在 `compose_contextual_reply` 增加与 mock 对齐的想念/好久未见分支
- 分支须在「哈哈」报喜之前，避免「想你」误命中开心分享
- 补充 compose 单测，确保回复含「想」类依恋表述，不含「开心起来了」报喜套话

**Non-Goals:**

- 不改 mock.py 已有分支（已满足评测）
- 不改 orchestrator 路由顺序
- 不扩展新场景或 API

## Decisions

1. **关键词与 mock 对齐**：检测 `想你`、`想念`、`好久不见`、`好久没聊`、`好想你`。
   - 理由：与 mock.py 第 572–584 行保持一致，降低双路径漂移风险。

2. **分支位置**：放在「哈哈」报喜分支之前（宠物捣蛋之后），避免「想你」被 `is_positive_utterance` 类报喜逻辑抢先。
   - 理由：与 mock 分支顺序一致，修复历史误路由根因。

3. **亲密程度推断**：compose 无 relationship stage，用 `prior_assistant` 含「亲爱的」「宝贝」「抱抱」判定亲密语气；否则走朋友/熟悉语气。
   - 理由：与 compose 倚靠分支（第 190–206 行）风格一致，最小 diff。

## Risks / Trade-offs

- [「想你」出现在其他语境] → 关键词整句匹配常见依恋口语，与 mock 一致
- [与 mock 措辞不完全一致] → 单测断言关键词（想、好久、陪）而非逐字相同
