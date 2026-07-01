## 1. reply_guard 句首嗯剥离

- [x] 1.1 在 `reply_guard.py` 新增 `strip_npc_leading_um` 与 `reply_starts_with_um`，复用 `_FILLER_HEAD_RE`
- [x] 1.2 在 `polish_reply` 末段调用 `strip_npc_leading_um`（道歉句豁免）
- [x] 1.3 补充 `test_reply_guard.py` 单元测试

## 2. compose / safety 模板修正

- [x] 2.1 修正 `dialogue_compose.py` 孤独失眠、masking「还好」、异地恋模板句首「嗯」
- [x] 2.2 修正 `safety.py` 未成年人边界话术句首「嗯…」

## 3. 对话质量规则

- [x] 3.1 在 `evaluator.py` 新增句首「嗯」major `robotic_tone` 检查
- [x] 3.2 补充 `test_dialogue_quality.py` 或 evaluator 单测

## 4. 验证

- [x] 4.1 `cd backend && python3 -m pytest --ignore=tests/test_dialogue_quality.py -q`
- [x] 4.2 `python3 scripts/run_dialogue_quality.py --strict`
- [x] 4.3 `python3 -m pytest tests/test_dialogue_quality.py -q`
- [x] 4.4 `cd .. && npx openspec validate --specs`
