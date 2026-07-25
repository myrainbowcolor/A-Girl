## Context

`scene_first` 编排下 `orchestrator` 优先调用 `compose_contextual_reply`；未命中时走 `SceneReplyEngine`，再 fallback 到 `compose_open_reply`。近期已补齐崩溃/难受/郁闷短句缺口，但绝望/迷茫/破防/憋屈/心痛等网络口语及单字「烦」仍未覆盖，导致部分短句落入「好，我收到了。不用一次说完~」类问卷兜底。

参考 `docs/ARCHITECTURE.md` 中 scene_first 分层：`dialogue_compose` 为无 LLM 的上下文拼装层，应与 `llm/mock.py` 通用负面情绪关键词对齐。

## Goals / Non-Goals

**Goals:**

- 扩展 `dialogue_compose.py` 短句低落分支关键词，覆盖绝望/迷茫/破防等口语
- 单字「烦」「烦啊」命中烦躁短句分支
- 「绷不住」并入既有倦怠极限分支（与「撑不住」并列）
- 补充 compose 探针单测

**Non-Goals:**

- 不改 `safety.py`、危机干预、记忆检索
- 不改主动消息调度频率
- 不新增 dialogue_quality 场景（基线已全绿，以 compose 单测保障）

## Decisions

1. **关键词并入既有短句低落分支**：与崩溃/难受/郁闷同一 `_pick` 模板池，最小 diff，避免新增独立分支逻辑。
2. **单字「烦」单独判断**：在现有 `("有点烦", "挺烦", "好烦", "烦死了") and len<=10` 之后追加 `text in ("烦", "烦啊") or (len(text)<=4 and "烦" in text)`，避免长句误命中。
3. **「绷不住」扩展撑不住分支**：与 mock 中负面情绪关键词「憋着」语义接近，用户表达情绪崩溃边缘。

## Risks / Trade-offs

- [关键词过宽误命中] → 限制 `len(text) <= 12` 于短句低落分支；「烦」分支额外限制字数
- [与考试焦虑「焦虑」分支冲突] → 「好焦虑」已由考试分支处理；「迷茫」不含考试语境，无冲突
