## Context

`long_session_warmup` 场景末轮用户表达正向续聊意愿，陌生关系走 `mock.py` `_scene_reply` 中「还想继续聊」分支。当前陌生分支文案以「嗯嗯」开头并使用「欢迎随时来找我聊」，与 persona 口语化约束及 transcript 拟真目标不符。朋友/亲密分支已有自然表述，无需改动。

## Goals / Non-Goals

**Goals:**
- 仅调整陌生关系续聊 mock 模板一句，更口语、无客服腔
- 保持 `expect_warmth` 评测通过（含温暖标记）
- 补充单测锁定文案约束

**Non-Goals:**
- 不改 `dialogue_compose.py`（该路径无此分支，对话质量 runner 走 mock）
- 不改关系阶段判定、亲密度、调度或真实 LLM prompt
- 不调整朋友/亲密续聊已有话术

## Decisions

1. **只改 mock 陌生分支一行模板**  
   理由：问题仅出现在 `_scene_reply` 陌生 `return`；最小 diff、可回滚。

2. **新文案结构：肯定 + 邀约 + 同频**  
   示例：`好呀～明天想聊就来找我，能陪你说话我也很开心。`  
   替代「嗯嗯，欢迎随时来找我聊…」；保留「开心」满足 `_WARM_MARKERS`。

3. **不测 compose 路径**  
   `compose_contextual_reply` 无续聊分支，生产 `scene_first` 对该句会 fallback 到 mock，行为一致。

## Risks / Trade-offs

- [真实 LLM 路径仍可能生成客服腔] → 本 change 仅约束 mock 基线；真实模型靠 persona prompt 与人工抽检
- [过度亲昵] → 陌生分支仍不用「亲爱的」等称呼，与朋友分支区分

## Migration Plan

部署后即生效，无数据迁移。回滚：恢复 mock 原一行模板。

## Open Questions

（无）
