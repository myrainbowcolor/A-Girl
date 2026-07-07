## Context

`orchestrator` 默认 `scene_first` 策略优先调用 `compose_contextual_reply`；未命中时降级 `compose_open_reply` 或 LLM。`2026-06-30-fix-stranger-continue-chat-reply` 已在 `mock.py` 修复陌生关系「还想继续聊」分支，但 `dialogue_compose.py` 未同步，导致生产路径对 `long_session_warmup` 末轮「明天还想来找你聊聊」返回 `None`，最终落入问卷式 open 兜底。

架构参考 `docs/ARCHITECTURE.md`：对话生成链路为 orchestrator → compose/scene → LLM fallback，compose 与 mock 场景分支应保持行为一致。

## Goals / Non-Goals

**Goals:**

- 在 `dialogue_compose.py` 增加「还想/明天/下次继续聊」分支，文案与 `mock.py` 对齐
- 通过 `test_dialogue_compose.py` 覆盖陌生/朋友续聊 compose 路径
- 保持 dialogue quality 26/26 全绿

**Non-Goals:**

- 不改 mock 已有分支（已修复）
- 不改 orchestrator 策略、关系阶段判定逻辑
- 不改 avatar、proactivity、安全策略

## Decisions

1. **分支位置**：放在 `compose_contextual_reply` 正向分享（「哈哈」）之前、想念分支之后，与 mock 优先级一致（正向延续，非负面 open 兜底）。
2. **关系判定**：复用现有 `prior_assistant` 亲密标记（「亲爱的」「宝贝」「抱抱」）区分朋友/亲密 vs 陌生；无亲密标记时走陌生口语化模板。
3. **文案来源**：直接复用 mock 已验证文案（`好呀～明天想聊就来找我，能陪你说话我也很开心。` 等），确保 compose/mock 一致。

## Risks / Trade-offs

- [误判其他含「明天」的负面句] → 关键词组合要求同时含「聊/找/来」，与 mock 一致，风险低
- [compose 与 mock 再次漂移] → spec 明确要求两者行为一致，并补充 compose 单测

## Migration Plan

纯代码增量，无 DB/API 变更；合并后 `scene_first` 路径自动生效，可回滚单文件改动。

## Open Questions

（无）
