## Context

`scene_first` 编排下 `orchestrator` 优先调用 `compose_contextual_reply`；未命中时走 `SceneReplyEngine`，再 fallback 到 `compose_open_reply`。近期已补齐崩溃/绝望/烦躁短句缺口，但没劲/没意思、心里堵/堵心、短句慌张/担心仍未覆盖，导致部分短句落入「好，我收到了。不用一次说完~」类问卷兜底。

参考 `docs/ARCHITECTURE.md` 中 scene_first 分层：`dialogue_compose` 为无 LLM 的上下文拼装层，应与 `llm/mock.py` 的 `_LOW`/`_VENT` 关键词对齐。

## Goals / Non-Goals

**Goals:**

- 扩展 `dialogue_compose.py` emo/低落分支，覆盖没劲/没意思/低落短句
- 新增心里堵/堵心/堵得慌短句分支（与「烦」分支语义接近）
- 新增短句慌张/担心分支（慌/害怕/担心，len≤10，排除育儿语境）
- 补充 compose 探针单测

**Non-Goals:**

- 不改 `safety.py`、危机干预、记忆检索
- 不改主动消息调度频率
- 不新增 dialogue_quality 场景（基线已全绿，以 compose 单测保障）

## Decisions

1. **没劲并入 emo/低落分支**：与 mock `_LOW = ("低落", "没劲", "丧", "emo", "心累")` 对齐，扩展既有 emo 分支关键词。
2. **堵心单独短句分支**：`len(text) <= 10` 且含堵/堵心/堵得慌/心里堵，复用烦躁类共情模板池。
3. **慌张/担心短句分支**：`len(text) <= 10` 且含慌/害怕/担心/好怕，须在育儿焦虑分支之后、通用 open 兜底之前；育儿语境（含孩子/耽误等）已由既有分支处理。

## Risks / Trade-offs

- [关键词过宽误命中] → 堵心/慌张分支限制 `len(text) <= 10`；育儿「害怕耽误」仍走育儿分支
- [与考试焦虑分支冲突] → 「好焦虑」「紧张」已由考试分支处理；单字「慌」不含考试关键词，无冲突
