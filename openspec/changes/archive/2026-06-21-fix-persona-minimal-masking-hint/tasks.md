## 1. persona 语气侧重

- [x] 1.1 在 `persona.py` 新增 `masked_low` 语气侧重与 masking/evasive/「累」判定，优先于 `closed`
- [x] 1.2 补充 `test_persona.py`：`还好`、`不知道`、`累` 含 masking 侧重；`..` 仍为封闭边界

## 2. reply_guard 边界判定

- [x] 2.1 在 `reply_guard.py` 的 `user_is_closed()` 排除 masking/evasive/「累」
- [x] 2.2 补充 `test_reply_guard.py`：`还好`/`累` 不判 closed；`不想说` 仍判 closed

## 3. 验证

- [x] 3.1 `cd backend && python3 -m pytest --ignore=tests/test_dialogue_quality.py -q`
- [x] 3.2 `python3 scripts/run_dialogue_quality.py --strict`
- [x] 3.3 `python3 -m pytest tests/test_dialogue_quality.py -q`
- [x] 3.4 `cd .. && npx openspec validate --specs`
