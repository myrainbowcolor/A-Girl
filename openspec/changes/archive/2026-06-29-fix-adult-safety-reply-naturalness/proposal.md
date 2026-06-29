## Why

`minor_boundary` 场景 transcript 显示，未成年人恋爱越界拦截话术 `_ADULT_RESPONSE` 在明确拒绝后连续抛出两个问句（「今天过得怎么样呀？有什么开心或烦恼的事想跟我讲吗？」），像访谈问卷而非真人微信聊天，与项目「每轮最多一个问句」的口语化约束不一致。安全边界本身正确，但接话方式可更自然，避免削弱陪伴感。

## What Changes

- 将 `backend/app/safety.py` 中 `_ADULT_RESPONSE` 改为 1～2 句口语化拒绝 + **至多一个**轻问句，引导到合适话题
- 保持拒绝恋人角色、不进入正常 LLM 生成的安全行为不变
- 补充 `test_safety.py` 断言：成人越界话术全句问号 ≤ 1
- 可选：在 `minor_boundary` 场景期望中强化「非问卷式」检查（若 evaluator 已有通用规则则依赖现有检查）

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `safety`: 未成年人恋爱越界拦截话术须口语化、全句至多一个问句

## Impact

- `backend/app/safety.py` — `_ADULT_RESPONSE` 文案
- `backend/tests/test_safety.py` — 新增/更新断言
- 不影响危机干预、暴力/隐私拦截逻辑及 `minor_guard_prompt`
