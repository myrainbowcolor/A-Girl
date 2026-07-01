## Why

对话质量评测 26 场景全绿，无 open `dialogue-quality` Issue。但 `latest.json` transcript 显示多条 NPC 回复仍以「嗯」开头（如 `stranger_late_night_lonely`「嗯，睡不着又孤单…」、`short_reply_user`「嗯，听起来不糟…」、`long_distance_miss`「嗯，异地恋难的时候…」），与 persona spec 第 16 条「**禁止**以「嗯」「嗯嗯」开头」不符，听感偏敷衍、机械，削弱情感陪伴拟真度。

## What Changes

- 在 `reply_guard.polish_reply` 末段统一剥离/改写 NPC 回复句首「嗯」「嗯嗯」「嗯…」（保留动作描写前缀如「（安静了一会儿）」）
- 修正 `dialogue_compose.py` 中孤独失眠、masking「还好」、异地恋等高可见场景模板的句首「嗯」
- 修正 `safety.py` 未成年人边界话术句首「嗯…」为更自然的动作前缀
- `dialogue_quality/evaluator.py` 新增 major 规则：NPC 回复（去动作括号后）以「嗯」开头则记 `robotic_tone`
- 补充单元测试与对话质量场景断言

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: 口语化回复约束须在生产路径（compose + polish）可验证地禁止句首「嗯」

## Impact

- `backend/app/reply_guard.py` — 句首 filler 剥离
- `backend/app/dialogue_compose.py` — 高可见模板改写
- `backend/app/safety.py` — 边界话术
- `backend/app/dialogue_quality/evaluator.py` — 启发式规则
- `backend/tests/test_reply_guard.py`、`backend/tests/test_dialogue_quality.py` — 测试
- 不改 orchestrator 接口、安全策略逻辑、调度频率

## 成功标准

- `latest.json` 中上述场景 transcript 不再以「嗯」开头
- `python3 -m pytest` 全绿
- `run_dialogue_quality.py --strict` 26/26 通过
