## Context

`scene_first` 编排优先调用 `compose_contextual_reply`。短句烦躁（「好烦」「有点烦」等，len≤10）当前命中 compose 专属分支，但模板含「是突然这样的，还是已经有一阵子了？」——与 persona spec 及 `GENERIC_SCENE_MARKERS` 所标识的问卷式兜底一致。mock `_scene_reply` 对含「烦」短句走通用低落共情，不叠「突然还是一阵子」。

## Goals / Non-Goals

**Goals:**

- compose 短句烦躁分支返回口语化共情，禁止「突然还是一阵子」类问卷套话
- mock `_empathy_reply` 陌生「烦」分支与 compose 对齐
- 保持每轮至多一个问句、句首不以「嗯」开头

**Non-Goals:**

- 不改分支优先级或新增场景
- 不改 sentiment/avatar 映射（另项优化）
- 不改 LLM system prompt

## Decisions

1. **替换 compose 模板池**：去掉含「突然」「一阵子」的选项，改为「心里挺堵…愿意说说是什么事最缠人」类轻问，与 mock 朋友/熟悉分支语气接近。
2. **同步 mock `_empathy_reply` 陌生分支**：去掉问卷句，改为「不想说原因也没关系，我在呢」+ 可选轻问。
3. **测试**：在现有 `test_compose_short_annoyance_no_um_prefix` 上增加 `assert "突然" not in out and "一阵子" not in out`。

## Risks / Trade-offs

- [轻问句仍可能被评作追问] → 仅用单句轻问，且与 mock 已有模式一致；dialogue quality 全量回归验证。
