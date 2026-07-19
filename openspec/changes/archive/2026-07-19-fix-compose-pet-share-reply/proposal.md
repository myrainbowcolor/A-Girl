## Why

`memory_pet_name` 等场景第 1 轮用户分享养宠物（如「我养了一只叫橘子的猫，超粘人」）时，`mock.py` 会返回轻松亲昵的养宠接话，但生产路径 `compose_contextual_reply` 未覆盖该分支，返回 `None` 后落入 `compose_open_reply` 问卷式兜底（如「嗯，我在呢。你先随便丢几个词给我也行~」）。已有宠物捣蛋续聊（代词「它」）分支，但首轮分享仍是 compose/mock 行为缺口，削弱 scene_first 编排下的生活分享拟真感。

## What Changes

- 在 `dialogue_compose.py` 的 `compose_contextual_reply` 新增与 `mock.py` 对齐的养宠物首轮分享分支（含「猫」「狗」「宠物」，排除「记得」记忆追问）
- 猫语境返回亲昵接话并轻问日常习惯；狗/泛宠物返回毛孩子陪伴式接话；至多一个问句
- 分支置于宠物捣蛋续聊（代词「它」）之前、通用 open 兜底之前
- 补充 `test_dialogue_compose.py` 单测覆盖首轮养宠分享 compose 路径

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：口语化回复约束中补充养宠物首轮分享 compose 场景，与 mock 行为一致

## Impact

- `backend/app/dialogue_compose.py` — 新增 1 组场景分支
- `backend/tests/test_dialogue_compose.py` — 新增 compose 单测
- 不影响安全、危机干预、记忆主路径；不改 API 契约

## 成功标准

- `compose_contextual_reply("我养了一只叫橘子的猫，超粘人", …)` 返回含「猫」「粘人」或「撒娇」类接话，非 open 兜底
- `python3 -m pytest` 全绿；`run_dialogue_quality.py --strict` 26/26 通过
