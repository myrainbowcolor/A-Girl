## Why

对话质量评测 26 场景全绿，无 open `dialogue-quality` Issue。但生产路径 `scene_first` 优先调用 `compose_contextual_reply`，在 `short_reply_user` 场景用户单字说「累」时，compose 未命中任何分支（返回 None），mock 场景引擎则误走通用「不太好受」负面分支，未按 persona spec 的「极简 masking 低落 / 疲惫共情」给出短句体贴接话。与「还好」「不知道」等已有 compose 分支不一致，真实 LLM 路径下体验偏弱。

修复前 transcript 片段：
- 用户：累
- NPC：嗯……能感觉到你现在不太好受。不想说太多也没关系，我就在这儿陪着你。

## What Changes

- 在 `backend/app/dialogue_compose.py` 的 `compose_contextual_reply` 中，于封闭极简句分支之前增加单字「累」疲惫共情分支，短句接住、可轻问一句，禁止问卷连珠炮
- 在 `backend/app/llm/mock.py` 的 `_scene_reply` 极简回复段增加「累」分支（须在通用负面关键词分支之前），与 compose 行为对齐
- 补充 `test_dialogue_compose.py` 单测，覆盖 compose 对「累」的回复
- 不改 orchestrator 调度、安全策略、API 契约

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: 生产路径（dialogue_compose）与 mock 场景分支对单字「累」须返回疲惫共情短句，与「还好」「不知道」等极简 masking 口语同等优先级，禁止仅返回泛化「不太好受」套话

## Impact

- `backend/app/dialogue_compose.py` — 单字「累」疲惫共情分支
- `backend/app/llm/mock.py` — 场景极简「累」分支
- `backend/tests/test_dialogue_compose.py` — 新增测试
- 不影响 API 契约、安全策略、记忆检索、avatar、调度逻辑
