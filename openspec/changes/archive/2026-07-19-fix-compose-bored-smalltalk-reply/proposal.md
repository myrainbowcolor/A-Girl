## Why

`bored_smalltalk` 场景第 1 轮用户说「好无聊啊」时，`mock.py` 会返回轻松闲聊接话，但生产路径 `compose_contextual_reply` 未覆盖该分支，返回 `None` 后落入 `compose_open_reply` 问卷式兜底（如「嗯，我在呢。你先随便丢几个词给我也行~」）。此前已补齐「无聊上文 + 极简嗯」与「你在干嘛」探问分支，首轮无聊口语仍是 compose/mock 行为缺口，削弱 scene_first 编排下的拟真陪伴感。

## What Changes

- 在 `dialogue_compose.py` 的 `compose_contextual_reply` 新增与 `mock.py` 对齐的无聊闲聊首轮分支（含「无聊」「没事干」「好闲」）
- 朋友/亲密关系返回亲昵续聊，陌生/熟悉关系返回轻松接话；至多一个问句，禁止句首「嗯」
- 分支置于通用 open 兜底之前
- 补充 `test_dialogue_compose.py` 单测覆盖 `bored_smalltalk` 第 1 轮 compose 路径

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：口语化回复约束中补充无聊闲聊首轮 compose 场景，与 mock 行为一致

## Impact

- `backend/app/dialogue_compose.py` — 新增 1 组场景分支
- `backend/tests/test_dialogue_compose.py` — 新增 compose 单测
- 不影响安全、危机干预、记忆主路径；不改 API 契约

## 成功标准

- `compose_contextual_reply("好无聊啊", …)` 返回含「无聊」「唠」或「聊」类轻松接话，非 open 兜底
- `python3 -m pytest` 全绿；`run_dialogue_quality.py --strict` 26/26 通过
